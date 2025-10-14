
#etl_github.py
#--------------
#ETL script for Open Source Community Analytics project.

#This script demonstrates:
#- Extraction of data from GitHub API (repositories, contributors, issues, pull requests)
#- Transformation of data to match PostgreSQL schema
#- Loading data into PostgreSQL database
#- Basic error handling and logging


import requests
import pandas as pd
from sqlalchemy import create_engine
import time
import os
from dotenv import load_dotenv
from urllib.parse import quote_plus
from datetime import datetime

#configurations

# PostgreSQL connection
load_dotenv()

POSTGRES_USER = os.getenv("POSTGRES_USER", "community_user")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "Userpass")
POSTGRES_DB = os.getenv("POSTGRES_DB", "community_analytics")
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "postgres")
POSTGRES_PORT = int(os.getenv("POSTGRES_PORT", 5432))

# Create SQLAlchemy engine for connection

# Encode password safely 
encoded_user = quote_plus(POSTGRES_USER)
encoded_password = quote_plus(POSTGRES_PASSWORD)
#print(f"Encoded user: {encoded_user}, Encoded password: {encoded_password}")
#for c in POSTGRES_USER + POSTGRES_PASSWORD + POSTGRES_DB:
    #print(ord(c), c)


# Create SQLAlchemy engine
engine = create_engine(
    f"postgresql+psycopg2://{encoded_user}:{encoded_password}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}",
    client_encoding="utf8"  # Assure que psycopg2 communique en UTF-8
)

# GitHub API configuration
load_dotenv()  # Load environment variables from .env file if present
GITHUB_USERNAME = "scikit-learn"  
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")          # Personnal Token to raise rate limits
HEADERS = {"Authorization": f"token {GITHUB_TOKEN}"} if GITHUB_TOKEN else {}

#Extraction functions

def github_get(url, params=None, max_retries=5):
    
    #Helper function to GET data from GitHub API with basic error handling.
    #Implements simple retry logic in case of temporary errors or rate limits.
    
    all_data = []
    page = 1
    retries = 0
    while True:
        p = params.copy() if params else {}
        p["per_page"] = 100
        p["page"] = page

        response = requests.get(url, headers=HEADERS, params=p)

        # Rate limit exceeded
        if response.status_code == 403 and "X-RateLimit-Remaining" in response.headers:
            reset_time = int(response.headers.get("X-RateLimit-Reset", time.time() + 60))
            sleep_time = max(reset_time - int(time.time()), 1)
            print(f"Rate limit exceeded. Sleeping for {sleep_time} seconds...")
            time.sleep(sleep_time)
            continue

        if response.status_code != 200:
            print(f"Error fetching {url}: {response.status_code} - {response.text}")
            retries += 1
            if retries >= max_retries:
                break
            print(f"Retrying ({retries}/{max_retries}) in 10 seconds...")
            time.sleep(10)
            continue

        data = response.json()
        if not data:
            break

        all_data.extend(data)
        page += 1

    return all_data

def df_to_postgres(df, table_name):
    
     #Insert a Pandas DataFrame into a PostgreSQL table using SQLAlchemy.
    
    if df.empty:
        print(f"No data to insert for table {table_name}. Skipping.")
        return
    df.to_sql(table_name, engine, if_exists="append", index=False)
    print(f"Inserted {len(df)} rows into table {table_name}.")

#Extract Projects

repos_url = f"https://api.github.com/users/{GITHUB_USERNAME}/repos"
repos_data = github_get(repos_url)


# Transform repositories data
projects_df = pd.DataFrame(repos_data)
if not projects_df.empty:
    # Select relevant columns and rename for consistency
    projects_df = projects_df[["id", "name", "description", "created_at", "updated_at"]].copy()
    # Rename 'id' to 'project_id' for clarity
    projects_df.rename(columns={"id": "project_id"}, inplace=True)

# Load into PostgreSQL
df_to_postgres(projects_df, "projects_raw")

#Excract Contributors

contributors_list = []

for repo in repos_data:
    repo_name = repo["name"]
    contrib_url = repo["contributors_url"]
    contributors = github_get(contrib_url)
    for c in contributors:
        contributors_list.append({
            "login": c["login"],
            "github_id": c["id"]
        })

