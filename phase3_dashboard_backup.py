# ============================================================
# Neighborhood Health & Wealth Index — Phase 3: Dashboard
# Geographic Focus: Chicago, IL (Cook County)
# Author: Joshua Mlongecha
# Run with: streamlit run phase3_dashboard.py
# ============================================================

import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import json

# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────

st.set_page_config(
    page_title="Chicago Neighborhood Opportunity Index",
    page_icon="🏙️",
    layout="wide"
)

# ─────────────────────────────────────────────
# LOAD DATA
# ─────────────────────────────────────────────

@st.cache_data
def load_data():
    df = pd.read_csv("data/chicago_opportunity_scores.csv")
    df["GEOID"] = df["GEOID"].astype(str)
    with open("data/chicago_opportunity_scores.geojson") as f:
        geojson = json.load(f)
    return df, geojson

df, geojson = load_data()

# ─────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────

st.title("🏙️ Chicago Neighborhood Opportunity Index")
st.markdown("""
This dashboard scores every census tract in Cook County (Chicago) on a **0–100 Opportunity Scale**
combining economic, health, and housing data from the U.S. Census Bureau and CDC PLACES.
""")

st.divider()

# ─────────────────────────────────────────────
# TOP METRICS ROW
# ─────────────────────────────────────────────

col1, col2, col3, col4, col5 = st.columns(5)

col1.metric("Total Tracts", f"{len(df):,}")
col2.metric("Avg Score", f"{df['opportunity_score'].mean():.1f} / 100")
col3.metric("Very High Opportunity", f"{(df['tier'] == 'Very High').sum():,}")
col4.metric("Low Opportunity", f"{(df['tier'] == 'Low').sum():,}")
col5.metric("Very Low Opportunity", f"{(df['tier'] == 'Very Low').sum():,}")

st.divider()

# ─────────────────────────────────────────────
# SIDEBAR FILTERS
# ─────────────────────────────────────────────

st.sidebar.header("🔍 Filters")

tier_options = ["All"] + list(df["tier"].dropna().unique())
selected_tier = st.sidebar.selectbox("Filter by Tier", tier_options)

score_range = st.sidebar.slider(
    "Opportunity Score Range",
    min_value=0,
    max_value=100,
    value=(0, 100)
)

map_metric = st.sidebar.selectbox(
    "Color Map By",
    ["opportunity_score", "economic_score", "health_score", "housing_score"]
)

# ─────────────────────────────────────────────
# FILTER DATA
# ─────────────────────────────────────────────

filtered = df[
    (df["opportunity_score"] >= score_range[0]) &
    (df["opportunity_score"] <= score_range[1])
]

if selected_tier != "All":
    filtered = filtered[filtered["tier"] == selected_tier]

st.sidebar.markdown(f"**{len(filtered):,} tracts shown**")

# ─────────────────────────────────────────────
# MAP + TABLE LAYOUT
# ─────────────────────────────────────────────

map_col, table_col = st.columns([3, 1])

