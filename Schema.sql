
-- DIM DATE
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS dim_date (
    date_id         INT PRIMARY KEY,        -- e.g. 20230911 (YYYYMMDD)
    full_date       DATE NOT NULL UNIQUE,
    day             INT NOT NULL,
    month           INT NOT NULL,
    month_name      VARCHAR(15) NOT NULL,
    quarter         INT NOT NULL,
    year            INT NOT NULL,
    day_name        VARCHAR(15) NOT NULL,
    is_weekend      BOOLEAN NOT NULL
);

-- ------------------------------------------------------------
-- DIM CITY
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS dim_city (
    city_id         SERIAL PRIMARY KEY,
    city_name       VARCHAR(50) NOT NULL UNIQUE,
    region          VARCHAR(50),
    latitude        FLOAT,
    longitude       FLOAT
);

-- ------------------------------------------------------------
-- FACT WEATHER
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS fact_weather (
    weather_id                  SERIAL PRIMARY KEY,
    date_id                     INT NOT NULL REFERENCES dim_date(date_id),
    city_id                     INT NOT NULL REFERENCES dim_city(city_id),
    temperature_2m_max          FLOAT,
    temperature_2m_min          FLOAT,
    temperature_2m_mean         FLOAT,
    apparent_temperature_max    FLOAT,
    apparent_temperature_min    FLOAT,
    precipitation_sum           FLOAT,
    rain_sum                    FLOAT,
    windspeed_10m_max           FLOAT,
    windgusts_10m_max           FLOAT,
    winddirection_10m_dominant  INT,
    shortwave_radiation_sum     FLOAT,
    sunshine_duration           FLOAT,
    et0_fao_evapotranspiration  FLOAT,
    weathercode                 INT,
    UNIQUE (date_id, city_id)
);

-- Helpful indexes for query performance
CREATE INDEX IF NOT EXISTS idx_fact_weather_date ON fact_weather(date_id);
CREATE INDEX IF NOT EXISTS idx_fact_weather_city ON fact_weather(city_id);

SELECT datname FROM pg_database;

SELECT '[' || datname || ']' as exact_name, length(datname) FROM pg_database WHERE datname LIKE 'Weather%';

SELECT COUNT(*) FROM dim_date;
SELECT COUNT(*) FROM dim_city;
SELECT COUNT(*) FROM fact_weather;
   