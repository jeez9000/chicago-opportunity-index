# ============================================================
# Neighborhood Health & Wealth Index — Phase 2: Index Scoring
# Geographic Focus: Chicago, IL (Cook County)
# Author: Joshua Mlongecha
# ============================================================

import pandas as pd
import numpy as np
import geopandas as gpd
import os

INPUT_CSV = "data/chicago_tracts_raw.csv"
INPUT_GEOJSON = "data/chicago_tracts_raw.geojson"
OUTPUT_DIR = "data"

# ─────────────────────────────────────────────
# WEIGHTS
# These determine how much each variable
# contributes to the final score (must sum to 1)
# ─────────────────────────────────────────────

WEIGHTS = {
    # Economic (50%)
    "median_household_income":  0.15,
    "poverty_rate":             0.12,
    "unemployment_rate":        0.10,
    "college_rate":             0.08,
    "median_home_value":        0.05,

    # Health (35%)
    "diabetes_pct":             0.10,
    "obesity_pct":              0.08,
    "poor_mental_health_pct":   0.07,
    "physical_inactivity_pct":  0.05,
    "uninsured_pct":            0.05,

    # Housing (15%)
    "renter_rate":              0.08,
    "total_population":         0.07,
}

# Variables where HIGHER = WORSE (will be flipped)
INVERT = {
    "poverty_rate",
    "unemployment_rate",
    "diabetes_pct",
    "obesity_pct",
    "poor_mental_health_pct",
    "physical_inactivity_pct",
    "uninsured_pct",
    "renter_rate",
}


# ─────────────────────────────────────────────
# 1. LOAD DATA
# ─────────────────────────────────────────────

def load_data():
    print("📂 Loading cleaned dataset...")
    df = pd.read_csv(INPUT_CSV)

    # Fix negative home values (census uses -666666666 for missing)
    df["median_home_value"] = df["median_home_value"].replace(-666666666, np.nan)

    # Fill remaining nulls with column median
    for col in WEIGHTS.keys():
        if col in df.columns:
            df[col] = df[col].fillna(df[col].median())

    print(f"   ✅ Loaded {len(df)} tracts")
    return df


# ─────────────────────────────────────────────
# 2. NORMALIZE (min-max scaling to 0–1)
# ─────────────────────────────────────────────

def normalize(df):
    print("📐 Normalizing variables...")
    df_norm = df.copy()

    for col in WEIGHTS.keys():
        min_val = df[col].min()
        max_val = df[col].max()

        if max_val == min_val:
            df_norm[col] = 0.5
        else:
            df_norm[col] = (df[col] - min_val) / (max_val - min_val)

        # Flip inverted variables so higher = better
        if col in INVERT:
            df_norm[col] = 1 - df_norm[col]

    print("   ✅ Normalization complete")
    return df_norm


# ─────────────────────────────────────────────
# 3. COMPUTE COMPOSITE SCORE
# ─────────────────────────────────────────────

def compute_score(df_norm, df_original):
    print("🧮 Computing composite index scores...")

    score = pd.Series(0.0, index=df_norm.index)
    for col, weight in WEIGHTS.items():
        score += df_norm[col] * weight

    # Scale to 0–100
    score = score * 100

    result = df_original[["GEOID", "total_population"]].copy()
    result["opportunity_score"] = score.round(2)

    # Add sub-scores for transparency
    econ_cols = ["median_household_income", "poverty_rate", "unemployment_rate",
                 "college_rate", "median_home_value"]
    health_cols = ["diabetes_pct", "obesity_pct", "poor_mental_health_pct",
                   "physical_inactivity_pct", "uninsured_pct"]
    housing_cols = ["renter_rate", "total_population"]

    def sub_score(cols):
        total_weight = sum(WEIGHTS[c] for c in cols)
        s = pd.Series(0.0, index=df_norm.index)
        for c in cols:
            s += df_norm[c] * WEIGHTS[c]
        return (s / total_weight * 100).round(2)

    result["economic_score"] = sub_score(econ_cols)
    result["health_score"] = sub_score(health_cols)
    result["housing_score"] = sub_score(housing_cols)

    # Add tier labels
    result["tier"] = pd.cut(
        result["opportunity_score"],
        bins=[0, 25, 45, 65, 80, 100],
        labels=["Very Low", "Low", "Moderate", "High", "Very High"]
    )

    print(f"   ✅ Scores computed")
    print(f"\n   Score distribution:")
    print(result["tier"].value_counts().sort_index().to_string())
    print(f"\n   Overall score stats:")
    print(result["opportunity_score"].describe().round(2).to_string())

    return result


# ─────────────────────────────────────────────
# 4. MERGE WITH GEODATA & SAVE
# ─────────────────────────────────────────────

def save_results(result_df):
    print("\n💾 Merging with shapefile and saving...")

    gdf = gpd.read_file(INPUT_GEOJSON)
    gdf["GEOID"] = gdf["GEOID"].astype(str)
    result_df["GEOID"] = result_df["GEOID"].astype(str)
    scored_gdf = gdf.merge(result_df, on="GEOID", how="inner")

    csv_path = os.path.join(OUTPUT_DIR, "chicago_opportunity_scores.csv")
    geojson_path = os.path.join(OUTPUT_DIR, "chicago_opportunity_scores.geojson")

    result_df.to_csv(csv_path, index=False)
    scored_gdf.to_file(geojson_path, driver="GeoJSON")

    print(f"   ✅ Saved:")
    print(f"   {csv_path}")
    print(f"   {geojson_path}")
    print("\n✅ Phase 2 complete! Ready for Phase 3 (Dashboard).")

    return scored_gdf


# ─────────────────────────────────────────────
# RUN
# ─────────────────────────────────────────────

if __name__ == "__main__":
    df = load_data()
    df_norm = normalize(df)
    result_df = compute_score(df_norm, df)
    scored_gdf = save_results(result_df)