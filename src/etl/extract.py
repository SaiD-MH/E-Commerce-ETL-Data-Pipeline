
import pandas as pd
import sys
import os
# Add parent directory to path
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), "../..")))
from src.db_connection import DatabaseConnection
from datetime import datetime

# url = 'https://raw.githubusercontent.com/SaiD-MH/Covid-19-Data-Pipeline/main/data/03-25-2025.csv'



def read_csv_from_source(file_name :str) -> pd.DataFrame:
    """
        Params: File Name to read
        Read csv file and return total number for readed files
    """

    uri = f'../../data/{file_name}'
    try:

        raw_data = pd.read_csv(uri)
    except FileNotFoundError as e:
        raise (f"File Not Found, Check file avaiability: {uri}") from e
    except Exception as e:
        raise Exception (f"Error while trying loading the file : {e}") from e

    return raw_data



def add_ingestion_datetime_column(raw_data : pd.DataFrame) -> pd.DataFrame:
    """
    Docstring for add_ingestion_datetime_column
    
    :param raw_data: the panda dataframe
    :type raw_data: pd.DataFrame
    :return: return dataframe after adding the ingested date column
    :rtype: DataFrame
    """
    df = raw_data.copy()
    df['ingestion_date'] = datetime.now()
    return df


def normalize_dataframe_columns_name(raw_data : pd.DataFrame) -> pd.DataFrame:
    """
    Docstring for normalize_dataframe_columns_name
    
    :param raw_data: raw data
    :type raw_data: pd.DataFrame
    :return: dataframe after columns renameing
    :rtype: DataFrame
    """
    
    columns_rename = {
        "InvoiceNo":"invoice_number",
        "StockCode":"stock_code", 
        "Description":"description",
        "Quantity":"quantity",
        "InvoiceDate" :"invoice_date",
        "UnitPrice": "unit_price",
        "CustomerID" :"customer_id",
        "Country" :"country"

    }
    df = raw_data.copy()

    return df.rename(columns=columns_rename)



def load_raw_data_to_bronze(raw_data: pd.DataFrame , db_connection: DatabaseConnection) -> int:
    """
        Load raw data , dataframe into the database
        to bronze schema

        args:
            - raw_data : the raw data to be loaded into the bronze schema
            - database connection object: abstract all the complexitiy of working the database

        return:
            total number of loaded data into bronze
    """ 
    return db_connection.load_dataframe_into_db(raw_data , "bronze", "raw_sales")


def run_extraction() -> dict:

    """
    Function to orchestra the execution flow of the extraction script
    
    :return: return dictionary with information about the execution flow 
    :rtype: dict
    """
    conn = DatabaseConnection()
    raw_data = read_csv_from_source('data_13-12-2025.csv')
    raw_data = normalize_dataframe_columns_name(raw_data)
    raw_data = add_ingestion_datetime_column(raw_data)
    total_inserted = load_raw_data_to_bronze(raw_data , conn)

    extraction_meta_data ={
        "source_loaded_num": len(raw_data),
        "total_inserted_into_bronze" : total_inserted,
        "status" : "Success" if (len(raw_data) == total_inserted) else "Failed"
    }

    return extraction_meta_data


run_extraction()