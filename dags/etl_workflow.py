from airflow import DAG
from datetime import datetime
from airflow.sensors.python import PythonSensor
from airflow.operators.python import PythonOperator
from airflow.hooks.base import BaseHook
from github import Github
from src.etl.extract import run_extraction
from src.etl.transform import run_transformation_cycle
from src.etl.load import run_load
from src.db_connection import DatabaseConnection
def check_github_file(**context):
    """Check if file exists in GitHub repository"""
    try:
        # Get GitHub connection
        conn = BaseHook.get_connection('github_conn')
        github_token = conn.password
        
        # Initialize GitHub client
        g = Github(github_token)
        repo = g.get_repo('SaiD-MH/E-Commerce-ETL-Data-Pipeline')
        
        # Check if file exists
        try:
            
            from airflow.macros import ds_format
    
            execution_date = context['ds']
            
            formatted = ds_format(execution_date, "%Y-%m-%d", "%d-%m-%Y")  # 13-01-2024
            print("YOUR RECORD IS: " ,formatted)
            file_content = repo.get_contents(f'data/data_{formatted}.csv', ref='main')
            print(f"File found: {file_content.path}")
            return True
        except Exception as e:
            print(f"File not found: {str(e)}")
            return False
            
    except Exception as e:
        print(f"Error checking GitHub: {str(e)}")
        return False


def file_found(**context):
    """Process the file when found"""
    print("SUIIIIIIIIIIIIIIIii")
    print(f"File detected! Starting ETL process...")
    # Add your ETL processing logic here

def run_extraction_job():
    with DatabaseConnection() as db_conn:
        result = run_extraction(db_conn)
    
    print(result)

def run_transformation_job():
    with DatabaseConnection() as db_conn:
        result = run_transformation_cycle(db_conn)
    
    print(result)

def run_loading_job():
    with DatabaseConnection() as db_conn:
        result = run_load(db_conn)
    
    print(result)


with DAG(
    dag_id='sales_dag',
    description="DAG for ETL process of the sales data of the e-commerce",
    start_date=datetime(2026, 1, 13),
    schedule_interval="@daily",
    catchup=False,
    tags=["Sales"]
) as dag:
    
    # Use PythonSensor as alternative to GithubSensor
    github_file_sensor = PythonSensor(
        task_id="github_file_sensor",
        python_callable=check_github_file,
        poke_interval=5,
        timeout=60,
        mode='poke'
    )

    extraction_job = PythonOperator(
        task_id = "extraction_job",
        python_callable = run_extraction_job
    )

    transformation_job = PythonOperator(
        task_id = "transformation_job",
        python_callable = run_transformation_job
    )

    loading_job = PythonOperator(
        task_id = "loading_job",
        python_callable = run_loading_job
    )
    # Set task dependency
    github_file_sensor >>extraction_job >> transformation_job >>loading_job