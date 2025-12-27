CREATE TABLE IF NOT EXISTS gold.product_dim (

    product_key SERIAL PRIMARY KEY,
    description VARCHAR(1000) NULL , 
    stock_code VARCHAR(100) NOT NULL 
);


CREATE INDEX IF NOT EXISTS stock_code_index ON gold.product_dim(stock_code);

