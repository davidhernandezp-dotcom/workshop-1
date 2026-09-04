-- Esquema del Data Warehouse recruitment_dw
-- Generado a partir del pipeline de carga (load.py)

CREATE TABLE IF NOT EXISTS dim_date (
    date_key INT PRIMARY KEY,
    full_date DATE,
    year INT,
    month INT,
    month_name VARCHAR(20),
    quarter INT
);

CREATE TABLE IF NOT EXISTS dim_technology (
    technology_key INT PRIMARY KEY,
    technology_name VARCHAR(100)
);

CREATE TABLE IF NOT EXISTS dim_country (
    country_key INT PRIMARY KEY,
    country_name VARCHAR(100)
);

CREATE TABLE IF NOT EXISTS dim_candidate_profile (
    profile_key INT PRIMARY KEY,
    seniority VARCHAR(50),
    yoe_range VARCHAR(10)
);

CREATE TABLE IF NOT EXISTS fact_applications (
    application_key INT PRIMARY KEY,
    date_key INT,
    technology_key INT,
    country_key INT,
    profile_key INT,
    code_challenge_score INT,
    technical_interview_score INT,
    is_hired TINYINT,
    FOREIGN KEY (date_key) REFERENCES dim_date(date_key),
    FOREIGN KEY (technology_key) REFERENCES dim_technology(technology_key),
    FOREIGN KEY (country_key) REFERENCES dim_country(country_key),
    FOREIGN KEY (profile_key) REFERENCES dim_candidate_profile(profile_key)
);