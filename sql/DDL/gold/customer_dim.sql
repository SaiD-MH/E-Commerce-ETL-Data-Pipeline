CREATE TABLE IF NOT EXISTS gold.customer_dim (

    customer_key SERIAL PRIMARY KEY,
    customer_id INTEGER NULL,
    customer_type VARCHAR(20) NOT NULL

);

CREATE INDEX customer_type_index ON gold.customer_dim(customer_type);