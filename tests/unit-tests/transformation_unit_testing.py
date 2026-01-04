import pandas as pd
import sys
import os
# Get the project root directory (2 levels up from this file)
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.insert(0, project_root)

from src.etl.transform import add_customer_type_column , add_is_return_column ,add_total_line_column , drop_non_postive_unit_price_values , add_transformation_date_column , drop_nullable_values , drop_zero_quantity,load_transformed_data_into_database,standardize_invoice_date_format
from datetime import datetime
import pytest
from pandas.testing import assert_frame_equal
import numpy as np
@pytest.fixture
def nullable_df():

    return pd.DataFrame({
    "raw_sales_id": [1, 2, 3],
    "invoice_number": [None, "INV-1002", "INV-1003"],
    "stock_code": ["S001", None, "S003"],
    "description": ["White T-Shirt", "Blue Jeans", "Sneakers"],
    "quantity": [3, 1, 2],
    "invoice_date": [
        pd.Timestamp("2025-01-01 10:15:00"),
        pd.Timestamp("2025-01-02 14:30:00"),
        pd.Timestamp("2025-01-03 18:45:00"),
    ],
    "unit_price": [19.99, 49.50, 89.99],
    "customer_id": ["CUST-01", None, "CUST-02"],
    "country": ["United Kingdom", "Germany", "France"],
    "ingestion_date": [
        pd.Timestamp("2025-01-01 10:20:00"),
        pd.Timestamp("2025-01-02 14:35:00"),
        pd.Timestamp("2025-01-03 18:50:00"),
    ],
    })

@pytest.fixture
def df():
    return pd.DataFrame({
    "raw_sales_id": [1, 2, 3],
    "invoice_number": ["INV-1001", "INV-1002", "INV-1003"],
    "stock_code": ["S001", "S002", "S003"],
    "description": ["White T-Shirt", "Blue Jeans", "Sneakers"],
    "quantity": [3, 1, 2],
    "invoice_date": [
        pd.Timestamp("2025-01-01 10:15:00"),
        pd.Timestamp("2025-01-02 14:30:00"),
        pd.Timestamp("2025-01-03 18:45:00"),
    ],
    "unit_price": [19.99, 49.50, 89.99],
    "customer_id": ["CUST-01", None, "CUST-02"],
    "country": ["United Kingdom", "Germany", "France"],
    "ingestion_date": [
        pd.Timestamp("2025-01-01 10:20:00"),
        pd.Timestamp("2025-01-02 14:35:00"),
        pd.Timestamp("2025-01-03 18:50:00"),
    ],
    })


def test_drop_nullable_values_have_null_values(nullable_df):

    #Given a nullbale dataframe 

    #when calling drop nullable values
    result = drop_nullable_values(nullable_df)


    #Then 
    assert len(result) ==1


def test_drop_nullable_values_have_full_values(df):

    #Given a nullbale dataframe 

    #when calling drop nullable values
    result = drop_nullable_values(df)


    #Then 
    assert len(result) ==3

def test_drop_zero_qunatity_with_non_zero_dataframe():
    
    #Given 
    data = pd.DataFrame({
        'quantity':[1,2,3]
    })


    #when calling drop zero quantity

    result = drop_zero_quantity(data)

    #Then 

    assert len(result) == 3


def test_drop_zero_qunatity_with_zero_dataframe():
    
    #Given 
    data = pd.DataFrame({
        'quantity':[1,0,0]
    })


    #when calling drop zero quantity

    result = drop_zero_quantity(data)

    #Then 

    assert len(result) == 1


def test_standardize_invoice_date_format():
    data = pd.DataFrame({
        'invoice_date': [pd.Timestamp("2025-01-01 10:15:00"),
                         pd.Timestamp("2025-01-25 10:15:00"),
                         pd.Timestamp("01-01-2025 10:15:00")]
    })


    result = standardize_invoice_date_format(data)


    expected = pd.DataFrame({
        'invoice_date': [pd.Timestamp("2025-01-01 10:15:00"),
                         pd.Timestamp("2025-01-25 10:15:00"),
                         pd.Timestamp("2025-01-01 10:15:00")]
    })
    assert_frame_equal(result , expected ,check_dtype=False)

def test_drop_non_postive_unit_price_values_with_positive_values():
    
    #Given
    data = pd.DataFrame({
        'unit_price' : [1.2,3,4.1]
    })

    #When 

    result = drop_non_postive_unit_price_values(data)

    #Then

    assert len(result) == 3


def test_drop_non_postive_unit_price_values_with_non_positive_values():
    
    #Given
    data = pd.DataFrame({
        'unit_price' : [1.2,0,-4.1]
    })

    #When 

    result = drop_non_postive_unit_price_values(data)

    #Then

    assert len(result) == 1


def test_add_transformation_date_column(monkeypatch):

    data = pd.DataFrame({
        'col1':[1,2,3]
    })


     # Given
    fixed_date = datetime(2026, 1, 2, 0, 0, 0)

    class MockDatetime(datetime):
        @classmethod
        def now(cls):
            return fixed_date

    monkeypatch.setattr(
        "src.etl.transform.datetime",
        MockDatetime
    )

    expected = data.copy()
    expected["transformed_date"] = fixed_date

    # When
    result = add_transformation_date_column(data)

    # Then
    assert_frame_equal(expected, result)


def test_add_customer_type_column_when_all_ids_are_exists():

    #Given
    data = pd.DataFrame({
        'customer_id' : ['cust1' , 'cust2' , 'cust3']
    })

    #When 
    result = add_customer_type_column(data)
    expected = pd.DataFrame({
        'customer_id' : ['cust1' , 'cust2' , 'cust3'],
        'customer_type':['registered','registered','registered']
    })


    #Then 

    assert_frame_equal(result , expected)


def test_add_customer_type_column_when_all_ids_are_missing():

    #Given
    data = pd.DataFrame({
        'customer_id' : ['cust1' , None , 'cust3']
    })

    #When 
    result = add_customer_type_column(data)
    expected = pd.DataFrame({
        'customer_id' : ['cust1' , None , 'cust3'],
        'customer_type':['registered','guest','registered']
    })


    #Then 

    assert_frame_equal(result , expected)

def test_add_is_return_column():

    #Given
    data = pd.DataFrame({
        'quantity': [1,-2,3]
    })


    #When 

    result = add_is_return_column(data) 

    expected = pd.DataFrame({
        'quantity' : [1,-2,3],
        'is_return' : [False , True , False]
    })
    #Then

    assert_frame_equal(result , expected)


def test_add_total_line_column():

    #Given
    data = pd.DataFrame({
        'quantity' : [1,2,3] , 
        'unit_price' : [1,2,3]
    })

    #When

    result = add_total_line_column(data)
    expected = pd.DataFrame({
        'quantity' : [1,2,3] , 
        'unit_price' : [1,2,3],
        'total_line' : [1,4,9]
    })

    #Then 
    
    assert_frame_equal(result , expected)
