
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

CREATE index IF NOT EXISTS ingestion_date_index on bronze.raw_sales(ingestion_date);