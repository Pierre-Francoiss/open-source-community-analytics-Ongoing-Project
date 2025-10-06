# open-source-community-analytics-Ongoing-Project
This project aims to analyze open-source software communities by collecting and processing data from the GitHub API. The focus is on understanding activity patterns, collaboration dynamics, and contributor interactions in large-scale projects such as PyTorch and TensorFlow.

The project is designed as a complete data engineering workflow: ingestion, storage, modeling, transformation, and analysis. The end goal is to provide meaningful insights into how open-source communities function and evolve over time.

# Objectives
-Collect issues, pull requests, comments, and contributor data from GitHub.\
-Store raw and processed data in a PostgreSQL database.\
-Transform and model the data into a clean relational structure.\
-Perform analysis on activity trends, sentiment in discussions, and contributor networks.\
-Build dashboards to compare different open-source projects.\

# Project Structure
open-source-community-analytics/\
  ├── data/             # Local data files if needed\
  ├── notebooks/        # Exploratory analysis\
  ├── src/              # ETL scripts and pipeline code\
  ├── tests/            # Data quality and unit tests\
  ├── README.md\
  ├── requirements.txt\

# Tech Stack
Python for data ingestion and transformation\
PostgreSQL for storage and data modeling\
SQLAlchemy for database interaction\
Apache Airflow for orchestration\
Streamlit for dashboards and visualizations\
NetworkX for social graph analysis\
Hugging Face for sentiment analysis\
