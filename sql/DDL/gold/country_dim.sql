CREATE TABLE IF NOT EXISTS gold.country_dim(

    country_key SERIAL PRIMARY KEY,
    country VARCHAR(200) NOT NULL
);

CREATE INDEX country_index ON gold.country_dim(country);