contributors_df = pd.DataFrame(contributors_list)
if not contributors_df.empty:
    contributors_df.drop_duplicates(subset=["github_id"], inplace=True)

df_to_postgres(contributors_df, "contributors_raw")

#Extract Issues

issues_list = []

for repo in repos_data:
    repo_name = repo["name"]
    issues_url = f"https://api.github.com/repos/{GITHUB_USERNAME}/{repo_name}/issues?state=all&per_page=100"
    issues = github_get(issues_url)
    # Filter out pull requests (issues and PRs are returned together)
    issues_only = [i for i in issues if "pull_request" not in i]
    for issue in issues_only:
        issues_list.append({
            "project_id": repo["id"],
            "title": issue.get("title"),
            "body": issue.get("body"),
            "state": issue.get("state"),
            "created_at": issue.get("created_at"),
            "updated_at": issue.get("updated_at")
        })

issues_df = pd.DataFrame(issues_list)
df_to_postgres(issues_df, "issues_raw")

#Extract Pull Requests

prs_list = []

for repo in repos_data:
    repo_name = repo["name"]
    prs_url = f"https://api.github.com/repos/{GITHUB_USERNAME}/{repo_name}/pulls?state=all&per_page=100"
    prs = github_get(prs_url)
    for pr in prs:
        prs_list.append({
            "project_id": repo["id"],
            "contributor_id": None,  # will map later based on contributor login
            "title": pr.get("title"),
            "body": pr.get("body"),
            "state": pr.get("state"),
            "created_at": pr.get("created_at"),
            "updated_at": pr.get("updated_at")
        })

prs_df = pd.DataFrame(prs_list)
df_to_postgres(prs_df, "pull_requestsraw")

#end of extraction process

#Transformation and loading process

# core functions to load and write tables

def load_table(table_name):
    """Read a table from PostgreSQL into a pandas DataFrame."""
    query = f"SELECT * FROM {table_name};"
    return pd.read_sql(query, engine)

def write_table(df, table_name):
    if df.empty:
        print(f"No data to insert for {table_name}")
        return
    df.to_sql(table_name, engine, if_exists="append", index=False)
    print(f"{len(df)} rows inserted into {table_name}")

# project table transformations

projects_raw = load_table("projects_raw")

if not projects_raw.empty:
    projects_clean = projects_raw.copy()
    projects_clean["name_clean"] = projects_clean["name"].str.lower().str.strip()

    # Simple activity level classification (based on update recency)
    now = pd.Timestamp.now()
    projects_clean["activity_level"] = projects_clean["updated_at"].apply(
        lambda d: "active" if (now - pd.to_datetime(d)).days < 180 else "stale"
    )

    projects_clean["transformed_at"] = datetime.now()
    write_table(projects_clean, "projects_clean")

# contributors table transformations

contributors_raw = load_table("contributors_raw")

if not contributors_raw.empty:
    contributors_clean = contributors_raw.copy()
    contributors_clean["login_clean"] = contributors_clean["login"].str.lower().str.strip()
    contributors_clean["activity_score"] = 1.0  # Placeholder: can compute later
    contributors_clean["transformed_at"] = datetime.now()
    write_table(contributors_clean, "contributors_clean")

#issues table transformations

issues_raw = load_table("issues_raw")

if not issues_raw.empty:
    issues_clean = issues_raw.copy()
    issues_clean["title_clean"] = issues_clean["title"].str.lower().str.strip()
    issues_clean["word_count"] = issues_clean["body"].fillna("").apply(lambda x: len(x.split()))
    issues_clean["is_closed"] = issues_clean["state"].apply(lambda s: s.lower() == "closed")
    issues_clean["transformed_at"] = datetime.now()
    write_table(issues_clean, "issues_clean")

#pull requests table transformations

pulls_raw = load_table("pull_requests_raw")

if not pulls_raw.empty:
    pulls_clean = pulls_raw.copy()
    pulls_clean["title_clean"] = pulls_clean["title"].str.lower().str.strip()
    pulls_clean["is_merged"] = pulls_clean["state"].apply(lambda s: s.lower() == "merged")
    pulls_clean["transformed_at"] = datetime.now()
    write_table(pulls_clean, "pull_requests_clean")

#end of transformation process

print("Transformation pipeline completed successfully.")



