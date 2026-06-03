# 🏙️ Chicago Neighborhood Opportunity Index

> A data-driven composite index scoring 1,328 census tracts across Cook County (Chicago) on economic strength, health outcomes, and housing stability.

**Built by:** Joshua Mlongecha | University of Connecticut, B.S. Data Science 2028  
**Stack:** Python · Pandas · GeoPandas · Scikit-learn · Streamlit · Folium  
**Data:** U.S. Census ACS 5-Year (2022) · CDC PLACES (2023) · Census TIGER Shapefiles

---

## 📌 Project Overview

This project builds a **Neighborhood Opportunity Index** from scratch — pulling raw government data, engineering a composite scoring system, training a machine learning risk model, and deploying an interactive dashboard.

The index scores every census tract in Cook County across 12 socioeconomic and health variables, then uses a Random Forest model to classify neighborhoods as **Stable** or **At Risk**.

**Key findings:**
- 251 of 1,328 tracts (19%) classified as At Risk
- Median household income and obesity rate are the strongest predictors of neighborhood risk
- Health outcomes and economic indicators are nearly equally predictive — suggesting wealth and health are deeply linked at the neighborhood level

---

## 🗂️ Project Structure

```
Neighborhood Health + Wealth Index/
│
├── data/
│   ├── chicago_tracts_raw.csv              # Merged Census + CDC data
│   ├── chicago_tracts_raw.geojson          # Geo data for mapping
│   ├── chicago_opportunity_scores.csv      # Composite index scores
│   ├── chicago_opportunity_scores.geojson  # Scored geo data
│   ├── chicago_risk_predictions.csv        # ML model predictions
│   └── cdc_places_cook.csv                 # Raw CDC PLACES data
│
├── plots/
│   └── model_results.png                   # ML model evaluation charts
│
├── .streamlit/
│   └── config.toml                         # Dashboard theme config
│
├── phase1_data_pipeline.py                 # Data collection & cleaning
├── phase2_index_scoring.py                 # Composite index construction
├── phase3_dashboard.py                     # Interactive Streamlit dashboard
├── phase4_ml_model.py                      # ML risk classification model
└── README.md
```

---

## 🔄 How to Reproduce

### 1. Clone the repo
```bash
git clone https://github.com/YOUR_USERNAME/chicago-opportunity-index.git
cd chicago-opportunity-index
```

### 2. Install dependencies
```bash
pip install requests pandas geopandas scikit-learn matplotlib seaborn streamlit folium streamlit-folium
```

### 3. Add your Census API key
Get a free key at [census.gov/developers](https://api.census.gov/data/key_signup.html).  
Open `phase1_data_pipeline.py` and replace:
```python
CENSUS_API_KEY = "your_key_here"
```

### 4. Download CDC PLACES data
```bash
mkdir data
curl -o data/cdc_places_cook.csv "https://chronicdata.cdc.gov/api/views/cwsq-ngmh/rows.csv?accessType=DOWNLOAD"
```

### 5. Run the pipeline
```bash
python3 phase1_data_pipeline.py    # Pull & merge data
python3 phase2_index_scoring.py    # Build composite index
python3 phase4_ml_model.py         # Train ML model
streamlit run phase3_dashboard.py  # Launch dashboard
```

---

## 📊 Data Sources

| Source | Description | Geography |
|--------|-------------|-----------|
| U.S. Census ACS 5-Year (2022) | Income, poverty, unemployment, education, housing | Census tract |
| CDC PLACES (2023) | Diabetes, obesity, mental health, physical inactivity, uninsured rate | Census tract |
| Census TIGER/Line Shapefiles | Geographic boundaries for mapping | Census tract |

---

## 🧮 Index Methodology

The Opportunity Index is a **weighted composite score (0–100)** built from 12 variables across three domains:

| Domain | Variables | Weight |
|--------|-----------|--------|
| **Economic** (50%) | Median income, poverty rate, unemployment, education, home values | 50% |
| **Health** (35%) | Diabetes, obesity, mental health, physical inactivity, uninsured | 35% |
| **Housing** (15%) | Renter rate, population density | 15% |

Each variable is min-max normalized to 0–1. Variables where higher = worse (e.g. poverty rate) are inverted before weighting.

**Opportunity Tiers:**
- 🟢 Very High: 80–100
- 🟢 High: 65–80
- 🟡 Moderate: 45–65
- 🟠 Low: 25–45
- 🔴 Very Low: 0–25

---

## 🤖 Machine Learning Model

A **Random Forest classifier** (200 estimators) predicts neighborhood risk using all 12 socioeconomic and health features.

**Results:**
| Model | AUC | CV AUC |
|-------|-----|--------|
| Random Forest | 0.993 | 0.996 |
| Gradient Boosting | 0.997 | 0.997 |
| Logistic Regression | 1.000 | 1.000 |

**Top predictive features:**
1. Median household income (19.6%)
2. Obesity rate (18.7%)
3. Poor mental health rate (18.6%)
4. Diabetes rate (13.7%)

> **Note:** The high AUC scores reflect that the features used to predict risk are closely related to the composite index itself. In a production setting, this model would be retrained on lagged data to predict future risk.

---

## 🗺️ Dashboard Features

- Interactive choropleth map of all 1,328 Cook County census tracts
- Color-coded by opportunity tier with hover tooltips
- Filter by tier and score range
- Analytics tab with score distribution charts
- Sortable data table with CSV export
- Dark professional theme

---

## 📬 Contact

**Joshua Mlongecha**  
University of Connecticut · B.S. Data Science, Class of 2028  
📧 jomlongecha@gmail.com

---

*Data is for portfolio and research purposes only. All sources are publicly available U.S. government datasets.*
