# dashboard_app.py
# ---------------------------------------------------------
# Streamlit dashboard for GitHub Community Analytics
# Connects to PostgreSQL (clean schema) and visualizes KPIs
# ---------------------------------------------------------

import streamlit as st
import pandas as pd
from sqlalchemy import create_engine

# ---------------------------------------------------------
# 1. Configuration & Connection
# ---------------------------------------------------------

POSTGRES_USER = "community_user"
POSTGRES_PASSWORD = "Userpass"
POSTGRES_DB = "community_analytics"
POSTGRES_HOST = "postgres"
POSTGRES_PORT = "5432"

# Create SQLAlchemy connection
engine = create_engine(
    f"postgresql+psycopg2://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
)

st.set_page_config(page_title="GitHub Community Dashboard", layout="wide")

# ---------------------------------------------------------
# 2. Load data
# ---------------------------------------------------------
@st.cache_data
def load_data():
    projects = pd.read_sql("SELECT * FROM projects_clean", engine)
    contributors = pd.read_sql("SELECT * FROM contributors_clean", engine)
    issues = pd.read_sql("SELECT * FROM issues_clean", engine)
    prs = pd.read_sql("SELECT * FROM pull_requests_clean", engine)
    return projects, contributors, issues, prs

try:
    projects, contributors, issues, prs = load_data()
except Exception as e:
    st.error(f"Database connection failed: {e}")
    st.stop()

# ---------------------------------------------------------
# 3. KPIs
# ---------------------------------------------------------
st.title("GitHub Community Analytics Dashboard")

col1, col2, col3, col4 = st.columns(4)
col1.metric("Projects", len(projects))
col2.metric("Contributors", len(contributors))
col3.metric("Open Issues", len(issues[issues["state"] == "open"]))
col4.metric("Pull Requests", len(prs))

st.markdown("---")

# ---------------------------------------------------------
# 4. Visualizations
# ---------------------------------------------------------
st.header("Activity Overview")

issues["created_at"] = pd.to_datetime(issues["created_at"])
prs["created_at"] = pd.to_datetime(prs["created_at"])

# Issues over time
issues_by_month = issues.groupby(issues["created_at"].dt.to_period("M")).size().reset_index(name="count")
issues_by_month["created_at"] = issues_by_month["created_at"].astype(str)
st.subheader("Issues created over time")
st.line_chart(issues_by_month.set_index("created_at"))

# Pull requests by project
st.subheader("Pull Requests by Project")
prs_by_project = prs.groupby("project_id").size().reset_index(name="count")
prs_by_project = prs_by_project.merge(projects[["project_id", "name"]], on="project_id", how="left")
st.bar_chart(prs_by_project.set_index("name")["count"])

# ---------------------------------------------------------
# 5. Contributors table
# ---------------------------------------------------------
st.header("Top Contributors")
st.dataframe(contributors.head(20))
