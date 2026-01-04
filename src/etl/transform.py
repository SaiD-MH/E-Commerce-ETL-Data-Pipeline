import pandas as pd
import sys
import os
# Add parent directory to path
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), "../..")))
from src.db_connection import DatabaseConnection
from datetime import datetime
from sqlalchemy import text
import numpy as np

def get_max_ingestion_date(db_conn: DatabaseConnection) -> datetime.date:
    """
        Function to return the max date of the column from the bronze.raw_sales
        to be used in fetching the new inserted data into bronze
    """

    with db_conn.engine.begin() as query_conn:
        result = query_conn.execute(text(""" SELECT max(ingestion_date) FROM BRONZE.RAW_SALES; """))
    return result.scalar().date()


def read_raw_data_from_bronze(db_conn: DatabaseConnection)-> pd.DataFrame:
    """
        Return the data that ready to be transformed.
        Return Type: Dataframe
    """

    return  db_conn.read_dataframe_from_db(f"SELECT * FROM BRONZE.RAW_SALES WHERE ingestion_date >= DATE '{get_max_ingestion_date(db_conn)}' ")


def drop_nullable_values(raw_data: pd.DataFrame) -> pd.DataFrame:

    """
    Docstring for drop_nullable_values
    
    :param raw_data: raw data that ready to be cleased from bronze layer
    :type raw_data: pd.DataFrame
    :return: cleased data after drop null values from all columns
    :rtype: DataFrame
    """
    raw_data_copy = raw_data.copy()

    columns = ['invoice_number', 'stock_code','quantity','invoice_date' , 'unit_price']
    return raw_data_copy.dropna(subset=columns)

def drop_zero_quantity(raw_data: pd.DataFrame)-> pd.DataFrame:
    """
    Docstring for drop_zero_quantity
    
    :param raw_data: cleased data after drop null values from all columns
    :type raw_data: pd.DataFrame
    :return: cleased data after remove all rows with zero quntity
    :rtype: DataFrame
    """
    
    raw_data_copy = raw_data.copy()

    return raw_data_copy[ raw_data_copy['quantity'] != 0]


def standardize_invoice_date_format(raw_data: pd.DataFrame) -> pd.DataFrame:
    """
    Docstring for standeralize_invoice_date_format
    
    :param raw_data: raw data , dataframe store raw data to transform the invoice date
    :type raw_data: pd.DataFrame
    :return: transformed dataframe after change the format of the invoice date column
    :rtype: DataFrame
    """

    raw_data_copy = raw_data.copy()
    raw_data_copy['invoice_date'] = pd.to_datetime(raw_data_copy['invoice_date'] , errors='coerce',dayfirst=True)

    # raw_data_copy['invoice_date'] = raw_data_copy['invoice_date'].dt.strftime("%Y-%m-%d %H:%M:%S")

    return raw_data_copy

def drop_non_postive_unit_price_values(raw_data : pd.DataFrame) -> pd.DataFrame:

    """
    Docstring for drop_non_postive_unit_price_values
    
    :param raw_data: raw data to ready to be transformed to drop unit price values <= 0
    :type raw_data: pd.DataFrame
    :return: cleansed data after drop all non-postive values
    :rtype: DataFrame
    """

    raw_data_copy = raw_data.copy()

    raw_data_copy = raw_data_copy[ raw_data_copy['unit_price'] > 0 ]

    return raw_data_copy


def add_transformation_date_column(raw_data : pd.DataFrame) -> pd.DataFrame:
    """
    Docstring for add_transformation_date_column
    
    :param raw_data: add a transformation timestamp column to be able to audit and track the raw in case of failing
    :type raw_data: pd.DataFrame
    :return: Description
    :rtype: DataFrame
    """

    raw_data_copy = raw_data.copy()
    raw_data_copy['transformed_date'] = datetime.now()

    return raw_data_copy


def add_customer_type_column(raw_data: pd.DataFrame)-> pd.DataFrame:
    """
    Docstring for add_customer_type_column
    
    :param raw_data: add a customer type column as guest or registered
    :type raw_data: pd.DataFrame
    :return: return a transformed dataframe after add the customer type column
    :rtype: DataFrame
    """

    raw_data_copy = raw_data.copy()
    
    raw_data_copy['customer_type'] = raw_data_copy['customer_id'].apply(lambda x: "guest" if pd.isna(x) else 'registered')

    return raw_data_copy


def add_is_return_column(raw_data: pd.DataFrame)-> pd.DataFrame:
    """
    Docstring for add_is_return_column
    
    :param raw_data: add is return column for quantity less than zero
    :type raw_data: pd.DataFrame
    :return: transformed dataframe with is returned column
    :rtype: DataFrame
    """


    raw_data_copy = raw_data.copy()
    raw_data_copy['is_return'] = raw_data_copy['quantity'].apply(lambda x: True if x < 0 else False)
    return raw_data_copy



def add_total_line_column(raw_data : pd.DataFrame) -> pd.DataFrame :
    """
    Docstring for add_total_line_column
    
    :param raw_data: Add total line column as transformed calculated column refer to total price 
    :type raw_data: pd.DataFrame
    :return: transfored dataframe with total line column
    :rtype: DataFrame
    """

    raw_data_copy = raw_data.copy()
    raw_data_copy['total_line'] = raw_data_copy['quantity'] * raw_data_copy['unit_price']

    return raw_data_copy

def load_transformed_data_into_database(tranformed_data : pd.DataFrame , db_conn : DatabaseConnection) ->int:
    """
    Docstring for load_transformed_data_into_database
    
    :param tranformed_data: stored transformed data into the database tot the silver schema
    :type tranformed_data: pd.DataFrame
    :return: total number of inserted columns into the silver schema 
    :rtype: int
    """

    return db_conn.load_dataframe_into_db(tranformed_data , "silver" , "cleansed_sales")

    


def run_transformation_cycle(db_connection: DatabaseConnection) -> dict:
    """
    Docstring for run_transformation_cycle
    
    :param db_connection: Transformation (T) orchestration cycle 
    :type db_connection: DatabaseConnection
    :return: metadata about the loaded and stored data
    :rtype: dict
    """
    raw_data = read_raw_data_from_bronze(db_connection)
    cleansed = drop_nullable_values(raw_data)
    cleansed = drop_zero_quantity(cleansed)
    cleansed = standardize_invoice_date_format(cleansed)
    cleansed = drop_non_postive_unit_price_values(cleansed)
    cleansed = add_customer_type_column(cleansed)
    cleansed = add_transformation_date_column(cleansed)
    cleansed = add_is_return_column(cleansed)
    cleansed = add_total_line_column(cleansed)
    cleansed_length = len(cleansed)
    total_inserted = load_transformed_data_into_database(cleansed , db_connection)

    return {
        "source_loaded_num": cleansed_length,
        "total_inserted_into_silver" : total_inserted,
        "status" : "Success" if (total_inserted == cleansed_length) else "Failed"
    }


if __name__ == '__main__':
    print(run_transformation_cycle(DatabaseConnection()))

