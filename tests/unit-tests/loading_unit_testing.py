import pandas as pd
import sys
import os
# Get the project root directory (2 levels up from this file)
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.insert(0, project_root)
from src.db_connection import DatabaseConnection
from src.etl.load import fill_country_dim_table,fill_customer_dim_table,fill_date_dim_table,fill_product_dim_table,fill_sales_fact_table
from datetime import datetime
import pytest
from unittest.mock import Mock 
from pandas.testing import assert_frame_equal
import numpy as np
from datetime import datetime

@pytest.fixture
def mock_db_conn():
    mock = Mock()
    return mock

@pytest.fixture
def existing_country_dim():
    return pd.DataFrame({
        "country_key":[1,2,3],
        "country": ["Egypt" , "USA" , "England"]
    })

@pytest.fixture
def existing_customer_dim():
    return pd.DataFrame({
        "customer_key" : [1,2,3,4] , 
        "customer_id":["-1",'1','2','3'],
        "customer_type":["guest",'registered','registered','registered']
    })

@pytest.fixture
def existing_date_dim():
    return pd.DataFrame({

    })

@pytest.fixture
def existing_date_dim():
    return pd.DataFrame({
    "date_key": [20250105, 20250318, 20251231],
    "full_date": [
        pd.to_datetime("2025-01-05").date(),
        pd.to_datetime("2025-03-18").date(),
        pd.to_datetime("2025-12-31").date()
    ],
    "day_of_week": [7, 2, 3],        # Monday=1
    "day_of_month": [5, 18, 31],
    "day_name": ["Sunday", "Tuesday", "Wednesday"],
    "week_of_year": [1, 12, 1],
    "month": [1, 3, 12],
    "month_name": ["January", "March", "December"],
    "quarter": [1, 1, 4],
    "year": [2025, 2025, 2025],
    "is_weekend": [True, False, False]
    })

@pytest.fixture
def existing_product_dim():
    return pd.DataFrame({
        "product_key":[1],
        "stock_code":["P1"],
        "description":[""]
    })
    


def test_fill_country_dim_when_no_new_records_to_be_inserted(mock_db_conn , existing_country_dim):

    mock_db_conn.read_dataframe_from_db.return_value = existing_country_dim


    #Given
    countries = pd.DataFrame({
        "country":["Egypt"]
    })


    #When

    result = fill_country_dim_table(countries , mock_db_conn)
    expected = pd.DataFrame({
        "country":[]
    })


    assert_frame_equal(expected , result ,check_dtype=False)

def test_fill_country_dim_when_new_records_to_be_inserted(mock_db_conn , existing_country_dim):

    mock_db_conn.read_dataframe_from_db.return_value = existing_country_dim


    #Given
    countries = pd.DataFrame({
        "country":["KSA"]
    })


    #When

    result = fill_country_dim_table(countries , mock_db_conn)
    expected = pd.DataFrame({
        "country":["KSA"]
    })


    assert_frame_equal(expected , result ,check_dtype=False)

def test_fill_customer_dim_when_customer_id_is_missing(existing_customer_dim , mock_db_conn):

    mock_db_conn.read_dataframe_from_db.return_value = existing_customer_dim


    #Given 
    customers = pd.DataFrame({
        "customer_id":[pd.NA],
        "customer_type":["guest"]
    })


    #When
    result = fill_customer_dim_table(customers , mock_db_conn)

    expected = pd.DataFrame({
        "customer_id":[] , 
        "customer_type":[]
    })
    
    assert_frame_equal(result , expected , check_index_type=False,check_dtype=False)


def test_fill_customer_dim_when_customer_id_is_mixing(existing_customer_dim , mock_db_conn):

    mock_db_conn.read_dataframe_from_db.return_value = existing_customer_dim


    #Given 
    customers = pd.DataFrame({
        "customer_id":[pd.NA , '6'],
        "customer_type":["guest" , 'registered']
    })


    #When
    result = fill_customer_dim_table(customers , mock_db_conn)

    expected = pd.DataFrame({
        "customer_id":['6'] , 
        "customer_type":['registered']
    })

    assert_frame_equal(result , expected , check_index_type=False,check_dtype=False)


