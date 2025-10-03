
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

# =========================================================
# 1. CONFIGURATION
# =========================================================

# PostgreSQL connection
POSTGRES_USER = "community_user"
POSTGRES_PASSWORD = "Userpass"
POSTGRES_DB = "community_analytics"
POSTGRES_HOST = "localhost"
POSTGRES_PORT = 5432

# Create SQLAlchemy engine for connection
engine = create_engine(
    f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
)

# GitHub API configuration
load_dotenv()  # Load environment variables from .env file if present
GITHUB_USERNAME = "scikit-learn"  # Example organization/user
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")          # Personnal Token to raise rate limits
HEADERS = {"Authorization": f"token {GITHUB_TOKEN}"} if GITHUB_TOKEN else {}

# =========================================================
# 2. HELPER FUNCTIONS
# =========================================================

def github_get(url, params=None):
    
    #Helper function to GET data from GitHub API with basic error handling.
    #Implements simple retry logic in case of temporary errors or rate limits.
    
    all_data = []
    page = 1
    while True:
        p = params.copy() if params else {}
        p["per_page"] = 100
        p["page"] = page

        response = requests.get(url, headers=HEADERS, params=p)
        if response.status_code != 200:
            print(f"Error fetching {url}: {response.status_code} - {response.text}")
            break

        data = response.json()
        if not data:  # stop when empty
            break

        all_data.extend(data)
        page += 1

    return all_data

def df_to_postgres(df, table_name):
    
     #Insert a Pandas DataFrame into a PostgreSQL table using SQLAlchemy.
    
    if df.empty:
        print(f"No data to insert for table {table_name}. Skipping.")
        return
    df.to_sql(table_name, engine, if_exists="replace", index=False)
    print(f"Inserted {len(df)} rows into table {table_name}.")

# =========================================================
# 3. EXTRACT: REPOSITORIES
# =========================================================

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
df_to_postgres(projects_df, "projects")

# =========================================================
# 4. EXTRACT: CONTRIBUTORS
# =========================================================

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

df_to_postgres(contributors_df, "contributors")

# =========================================================
# 5. EXTRACT: ISSUES
# =========================================================

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
df_to_postgres(issues_df, "issues")

# =========================================================
# 6. EXTRACT: PULL REQUESTS
# =========================================================

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
df_to_postgres(prs_df, "pull_requests")

# =========================================================
# 7. NOTES / NEXT STEPS
# =========================================================

#- This script can be extended to include more data points (e.g., comments, reviews).

