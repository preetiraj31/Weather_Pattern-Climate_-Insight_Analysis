import pandas as pd
from pathlib import Path

# ------------------------------------------------------------
# 1. LOAD DATA
# ------------------------------------------------------------

RAW_PATH = Path(__file__).resolve().parent.parent / "data" / "processed" / "weather_combined_raw.csv"

df = pd.read_csv(RAW_PATH)

# ------------------------------------------------------------
# 2. FIRST LOOK AT THE DATA
# ------------------------------------------------------------

print("Shape:", df.shape)
print("\nColumn names:\n", df.columns.tolist())
print("\nData types:\n", df.dtypes)
print("\nFirst 5 rows:\n", df.head())
print("\nMissing values per column:\n", df.isnull().sum())
print("\nDuplicate rows:", df.duplicated().sum())

# ------------------------------------------------------------
# 3. DATE COLUMN FIX
# ------------------------------------------------------------
# 'date' currently comes in as string -> convert to real datetime
# so we can do time-series operations (month, year, resampling) later.

df["date"] = pd.to_datetime(df["date"])
print("\ndate dtype after conversion:", df["date"].dtype)

# ------------------------------------------------------------
# 4. PER-CITY CONSISTENCY CHECK
# ------------------------------------------------------------
# Make sure every city has the same date range and same row count.
# If one city has fewer rows, it means some days are missing for it.

print("\nRows per city:\n", df.groupby("city")["date"].count())
print("\nDate range per city:\n", df.groupby("city")["date"].agg(["min", "max"]))

# ------------------------------------------------------------
# 5. OUTLIER / SANITY CHECK
# ------------------------------------------------------------
# Basic real-world range checks for weather values.
# Anything outside these ranges is very likely a bad reading, not real weather.

sanity_checks = {
    "temperature_2m_max": (-10, 55),
    "temperature_2m_min": (-10, 45),
    "precipitation_sum": (0, 500),
    "windspeed_10m_max": (0, 200),
}

for col, (low, high) in sanity_checks.items():
    bad_rows = df[(df[col] < low) | (df[col] > high)]
    print(f"\n{col}: {len(bad_rows)} rows outside expected range ({low} to {high})")

# ------------------------------------------------------------
# 6. SAVE CLEANED DATA
# ------------------------------------------------------------

CLEANED_PATH = RAW_PATH.parent / "weather_cleaned.csv"
df.to_csv(CLEANED_PATH, index=False)
print(f"\nCleaned data saved to: {CLEANED_PATH}")
print("Final shape:", df.shape)