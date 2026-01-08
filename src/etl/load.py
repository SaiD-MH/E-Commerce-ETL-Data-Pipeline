import pandas as pd
import sys
import os
# Add parent directory to path
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), "../..")))
from src.db_connection import DatabaseConnection
from datetime import datetime
from sqlalchemy import text
import numpy as np

def get_max_transformed_date(db_conn: DatabaseConnection) -> datetime.date:
    """
        Function to return the max date of the column from the bronze.raw_sales
        to be used in fetching the new inserted data into bronze
    """

    with db_conn.engine.begin() as query_conn:
        result = query_conn.execute(text(""" SELECT max(transformed_date) FROM SILVER.cleansed_sales; """))
    return result.scalar().date()



def read_data_from_silver(db_conn: DatabaseConnection) ->pd.DataFrame:
    """
    Docstring for read_data_from_silver
    
    :param db_conn: database connection object
    :type db_conn: DatabaseConnection
    :return: return the data from silver layer which have max data to be processed
    :rtype: DataFrame
    """
    return db_conn.read_dataframe_from_db(f"SELECT * FROM Silver.cleansed_sales where transformed_date >= DATE '{get_max_transformed_date(db_conn)}'")



def fill_date_dim_table(cleansed_data: pd.DataFrame, db_connection: DatabaseConnection) -> pd.DataFrame:
    """
    Fill date dimension table for the ingestion date.

    Returns:
        DataFrame with single date dimension record
    """
    

    date_dim = cleansed_data[['invoice_date']].copy()

    date_dim['date_key'] = date_dim['invoice_date'].apply(lambda x: int(x.strftime("%Y%m%d")))
    date_dim['full_date'] = date_dim['invoice_date'].apply(lambda x: x.date())
    date_dim['day_of_week'] = date_dim['invoice_date'].apply(lambda x: x.date().weekday()+ 1)
    date_dim['day_of_month'] = date_dim['invoice_date'].apply(lambda x: x.date().day)
    date_dim['day_name'] = date_dim ['invoice_date'].apply(lambda x: x.date().strftime("%A"))
    date_dim['week_of_year'] = date_dim['invoice_date'].apply(lambda x: x.date().isocalendar()[1])
    date_dim['month'] = date_dim['invoice_date'].apply(lambda x: x.date().month)
    date_dim['month_name']=date_dim['invoice_date'].apply(lambda x: x.date().strftime("%B"))
    date_dim['quarter']=date_dim['invoice_date'].apply(lambda x: (x.date().month - 1 )// 3 + 1)
    date_dim['year'] = date_dim['invoice_date'].apply(lambda x: x.date().year)
    date_dim['is_weekend'] = date_dim['invoice_date'].apply(lambda x: x.date().weekday() >= 5)


    all_stored_dates = db_connection.read_dataframe_from_db("SELECT * FROM GOLD.DATE_DIM;")

    date_dim = date_dim.merge(all_stored_dates , how='left' , on=['date_key'] , indicator=True, suffixes=("","X"))


    date_dim = date_dim[date_dim['_merge'] == 'left_only']
    

    date_dim = date_dim[["date_key","full_date","day_of_week","day_of_month","day_name","week_of_year","month","month_name","quarter","year","is_weekend"]]
    date_dim = date_dim.drop_duplicates(subset=['date_key'])
    # 0 if len(date_dim) == 0 else db_connection.load_dataframe_into_db(date_dim , 'gold' , 'date_dim')    
    return  date_dim



def fill_customer_dim_table(cleansed_data: pd.DataFrame , db_conn:DatabaseConnection) -> pd.DataFrame:

    """
    Docstring for fill_customer_dim_table
    
    :param cleansed_data: cleased data related to customer info to be loaded into customer dim table
    :type cleansed_data: pd.DataFrame
    :param db_conn: database connection object for r/w dataframe from / into database
    :type db_conn: DatabaseConnection
    :return: new batch of the customer data to be inserted into the customer dim
    :rtype: DataFrame
    """
    customer_data = cleansed_data.copy()
    
    known_customers = customer_data[ customer_data['customer_type'] =='registered']
    unknown_customers = customer_data[ customer_data['customer_type'] =='guest']
    
    all_existing_customers = db_conn.read_dataframe_from_db("SELECT * FROM gold.customer_dim where customer_type ='registered';")

    customers_to_be_inserted = known_customers.merge(all_existing_customers , how='left',on=['customer_id'],indicator=True ,suffixes=["" , "X"])
    customers_to_be_inserted = customers_to_be_inserted[customers_to_be_inserted['_merge'] == 'left_only']
    customers_to_be_inserted = customers_to_be_inserted[ ['customer_id' , 'customer_type']]
    customers_to_be_inserted = customers_to_be_inserted.drop_duplicates(subset=['customer_id' ,'customer_type'])
    
    customers_to_be_inserted = pd.concat([customers_to_be_inserted , unknown_customers],ignore_index=True)
    customers_to_be_inserted = customers_to_be_inserted [ ['customer_id' , 'customer_type']]
    # 0 if len(customers_to_be_inserted) == 0  else db_conn.load_dataframe_into_db(customers_to_be_inserted , 'gold','customer_dim')
    return customers_to_be_inserted


def fill_product_dim_table(cleansed_data:pd.DataFrame ,db_conn:DatabaseConnection)-> pd.DataFrame:
    """
    Docstring for fill_product_dim_table
    
    :param cleansed_data: cleased data regarding the product info
    :type cleansed_data: pd.DataFrame
    :param db_conn: database connection object for r/w dataframe from / into database
    :type db_conn: DatabaseConnection
    :return: Description
    :rtype: DataFrame
    """


    product_dim = cleansed_data.copy()

    all_existing_products = db_conn.read_dataframe_from_db("SELECT * FROM GOLD.Product_dim;")

    product_dim = product_dim.merge(all_existing_products , how='left',on=['stock_code'] , indicator=True ,suffixes=["" , "X"])

    product_dim = product_dim[ product_dim['_merge']=='left_only']

    product_dim = product_dim.drop_duplicates(subset=['stock_code'])


    return product_dim[['stock_code' , 'description']]


def fill_country_dim_table(cleansed_data: pd.DataFrame , db_conn: DatabaseConnection)-> pd.DataFrame:
    """
    Docstring for fill_country_dim_table
    
    :param cleansed_data: cleansed data regarding product dim info
    :type cleansed_data: pd.DataFrame
    :param db_conn: database connection object for r/w dataframe from / into database
    :type db_conn: DatabaseConnection
    :return: Description
    :rtype: DataFrame
    """
    new_country_batch = cleansed_data[ ['country']]

    all_countries = db_conn.read_dataframe_from_db("SELECT * FROM gold.country_dim;")

    new_batch_to_be_inserted = new_country_batch.merge(all_countries , how = 'left' , on=['country'],indicator=True)
    
    new_batch_to_be_inserted = new_batch_to_be_inserted[ new_batch_to_be_inserted['_merge']=='left_only']
    new_batch_to_be_inserted = new_batch_to_be_inserted[['country']].drop_duplicates(subset=['country'])

    # 0 if len(new_batch_to_be_inserted) == 0 else db_conn.load_dataframe_into_db(new_batch_to_be_inserted ,'gold' , 'country_dim')
    return new_batch_to_be_inserted

def fill_sales_fact_table(db_conn:DatabaseConnection , cleansed_data:pd.DataFrame )-> pd.DataFrame:
    """
    Docstring for fill_sales_fact_table
    
    :param db_conn: database connection object for r/w dataframe from / into database
    :type db_conn: DatabaseConnection
    :param cleansed_data: cleased data related to fact table to fill it
    :type cleansed_data: pd.DataFrame
    :return: Description
    :rtype: DataFrame
    """
    # Load Dims

    customer_dim = db_conn.read_dataframe_from_db("SELECT * FROM  GOLD.CUSTOMER_DIM;")
    country_dim = db_conn.read_dataframe_from_db("SELECT  * FROM  GOLD.COUNTRY_DIM;")
    product_dim = db_conn.read_dataframe_from_db("SELECT * FROM GOLD.product_dim;")

    cleansed_data['date_key'] = cleansed_data['invoice_date'].apply(lambda x: int(x.strftime("%Y%m%d")))
    cleansed_data['customer_id'] = cleansed_data['customer_id'].apply(lambda x: '-1' if x == pd.isna(x) else x)    
    cleansed_data = cleansed_data.merge(country_dim , on=['country'] , how='inner')
    cleansed_data = cleansed_data.merge(customer_dim ,how='inner',on=['customer_id'],suffixes=["", "X"])
    cleansed_data = cleansed_data.merge(product_dim , how='inner' , on=['stock_code'] , suffixes=["" , "X"])
    sales_fact_dim = cleansed_data[ ['silver_sales_id', 'date_key' , 'product_key' , 'country_key' , 'customer_key' , 'invoice_number',
                                     'quantity' , 'unit_price', 'is_return' , 'total_line'] ]


    return sales_fact_dim
    
def load_dim_tables_into_gold_schema(db_conn:DatabaseConnection , dim_tables:list):
    """
    Docstring for load_dim_tables_into_gold_schema
    
    :param db_conn: database connection object for r/w dataframe from / into database
    :type db_conn: DatabaseConnection
    :param dim_tables: list of all dims tables to be inserted into the database list of dict keys -> table_name , table_data
    :type dim_tables: list of dict
    """

    for table in dim_tables:
        if len(table['table_data']):
            db_conn.load_dataframe_into_db(table["table_data"] , 'gold',table['table_name'])

def run_load(db_conn:DatabaseConnection):
    """
    Docstring for run_load
    Purpose: to orchestra the execution flow of the loading script
    :param db_conn: database connection object for r/w dataframe from / into database
    :type db_conn: DatabaseConnection
    """
    cleansed_data = read_data_from_silver(db_conn)
    date_dim = fill_date_dim_table(cleansed_data[['invoice_date']],db_conn)
    customer_dim = fill_customer_dim_table(cleansed_data[['customer_id','customer_type']],db_conn)
    product_dim = fill_product_dim_table(cleansed_data[['stock_code' , 'description']] ,db_conn)
    country_dim = fill_country_dim_table(cleansed_data[['country']],db_conn)

    dim_metadata = [ 
        {
            "table_name":"date_dim",
            "table_data":date_dim
        },
        {
            "table_name":"customer_dim",
            "table_data":customer_dim
        },
        {
            "table_name":"product_dim",
            "table_data":product_dim
        },
        {
            "table_name":"country_dim",
            "table_data":country_dim
        }
     
    ]

    load_dim_tables_into_gold_schema(db_conn , dim_metadata)

    sales_fact =  fill_sales_fact_table(db_conn , cleansed_data)

    total_inserted_into_gold = db_conn.load_dataframe_into_db(sales_fact , 'gold','sales_fact')

    silver_data_len = len(cleansed_data)

    return {
        "total_from_silver": silver_data_len,
        "total_inserted_into_gold" : total_inserted_into_gold,
        "status" : "Success" if (silver_data_len == total_inserted_into_gold) else "Failed"
    }



if __name__ == '__main__':
    print(run_load(DatabaseConnection()))


