import pandas as pd
import sys
import os
# Get the project root directory (2 levels up from this file)
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.insert(0, project_root)

from src.etl.extract import validate_required_columns_existance , add_ingestion_datetime_column,normalize_dataframe_columns_name
from datetime import datetime
import pytest
from pandas.testing import assert_frame_equal

@pytest.fixture
def df():
    return pd.DataFrame([{
    "InvoiceNo": "536365",
    "StockCode": "85123A",
    "Description": "WHITE HANGING HEART T-LIGHT HOLDER",
    "Quantity": 6,
    "InvoiceDate": "2010-12-01",
    "UnitPrice": 2.55,
    "CustomerID": 17850,
    "Country": "United Kingdom"
}])


def test_validate_requried_columns_with_missing_columns():
    
    # Given a missing requried columns
    df = pd.DataFrame({'col1':[1,2,3] , 'col2':[4,5,6]})
    
     
    expected = set(["InvoiceNo", "StockCode", "Description", "Quantity",
        "InvoiceDate", "UnitPrice", "CustomerID", "Country"])
    # When calling validate dataframe with requried columns
    result = validate_required_columns_existance(df)

    # Then 
    assert result == expected


def test_validate_requried_columns_with_requried_columns():
    
    # Given a missing requried columns
    df = pd.DataFrame([{
        "InvoiceNo": [],
        "StockCode": [],
        "Description": [],
        "Quantity": [],
        "InvoiceDate": [],
        "UnitPrice": [],
        "CustomerID": [],
        "Country": []
    }])

    
     
    expected = set([])
    
    
    # When calling validate dataframe with requried columns
    result = validate_required_columns_existance(df)

    # Then 
    assert result == expected


def test_adding_ingestion_date_to_normal_dataframe(df, monkeypatch):
    # Given
    fixed_date = datetime(2026, 1, 2, 0, 0, 0)

    class MockDatetime(datetime):
        @classmethod
        def now(cls):
            return fixed_date

    monkeypatch.setattr(
        "src.etl.extract.datetime",
        MockDatetime
    )

    expected = df.copy()
    expected["ingestion_date"] = fixed_date

    # When
    result = add_ingestion_datetime_column(df)

    # Then
    assert_frame_equal(expected, result)

def test_normalize_dataframe_columns_name(df):
    
    #Given a normal dataframe
     
    # When calling normalize dataframe 
    result = normalize_dataframe_columns_name(df)




    excepted = pd.DataFrame([{
    "invoice_number": None,
    "stock_code": None,
    "description": None,
    "quantity": None,
    "invoice_date": None,
    "unit_price": None,
    "customer_id": None,
    "country": None
            }])

  
    assert list(excepted.columns) == list(result.columns)