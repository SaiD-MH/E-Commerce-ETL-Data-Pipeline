import sys
import os
# Get the project root directory (2 levels up from this file)
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.insert(0, project_root)

from src.db_connection import DatabaseConnection
from src.etl.extract import run_extraction
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

            """))
        yield db_conn



def test_extraction_cycle_when_sucess(pg_container):

    

    result  = run_extraction(pg_container  )

    expected = {
            "source_loaded_num":999,
            "total_inserted_into_bronze":999,
            "status":"Success"
    }

    assert result == expected



def test_extraction_cycle_when_failed(pg_container):

    

    result  = run_extraction(pg_container  )

    expected = {
            "source_loaded_num":10097,
            "total_inserted_into_bronze":100,
            "status":"Failed"
    }

    assert result != expected





