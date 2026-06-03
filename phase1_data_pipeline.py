# ============================================================
# Neighborhood Health & Wealth Index — Phase 1: Data Pipeline
# Geographic Focus: Chicago, IL (Cook County)
# Author: Joshua Mlongecha
# ============================================================

import requests
import pandas as pd
import geopandas as gpd
import os

# ─────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────
CENSUS_API_KEY = "fa51595e4d58498eb8f33d906cca7e418f4c72c8"
STATE_FIPS = "17"       # Illinois
COUNTY_FIPS = "031"     # Cook County (Chicago)

OUTPUT_DIR = "data"
os.makedirs(OUTPUT_DIR, exist_ok=True)


# ─────────────────────────────────────────────
# 1. CENSUS ACS 5-Year Data (2022)
# ─────────────────────────────────────────────

ACS_VARIABLES = {
    "B19013_001E": "median_household_income",
    "B17001_002E": "population_below_poverty",
    "B17001_001E": "population_for_poverty_calc",
    "B23025_005E": "unemployed",
    "B23025_002E": "labor_force",
    "B15003_022E": "bachelors_degree",
    "B15003_023E": "masters_degree",
    "B15003_024E": "professional_degree",
    "B15003_025E": "doctorate_degree",
    "B15003_001E": "population_25_plus",
    "B25077_001E": "median_home_value",
    "B25003_003E": "renter_occupied",
    "B25003_001E": "total_occupied_units",
    "B01003_001E": "total_population",
}

def fetch_census_data():
    print("📡 Fetching Census ACS data for Cook County tracts...")

    var_string = ",".join(ACS_VARIABLES.keys())
    url = (
        f"https://api.census.gov/data/2022/acs/acs5"
        f"?get=NAME,{var_string}"
        f"&for=tract:*"
        f"&in=state:{STATE_FIPS}+county:{COUNTY_FIPS}"
        f"&key={CENSUS_API_KEY}"
    )

    response = requests.get(url)
    response.raise_for_status()

    if not response.text.strip():
        raise ValueError("Empty response from Census API")

    data = response.json()
    df = pd.DataFrame(data[1:], columns=data[0])
    df = df.rename(columns=ACS_VARIABLES)
    df["GEOID"] = df["state"] + df["county"] + df["tract"]

    numeric_cols = list(ACS_VARIABLES.values())
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df["poverty_rate"] = df["population_below_poverty"] / df["population_for_poverty_calc"]
    df["unemployment_rate"] = df["unemployed"] / df["labor_force"]
    df["college_rate"] = (
        df["bachelors_degree"] + df["masters_degree"] +
        df["professional_degree"] + df["doctorate_degree"]
    ) / df["population_25_plus"]
    df["renter_rate"] = df["renter_occupied"] / df["total_occupied_units"]

    df = df.drop(columns=[
        "population_below_poverty", "population_for_poverty_calc",
        "unemployed", "labor_force",
        "bachelors_degree", "masters_degree", "professional_degree", "doctorate_degree",
        "population_25_plus", "renter_occupied", "total_occupied_units",
        "state", "county", "tract", "NAME"
    ])

    print(f"   ✅ Census: {len(df)} tracts loaded")
    return df


# ─────────────────────────────────────────────
# 2. CDC PLACES Data (from local CSV)
# ─────────────────────────────────────────────

def fetch_cdc_places():
    print("📡 Loading CDC PLACES health data from local file...")

    df = pd.read_csv("data/cdc_places_cook.csv")

    # Filter to Cook County, Illinois, census tract level (11-digit LocationID)
    df = df[
        (df["StateAbbr"] == "IL") &
        (df["CountyName"] == "Cook") &
        (df["LocationID"].astype(str).str.len() == 11)
    ]

    # Keep only the measures we need
    measures = {
        "DIABETES": "diabetes_pct",
        "OBESITY": "obesity_pct",
        "MHLTH": "poor_mental_health_pct",
        "LPA": "physical_inactivity_pct",
        "ACCESS2": "uninsured_pct",
    }

    df = df[df["MeasureId"].isin(measures.keys())]

    # Pivot so each measure becomes a column
    df_pivot = df.pivot_table(
        index="LocationID",
        columns="MeasureId",
        values="Data_Value"
    ).reset_index()

    df_pivot.columns.name = None
    df_pivot = df_pivot.rename(columns={"LocationID": "GEOID"})
    df_pivot = df_pivot.rename(columns=measures)

    df_pivot["GEOID"] = df_pivot["GEOID"].astype(str)

    for col in measures.values():
        if col in df_pivot.columns:
            df_pivot[col] = pd.to_numeric(df_pivot[col], errors="coerce") / 100

    print(f"   ✅ CDC PLACES: {len(df_pivot)} tracts loaded")
    return df_pivot


# ─────────────────────────────────────────────
# 3. Census TIGER Shapefile (Cook County tracts)
# ─────────────────────────────────────────────

def fetch_shapefile():
    print("📡 Fetching Cook County census tract shapefile...")

    url = (
        "https://www2.census.gov/geo/tiger/TIGER2022/TRACT/"
        "tl_2022_17_tract.zip"
    )

    gdf = gpd.read_file(url)
    gdf = gdf[gdf["COUNTYFP"] == COUNTY_FIPS].copy()
    gdf = gdf[["GEOID", "geometry"]]

    print(f"   ✅ Shapefile: {len(gdf)} tracts loaded")
    return gdf


# ─────────────────────────────────────────────
# 4. MERGE & SAVE
# ─────────────────────────────────────────────

def build_master_dataset():
    census_df = fetch_census_data()
    cdc_df = fetch_cdc_places()
    shapefile_gdf = fetch_shapefile()

    print("\n🔗 Merging datasets...")

    merged = pd.merge(census_df, cdc_df, on="GEOID", how="inner")
    final_gdf = shapefile_gdf.merge(merged, on="GEOID", how="inner")

    final_gdf = final_gdf[final_gdf.isnull().mean(axis=1) < 0.5]

    print(f"   ✅ Final dataset: {len(final_gdf)} tracts after cleaning")

    csv_path = os.path.join(OUTPUT_DIR, "chicago_tracts_raw.csv")
    geojson_path = os.path.join(OUTPUT_DIR, "chicago_tracts_raw.geojson")

    final_gdf.drop(columns="geometry").to_csv(csv_path, index=False)
    final_gdf.to_file(geojson_path, driver="GeoJSON")

    print(f"\n💾 Saved to:")
    print(f"   {csv_path}")
    print(f"   {geojson_path}")
    print("\n✅ Phase 1 complete! Ready for Phase 2 (Index Scoring).")

    return final_gdf


# ─────────────────────────────────────────────
# 5. SUMMARY
# ─────────────────────────────────────────────

def summarize(gdf):
    df = gdf.drop(columns="geometry")
    print("\n📊 Dataset Summary:")
    print(f"   Tracts: {len(df)}")
    print(f"   Columns: {list(df.columns)}")
    print("\n   Null counts:")
    print(df.isnull().sum().to_string())
    print("\n   Sample rows:")
    print(df.head(3).to_string())


# ─────────────────────────────────────────────
# RUN
# ─────────────────────────────────────────────

if __name__ == "__main__":
    gdf = build_master_dataset()
    summarize(gdf)