def test_fill_customer_dim_when_customer_id_is_already_exists(existing_customer_dim , mock_db_conn):

    mock_db_conn.read_dataframe_from_db.return_value = existing_customer_dim


    #Given 
    customers = pd.DataFrame({
        "customer_id":['2'],
        "customer_type":['registered']
    })


    #When
    result = fill_customer_dim_table(customers , mock_db_conn)

    expected = pd.DataFrame({
        "customer_id":[] , 
        "customer_type":[]
    })

    assert_frame_equal(result , expected , check_index_type=False,check_dtype=False)


def test_fill_date_dim_when_record_not_exists(existing_date_dim , mock_db_conn):
    mock_db_conn.read_dataframe_from_db.return_value = existing_date_dim

    #Given
    dates = pd.DataFrame({
        "invoice_date":[pd.Timestamp("2026-01-01 00:00:00")]
    })


    #when

    result = fill_date_dim_table(dates , mock_db_conn)
    expected = pd.DataFrame({
    "date_key": [20260101],
    "full_date": [pd.to_datetime("2026-01-01").date()],
    "day_of_week": [4],          # Monday=1 → Thursday=4
    "day_of_month": [1],
    "day_name": ["Thursday"],
    "week_of_year": [1],
    "month": [1],
    "month_name": ["January"],
    "quarter": [1],
    "year": [2026],
    "is_weekend": [False]
})

    #then

    assert_frame_equal(result , expected)

def test_fill_date_dim_when_record_is_exists(existing_date_dim , mock_db_conn):
    mock_db_conn.read_dataframe_from_db.return_value = existing_date_dim

    #Given
    dates = pd.DataFrame({
        "invoice_date":[pd.Timestamp("2025-01-05 00:00:00")]
    })


    #when

    result = fill_date_dim_table(dates , mock_db_conn)
    expected = pd.DataFrame({
    "date_key": [],
    "full_date": [],
    "day_of_week": [],       
    "day_of_month": [],
    "day_name": [],
    "week_of_year": [],
    "month": [],
    "month_name": [],
    "quarter": [],
    "year": [],
    "is_weekend": []
})

    #then

    assert_frame_equal(result , expected,check_dtype=False)

def test_fill_date_dim_when_record_is_exists(existing_date_dim , mock_db_conn):
    mock_db_conn.read_dataframe_from_db.return_value = existing_date_dim

    #Given
    dates = pd.DataFrame({
        "invoice_date":[pd.Timestamp("2025-01-05 00:00:00")]
    })


    #when

    result = fill_date_dim_table(dates , mock_db_conn)
    expected = pd.DataFrame({
    "date_key": [],
    "full_date": [],
    "day_of_week": [],       
    "day_of_month": [],
    "day_name": [],
    "week_of_year": [],
    "month": [],
    "month_name": [],
    "quarter": [],
    "year": [],
    "is_weekend": []
})

    #then

    assert_frame_equal(result , expected,check_dtype=False)

def test_product_dim_when_product_not_exists(mock_db_conn , existing_product_dim):
    
    mock_db_conn.read_dataframe_from_db.return_value = existing_product_dim


    #Given

    products = pd.DataFrame({
        "stock_code":["P2"] ,
        "description":[""]
    })

    #When

    result = fill_product_dim_table(products , mock_db_conn)
    expected = pd.DataFrame({

        "stock_code":["P2"] ,
        "description":[""]
    })


    #Then

    assert_frame_equal(result , expected , check_dtype=False)


def test_product_dim_when_product_exists(mock_db_conn , existing_product_dim):
    
    mock_db_conn.read_dataframe_from_db.return_value = existing_product_dim


    #Given

    products = pd.DataFrame({
        "stock_code":["P1"] ,
        "description":[""]
    })

    #When

    result = fill_product_dim_table(products , mock_db_conn)
    expected = pd.DataFrame({

        "stock_code":[] ,
        "description":[]
    })


    #Then

    assert_frame_equal(result , expected , check_dtype=False)
