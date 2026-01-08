import sys
import os
# Get the project root directory (2 levels up from this file)
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.insert(0, project_root)

from src.db_connection import DatabaseConnection
from src.etl.extract import run_extraction
from src.etl.transform import run_transformation_cycle
from src.etl.load import run_load
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
                CREATE SCHEMA IF NOT EXISTS gold;   
                CREATE TABLE IF NOT EXISTS gold.country_dim(

                country_key SERIAL PRIMARY KEY,
                country VARCHAR(200) NOT NULL);

                CREATE TABLE IF NOT EXISTS gold.customer_dim (

                customer_key SERIAL PRIMARY KEY,
                customer_id VARCHAR NULL,
                customer_type VARCHAR(20) NOT NULL

            );
            CREATE TABLE IF NOT EXISTS gold.date_dim(

                date_key int primary key ,
                full_date timestamp not null ,
                day_of_week int not null,
                day_of_month int not null,
                day_name varchar(10) not null,
                week_of_year int not null,
                month int not null,
                month_name varchar(10) not null , 
                quarter int not null , 
                year int not null,
                is_weekend boolean not null 
            );    
            
            CREATE TABLE IF NOT EXISTS gold.product_dim (

                product_key SERIAL PRIMARY KEY,
                description VARCHAR(1000) NULL , 
                stock_code VARCHAR(100) NOT NULL 
            );
            CREATE TABLE IF NOT EXISTS gold.sales_fact (

                sales_key SERIAL PRIMARY KEY,
                silver_sales_id INTEGER NOT NULL, 
                date_key INTEGER NOT NULL,
                product_key integer NOT NULL,
                country_key INTEGER NOT NULL,
                customer_key INTEGER NOT NULL, 
                invoice_number VARCHAR(50) NOT NULL , 
                quantity INTEGER NOT NULL,            -- Must have
                unit_price NUMERIC(10,2) NOT NULL,    -- Must have
                is_return boolean NOT NULL,
                total_line NUMERIC(15,2) NOT NULL,
                gold_dt_ingestion TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
                CONSTRAINT fk_customer_key FOREIGN KEY (customer_key) REFERENCES gold.customer_dim(customer_key),
                CONSTRAINT fk_silver_sales_id FOREIGN KEY (silver_sales_id) REFERENCES silver.cleansed_sales(silver_sales_id),
                CONSTRAINT fk_date_key FOREIGN KEY (date_key) REFERENCES gold.date_dim(date_key),
                CONSTRAINT fk_product_key FOREIGN KEY (product_key) REFERENCES gold.product_dim(product_key),
                CONSTRAINT fk_country_key FOREIGN KEY (country_key) REFERENCES gold.country_dim(country_key)
            );

                
            """))
        yield db_conn



def test_transformation_cycle_when_sucess(pg_container):

    

    extraction_result  = run_extraction(pg_container)
    transformation_result = run_transformation_cycle(pg_container)
    loading_result = run_load(pg_container)

    expected_of_extraction = {
            "source_loaded_num":999,
            "total_inserted_into_bronze":999,
            "status":"Success"
    }

    expected_of_transformation = { 
            "source_loaded_num":998,
            "total_inserted_into_silver":998,
            "status":"Success"
    }

    expected_of_loading = { 
        "total_from_silver": 998,
        "total_inserted_into_gold" : 998,
        "status" : "Success"
    }

    print(loading_result)
    print(expected_of_loading)

    assert extraction_result == expected_of_extraction
    assert transformation_result == expected_of_transformation
    assert loading_result == expected_of_loading

