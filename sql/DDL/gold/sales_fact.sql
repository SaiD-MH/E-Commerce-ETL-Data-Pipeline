CREATE TABLE IF NOT EXISTS gold.sales_fact (

    sales_key SERIAL PRIMARY KEY,
    silver_sales_id INTEGER NOT NULL, 
    date_key INTEGER NOT NULL,
    product_key VARCHAR(100) NOT NULL,
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

CREATE INDEX IF NOT EXISTS sales_key_index on gold.sales_fact(sales_key);
CREATE INDEX IF NOT EXISTS date_key_index on gold.sales_fact(date_key);
CREATE INDEX IF NOT EXISTS country_key_index on gold.sales_fact(country_key);
CREATE INDEX IF NOT EXISTS product_key_index on gold.sales_fact(product_key);



