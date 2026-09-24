# 🌦️ Weather Pattern Analysis & Climate Insights Dashboard

> Analyzing 3 Years of Climate Trends Across 9 Major Indian Cities

An end-to-end data analytics project: real historical weather data is pulled from an API, cleaned with Python, modeled in a PostgreSQL star schema, and visualized in an interactive Power BI dashboard.

---

## 📌 Business Problem

Weather directly affects agriculture, energy demand, logistics, tourism and urban planning. This project answers questions such as:

- Which cities are the hottest / coolest, and by how much?
- Which cities receive the most rainfall?
- How do temperature and precipitation change over time (month-on-month, year-on-year)?
- How do seasonal patterns differ across regions?

---

## 🗂️ Data Source

| Item | Details |
|------|---------|
| **API** | [Open-Meteo Historical Weather API](https://open-meteo.com/) |
| **Data type** | Real historical daily data (no mock/synthetic data) |
| **Cities (9)** | Delhi, Mumbai, Bengaluru, Chennai, Kolkata, Hyderabad, Chandigarh, Jaipur, Pune |
| **Time period** | 2023-09-11 to 2026-09-11 (3 years) |
| **Volume** | 9,873 rows × 19 columns (1,097 days per city) |

Data was extracted with `src/api_ingestion.py`, a config-driven script (`CITIES` dictionary), so adding or removing a city is easy.

---

## 🛠️ Tech Stack

- **Python** (pandas, requests, SQLAlchemy): ingestion, cleaning, ETL
- **PostgreSQL**: data warehouse (star schema), managed via pgAdmin
- **Power BI Desktop**: data modeling, DAX, dashboard
- **Git & GitHub**: version control

---

## 🏗️ Project Architecture

```
Open-Meteo API → Raw Data (CSV) → Python Cleaning → PostgreSQL (Star Schema) → Power BI (Model + DAX) → Dashboard & Insights
```
