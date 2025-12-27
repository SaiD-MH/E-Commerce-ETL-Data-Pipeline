
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

CREATE index IF NOT EXISTS transformed_date_index on silver.cleansed_sales(transformed_date);
CREATE index IF NOT EXISTS invoice_date_index on silver.cleansed_sales(invoice_date);
CREATE index IF NOT EXISTS customer_id_index on silver.cleansed_sales(customer_id);