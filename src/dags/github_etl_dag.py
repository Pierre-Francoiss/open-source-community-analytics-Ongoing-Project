from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta

default_args = {
    "owner": "airflow",
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

with DAG(
    dag_id="github_etl_pipeline",
    default_args=default_args,
    description="Full ETL pipeline for GitHub data monitoring",
    schedule_interval="@daily",  # For daily running
    start_date=datetime(2025, 1, 1),
    catchup=False,
) as dag:

    github_etl = BashOperator(
        task_id="run_github_etl",
        bash_command="python /opt/airflow/src/etl_github.py"
    )
