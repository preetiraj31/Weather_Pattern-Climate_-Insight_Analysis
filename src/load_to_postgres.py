import pandas as pd
from pathlib import Path
from sqlalchemy import create_engine

# ------------------------------------------------------------
# 1. DATABASE CONNECTION
# ------------------------------------------------------------
# Fill in your own PostgreSQL password below.
# Format: postgresql+psycopg2://<user>:<password>@<host>:<port>/<database>

DB_USER = "postgres"
DB_PASSWORD = "2004"
DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "weather_analytics"

engine = create_engine(
    f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

# ------------------------------------------------------------
# 2. LOAD CLEANED DATA
# ------------------------------------------------------------

CLEANED_PATH = Path(__file__).resolve().parent.parent / "data" / "processed" / "weather_cleaned.csv"
df = pd.read_csv(CLEANED_PATH, parse_dates=["date"])

print("Loaded cleaned data:", df.shape)

# ------------------------------------------------------------
# 3. BUILD DIM_DATE
# ------------------------------------------------------------

unique_dates = pd.DataFrame({"full_date": df["date"].unique()})
unique_dates["full_date"] = pd.to_datetime(unique_dates["full_date"])

unique_dates["date_id"] = unique_dates["full_date"].dt.strftime("%Y%m%d").astype(int)
unique_dates["day"] = unique_dates["full_date"].dt.day
unique_dates["month"] = unique_dates["full_date"].dt.month
unique_dates["month_name"] = unique_dates["full_date"].dt.month_name()
unique_dates["quarter"] = unique_dates["full_date"].dt.quarter
unique_dates["year"] = unique_dates["full_date"].dt.year
unique_dates["day_name"] = unique_dates["full_date"].dt.day_name()
unique_dates["is_weekend"] = unique_dates["full_date"].dt.dayofweek >= 5

dim_date = unique_dates[
    ["date_id", "full_date", "day", "month", "month_name", "quarter", "year", "day_name", "is_weekend"]
].sort_values("date_id")

print("dim_date rows:", len(dim_date))

# ------------------------------------------------------------
# 4. BUILD DIM_CITY
# ------------------------------------------------------------

dim_city = df[["city", "region", "latitude", "longitude"]].drop_duplicates().reset_index(drop=True)
dim_city = dim_city.rename(columns={"city": "city_name"})

print("dim_city rows:", len(dim_city))

# ------------------------------------------------------------
# 5. LOAD DIM TABLES INTO POSTGRES FIRST
# ------------------------------------------------------------
# We load dims first so we can read back their auto-generated / mapped IDs
# and use them to build the fact table with correct foreign keys.

dim_date.to_sql("dim_date", engine, if_exists="append", index=False)

# dim_city uses SERIAL city_id, so let Postgres generate it, then read it back
dim_city.to_sql("dim_city", engine, if_exists="append", index=False)

# Read back dim_city with the generated city_id so we can map city_name -> city_id
city_lookup = pd.read_sql("SELECT city_id, city_name FROM dim_city", engine)

# ------------------------------------------------------------
# 6. BUILD FACT_WEATHER
# ------------------------------------------------------------

fact = df.copy()
fact["date_id"] = fact["date"].dt.strftime("%Y%m%d").astype(int)

fact = fact.merge(city_lookup, left_on="city", right_on="city_name", how="left")

fact_columns = [
    "date_id", "city_id",
    "temperature_2m_max", "temperature_2m_min", "temperature_2m_mean",
    "apparent_temperature_max", "apparent_temperature_min",
    "precipitation_sum", "rain_sum",
    "windspeed_10m_max", "windgusts_10m_max", "winddirection_10m_dominant",
    "shortwave_radiation_sum", "sunshine_duration", "et0_fao_evapotranspiration",
    "weathercode",
]

fact_weather = fact[fact_columns]

print("fact_weather rows:", len(fact_weather))

# ------------------------------------------------------------
# 7. LOAD FACT TABLE
# ------------------------------------------------------------

fact_weather.to_sql("fact_weather", engine, if_exists="append", index=False)

print("\nAll data loaded successfully into PostgreSQL.")