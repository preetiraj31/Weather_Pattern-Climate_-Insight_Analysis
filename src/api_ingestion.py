"""
api_ingestion.py

Reusable Open-Meteo historical weather data ingestion script.
Fetches daily weather data for multiple cities and saves raw + lightly
processed CSVs for downstream cleaning (see data_cleaning.py).

Usage:
    python api_ingestion.py

To add/remove a city, just edit the CITIES dictionary below.
"""

import time
import requests
import pandas as pd
from datetime import date, timedelta
from pathlib import Path

# ---------------------------------------------------------------------------
# 1. CONFIGURATION
# ---------------------------------------------------------------------------

# City name -> (latitude, longitude, state/region)
# Add or remove cities here without touching any other code.
CITIES = {
    "Delhi": (28.6139, 77.2090, "Delhi"),
    "Mumbai": (19.0760, 72.8777, "Maharashtra"),
    "Bengaluru": (12.9716, 77.5946, "Karnataka"),
    "Chennai": (13.0827, 80.2707, "Tamil Nadu"),
    "Kolkata": (22.5726, 88.3639, "West Bengal"),
    "Hyderabad": (17.3850, 78.4867, "Telangana"),
    "Chandigarh": (30.7333, 76.7794, "Chandigarh"),
    "Jaipur": (26.9124, 75.7873, "Rajasthan"),
    "Pune": (18.5204, 73.8567, "Maharashtra"),
}

# Date range: last N years up to yesterday (archive API doesn't include today)
YEARS_OF_HISTORY = 3
END_DATE = date.today() - timedelta(days=1)
START_DATE = END_DATE.replace(year=END_DATE.year - YEARS_OF_HISTORY)

# Daily variables we want from the API
DAILY_VARS = [
    "temperature_2m_max",
    "temperature_2m_min",
    "temperature_2m_mean",
    "apparent_temperature_max",
    "apparent_temperature_min",
    "precipitation_sum",
    "rain_sum",
    "windspeed_10m_max",
    "windgusts_10m_max",
    "winddirection_10m_dominant",
    "shortwave_radiation_sum",
    "sunshine_duration",
    "et0_fao_evapotranspiration",
    "weathercode",
]

BASE_URL = "https://archive-api.open-meteo.com/v1/archive"

RAW_DIR = Path(__file__).resolve().parent.parent / "data" / "raw"
PROCESSED_DIR = Path(__file__).resolve().parent.parent / "data" / "processed"
RAW_DIR.mkdir(parents=True, exist_ok=True)
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------------------------------
# 2. FETCH FUNCTION (single city, with error handling + 1 retry)
# ---------------------------------------------------------------------------

def fetch_city_weather(city_name: str, lat: float, lon: float, retries: int = 1) -> pd.DataFrame | None:
    """
    Calls the Open-Meteo Archive API for one city and returns a DataFrame.
    Returns None if the call fails after retries (caller decides how to handle it).
    """
    params = {
        "latitude": lat,
        "longitude": lon,
        "start_date": START_DATE.isoformat(),
        "end_date": END_DATE.isoformat(),
        "daily": ",".join(DAILY_VARS),
        "timezone": "auto",
    }

    attempt = 0
    while attempt <= retries:
        try:
            response = requests.get(BASE_URL, params=params, timeout=30)
            response.raise_for_status()
            payload = response.json()

            if "daily" not in payload:
                print(f"[WARN] {city_name}: no 'daily' block in response, skipping.")
                return None

            df = pd.DataFrame(payload["daily"])
            df["city"] = city_name
            df["latitude"] = lat
            df["longitude"] = lon
            return df

        except requests.exceptions.RequestException as e:
            attempt += 1
            print(f"[ERROR] {city_name}: attempt {attempt} failed ({e})")
            if attempt <= retries:
                time.sleep(2)  # brief backoff before retry
            else:
                print(f"[FAILED] {city_name}: giving up after {retries + 1} attempts.")
                return None


# ---------------------------------------------------------------------------
# 3. ORCHESTRATION — loop over all cities, combine, save
# ---------------------------------------------------------------------------

def collect_all_cities() -> pd.DataFrame:
    all_frames = []
    failed_cities = []

    for city_name, (lat, lon, region) in CITIES.items():
        print(f"Fetching: {city_name} ({START_DATE} to {END_DATE}) ...")
        df = fetch_city_weather(city_name, lat, lon)

        if df is None:
            failed_cities.append(city_name)
            continue

        df["region"] = region
        all_frames.append(df)

        # Save per-city raw file too, useful for debugging individual cities
        raw_path = RAW_DIR / f"{city_name.lower()}_raw.csv"
        df.to_csv(raw_path, index=False)

        time.sleep(1)  # be polite to the free API — avoid hammering it

    if not all_frames:
        raise RuntimeError("No city data was successfully collected. Check network/API status.")

    combined = pd.concat(all_frames, ignore_index=True)

    if failed_cities:
        print(f"\n[SUMMARY] Failed to fetch: {failed_cities}")
    print(f"[SUMMARY] Successfully fetched {len(CITIES) - len(failed_cities)}/{len(CITIES)} cities, "
          f"{len(combined)} total rows.")

    return combined


def basic_dtype_fix(df: pd.DataFrame) -> pd.DataFrame:
    """
    Light-touch processing only — NOT full cleaning (that's Phase 3).
    Just makes sure date is a proper datetime and columns are sensibly typed
    so the raw-combined file is usable for a quick sanity check.
    """
    df["time"] = pd.to_datetime(df["time"])
    df = df.rename(columns={"time": "date"})
    numeric_cols = [c for c in DAILY_VARS if c in df.columns and c != "weathercode"]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    return df


# ---------------------------------------------------------------------------
# 4. MAIN
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    combined_df = collect_all_cities()
    combined_df = basic_dtype_fix(combined_df)

    processed_path = PROCESSED_DIR / "weather_combined_raw.csv"
    combined_df.to_csv(processed_path, index=False)

    print(f"\nSaved combined dataset -> {processed_path}")
    print(f"Shape: {combined_df.shape}")
    print(combined_df.head())