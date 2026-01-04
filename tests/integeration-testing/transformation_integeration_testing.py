import sys
import os
# Get the project root directory (2 levels up from this file)
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.insert(0, project_root)

from src.db_connection import DatabaseConnection
from src.etl.extract import run_extraction
from src.etl.transform import run_transformation_cycle
from datetime import datetime
import pytest
from pandas.testing import assert_frame_equal

from testcontainers.postgres import PostgresContainer
from sqlalchemy import text


@pytest.fixture(scope="function")
def pg_container():
    with PostgresContainer() as pg:
        db_conn = DatabaseConnection(pg.get_container_host_ip() , pg.dbname ,pg.username,pg.password,pg.get_exposed_port(5432))
          # 🔹 Initialize schema & table
        with db_conn.engine.begin() as conn:
            conn.execute(text("""
               CREATE SCHEMA IF NOT EXISTS bronze;

                CREATE TABLE IF NOT EXISTS bronze.raw_sales (
                    raw_sales_id SERIAL PRIMARY KEY,
                    invoice_number VARCHAR(50)  NULL,  -- Must have
                    stock_code VARCHAR(50) NULL,      -- Must have
                    description VARCHAR(500),             -- Optional
                    quantity INTEGER NULL,            -- Must have
                    invoice_date TIMESTAMP NULL,      -- Must have
                    unit_price NUMERIC(10,2) NULL,    -- Must have
                    customer_id VARCHAR(50),              -- Optional (guests)
                    country VARCHAR(100),                 -- Optional
                    ingestion_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
                );
                              
                
                CREATE SCHEMA IF NOT EXISTS silver;

                CREATE TABLE IF NOT EXISTS silver.cleansed_sales (
                    silver_sales_id SERIAL PRIMARY KEY,
                    raw_sales_id INTEGER NOT NULL,
                    invoice_number VARCHAR(50) NOT NULL,  -- Must have
                    stock_code VARCHAR(50) NOT NULL,      -- Must have
                    description VARCHAR(500),             -- Optional
                    quantity INTEGER NOT NULL,            -- Must have
                    invoice_date TIMESTAMP NOT NULL,      -- Must have
                    unit_price NUMERIC(10,2) NOT NULL,    -- Must have
                    customer_id VARCHAR(50),              -- Optional (guests)
                    country VARCHAR(100),                 -- Optional
                    ingestion_date TIMESTAMP NOT NULL,
                    customer_type VARCHAR(20) NOT NULL,
                    is_return boolean NOT NULL,
                    total_line NUMERIC(15,2) NOT NULL,
                    transformed_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
                );

            """))
        yield db_conn



def test_transformation_cycle_when_sucess(pg_container):

    

    extraction_result  = run_extraction(pg_container)
    transformation_result = run_transformation_cycle(pg_container)

    expected_of_extraction = {
            "source_loaded_num":10097,
            "total_inserted_into_bronze":10097,
            "status":"Success"
    }

    expected_of_transformation = {
            "source_loaded_num":10051,
            "total_inserted_into_silver":10051,
            "status":"Success"
    }

    assert extraction_result == expected_of_extraction
    assert transformation_result == expected_of_transformation