with map_col:
    st.subheader("🗺️ Opportunity Map")

    # Build Folium map
    m = folium.Map(
        location=[41.85, -87.75],
        zoom_start=10,
        tiles="CartoDB positron"
    )

    # Color scale
    color_scale = {
        "Very High": "#1a9641",
        "High":      "#a6d96a",
        "Moderate":  "#ffffbf",
        "Low":       "#fdae61",
        "Very Low":  "#d7191c",
    }

    # Filter GeoJSON to match filtered tracts
    filtered_geoids = set(filtered["GEOID"].astype(str))
    filtered_geojson = {
        "type": "FeatureCollection",
        "features": [
            f for f in geojson["features"]
            if str(f["properties"].get("GEOID", "")) in filtered_geoids
        ]
    }

    # Merge scores into GeoJSON properties
    score_lookup = df.set_index("GEOID")[
        ["opportunity_score", "economic_score", "health_score",
         "housing_score", "tier", "total_population"]
    ].to_dict("index")

    for feature in filtered_geojson["features"]:
        geoid = str(feature["properties"].get("GEOID", ""))
        if geoid in score_lookup:
            feature["properties"].update(score_lookup[geoid])

    folium.GeoJson(
        filtered_geojson,
        name="Opportunity Score",
        style_function=lambda feature: {
            "fillColor": color_scale.get(
                feature["properties"].get("tier", "Moderate"), "#ffffbf"
            ),
            "color": "white",
            "weight": 0.5,
            "fillOpacity": 0.75,
        },
        tooltip=folium.GeoJsonTooltip(
            fields=["GEOID", "opportunity_score", "economic_score",
                    "health_score", "housing_score", "tier"],
            aliases=["Tract ID", "Opportunity Score", "Economic Score",
                     "Health Score", "Housing Score", "Tier"],
            localize=True,
            sticky=True
        )
    ).add_to(m)

    # Legend
    legend_html = """
    <div style="position: fixed; bottom: 30px; left: 30px; z-index: 1000;
                background-color: white; padding: 12px; border-radius: 8px;
                border: 1px solid #ccc; font-size: 13px;">
        <b>Opportunity Tier</b><br>
        <span style="color:#1a9641">■</span> Very High (80–100)<br>
        <span style="color:#a6d96a">■</span> High (65–80)<br>
        <span style="color:#ffffbf; background:#ffffbf">■</span>
        <span style="color:#999"> Moderate (45–65)</span><br>
        <span style="color:#fdae61">■</span> Low (25–45)<br>
        <span style="color:#d7191c">■</span> Very Low (0–25)
    </div>
    """
    m.get_root().html.add_child(folium.Element(legend_html))

    st_folium(m, width=900, height=550)

with table_col:
    st.subheader("📊 Top & Bottom Tracts")

    st.markdown("**🟢 Highest Scoring**")
    top = filtered.nlargest(5, "opportunity_score")[
        ["GEOID", "opportunity_score", "tier"]
    ].reset_index(drop=True)
    top.columns = ["Tract", "Score", "Tier"]
    st.dataframe(top, use_container_width=True, hide_index=True)

    st.markdown("**🔴 Lowest Scoring**")
    bottom = filtered.nsmallest(5, "opportunity_score")[
        ["GEOID", "opportunity_score", "tier"]
    ].reset_index(drop=True)
    bottom.columns = ["Tract", "Score", "Tier"]
    st.dataframe(bottom, use_container_width=True, hide_index=True)

# ─────────────────────────────────────────────
# SCORE DISTRIBUTION CHART
# ─────────────────────────────────────────────

st.divider()
st.subheader("📈 Score Distribution")

chart_col1, chart_col2 = st.columns(2)

with chart_col1:
    tier_counts = filtered["tier"].value_counts().reset_index()
    tier_counts.columns = ["Tier", "Count"]
    tier_order = ["Very Low", "Low", "Moderate", "High", "Very High"]
    tier_counts["Tier"] = pd.Categorical(
        tier_counts["Tier"], categories=tier_order, ordered=True
    )
    tier_counts = tier_counts.sort_values("Tier")
    st.bar_chart(tier_counts.set_index("Tier"))

with chart_col2:
    st.markdown("**Score Breakdown by Component**")
    avg_scores = pd.DataFrame({
        "Component": ["Economic", "Health", "Housing", "Overall"],
        "Avg Score": [
            filtered["economic_score"].mean(),
            filtered["health_score"].mean(),
            filtered["housing_score"].mean(),
            filtered["opportunity_score"].mean(),
        ]
    }).set_index("Component")
    st.bar_chart(avg_scores)

# ─────────────────────────────────────────────
# RAW DATA TABLE
# ─────────────────────────────────────────────

st.divider()
with st.expander("📋 View Raw Data"):
    st.dataframe(
        filtered.sort_values("opportunity_score", ascending=False),
        use_container_width=True,
        hide_index=True
    )
    st.download_button(
        "⬇️ Download CSV",
        data=filtered.to_csv(index=False),
        file_name="chicago_opportunity_scores_filtered.csv",
        mime="text/csv"
    )

# ─────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────

st.divider()
st.markdown("""
<div style='text-align: center; color: gray; font-size: 12px;'>
    Data Sources: U.S. Census Bureau ACS 5-Year (2022) • CDC PLACES (2023) • TIGER/Line Shapefiles<br>
    Built by Joshua Mlongecha | University of Connecticut
</div>
""", unsafe_allow_html=True)
