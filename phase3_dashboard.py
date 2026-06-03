# ============================================================
# Chicago Neighborhood Opportunity Index — Professional Dashboard
# Author: Joshua Mlongecha | University of Connecticut
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
    page_title="Chicago Opportunity Index",
    page_icon="🏙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─────────────────────────────────────────────
# PROFESSIONAL CSS
# ─────────────────────────────────────────────

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

/* ── Global ── */
html, body, [class*="css"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
}
.stApp {
    background-color: #0a0e1a !important;
    color: #ffffff !important;
}

/* ── Hide Streamlit chrome ── */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding-top: 0 !important; padding-bottom: 2rem; max-width: 100% !important; }

/* ── Top nav bar ── */
.topbar {
    background: linear-gradient(90deg, #0a2342 0%, #1a3a5c 60%, #1e4976 100%);
    padding: 14px 40px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin: -1rem -1rem 2rem -1rem;
    border-bottom: 3px solid #2e86c1;
}
.topbar-title {
    color: #ffffff;
    font-size: 17px;
    font-weight: 700;
    letter-spacing: 0.3px;
}
.topbar-sub {
    color: #7fb3d3;
    font-size: 12px;
    font-weight: 400;
    margin-top: 2px;
}
.topbar-badge {
    background: rgba(255,255,255,0.1);
    border: 1px solid rgba(255,255,255,0.2);
    color: #a8d4f0;
    font-size: 11px;
    font-weight: 600;
    padding: 4px 12px;
    border-radius: 20px;
    margin-left: 8px;
}

/* ── Section headers ── */
.section-title {
    font-size: 15px;
    font-weight: 700;
    color: #ffffff;
    text-transform: uppercase;
    letter-spacing: 0.8px;
    margin-bottom: 14px;
    padding-bottom: 8px;
    border-bottom: 2px solid #e2e8f0;
}

/* ── Metric cards ── */
.metric-card {
    background: #ffffff;
    border-radius: 12px;
    padding: 20px 24px;
    border: 1px solid #e2e8f0;
    box-shadow: 0 1px 3px rgba(0,0,0,0.06), 0 4px 16px rgba(0,0,0,0.04);
    height: 100%;
}
.metric-label {
    font-size: 11px;
    font-weight: 600;
    color: #64748b;
    text-transform: uppercase;
    letter-spacing: 0.8px;
    margin-bottom: 8px;
}
.metric-value {
    font-size: 32px;
    font-weight: 800;
    color: #0a2342;
    line-height: 1;
    margin-bottom: 6px;
}
.metric-delta-pos {
    font-size: 12px;
    font-weight: 600;
    color: #16a34a;
}
.metric-delta-neg {
    font-size: 12px;
    font-weight: 600;
    color: #dc2626;
}
.metric-accent {
    width: 36px;
    height: 4px;
    border-radius: 2px;
    margin-top: 12px;
}

/* ── Content cards ── */
.content-card {
    background: #ffffff;
    border-radius: 12px;
    padding: 24px;
    border: 1px solid #e2e8f0;
    box-shadow: 0 1px 3px rgba(0,0,0,0.06);
    margin-bottom: 16px;
}

/* ── Tier pills ── */
.pill {
    display: inline-block;
    padding: 3px 10px;
    border-radius: 20px;
    font-size: 11px;
    font-weight: 600;
}
.pill-vh { background: #dcfce7; color: #16a34a; }
.pill-h  { background: #d1fae5; color: #059669; }
.pill-m  { background: #fef9c3; color: #ca8a04; }
.pill-l  { background: #ffedd5; color: #ea580c; }
.pill-vl { background: #fee2e2; color: #dc2626; }

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background-color: #111827 !important;
    border-right: 1px solid #e2e8f0 !important;
}
[data-testid="stSidebar"] .stMarkdown h2,
[data-testid="stSidebar"] .stMarkdown h3 {
    color: #0a2342 !important;
}
.sidebar-section {
    background: #f8fafc;
    border-radius: 10px;
    padding: 14px 16px;
    margin-bottom: 12px;
    border: 1px solid #e2e8f0;
}
.sidebar-label {
    font-size: 10px;
    font-weight: 700;
    color: #64748b;
    text-transform: uppercase;
    letter-spacing: 0.8px;
    margin-bottom: 6px;
}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
    background: #ffffff;
    border-radius: 10px;
    padding: 4px;
    border: 1px solid #e2e8f0;
    gap: 4px;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 8px;
    font-weight: 600;
    font-size: 13px;
    color: #64748b;
    padding: 8px 20px;
}
.stTabs [aria-selected="true"] {
    background: #0a2342 !important;
    color: #ffffff !important;
}

/* ── Buttons ── */
.stDownloadButton button {
    background: #0a2342 !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    font-size: 13px !important;
    padding: 10px 20px !important;
}
.stDownloadButton button:hover {
    background: #1a3a5c !important;
}

/* ── Footer ── */
.footer {
    text-align: center;
    color: #94a3b8;
    font-size: 12px;
    margin-top: 40px;
    padding: 20px 0;
    border-top: 1px solid #e2e8f0;
}

/* ── Selectbox / slider ── */
.stSelectbox > div > div,
.stSlider > div { border-radius: 8px !important; }

/* ── Dataframe ── */
[data-testid="stDataFrame"] { border-radius: 10px !important; overflow: hidden; }
</style>
""", unsafe_allow_html=True)

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
# TOP NAV BAR
# ─────────────────────────────────────────────

st.markdown("""
<div class="topbar">
    <div>
        <div class="topbar-title">🏙️ Chicago Neighborhood Opportunity Index</div>
        <div class="topbar-sub">Cook County · 1,328 Census Tracts · ACS 2022 + CDC PLACES 2023</div>
    </div>
    <div>
        <span class="topbar-badge">📊 Data Science</span>
        <span class="topbar-badge">🏠 Real Estate</span>
        <span class="topbar-badge">🏥 Public Health</span>
    </div>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────

with st.sidebar:
    st.markdown("### 🔍 Dashboard Controls")
    st.markdown("---")

    st.markdown('<div class="sidebar-label">Filter by Tier</div>', unsafe_allow_html=True)
    selected_tier = st.selectbox(
        "", ["All", "Very High", "High", "Moderate", "Low", "Very Low"],
        label_visibility="collapsed"
    )

    st.markdown('<div class="sidebar-label" style="margin-top:14px">Score Range</div>', unsafe_allow_html=True)
    score_range = st.slider("", 0, 100, (0, 100), label_visibility="collapsed")

    st.markdown('<div class="sidebar-label" style="margin-top:14px">Map Color Variable</div>', unsafe_allow_html=True)
    map_metric = st.selectbox(
        "",
        ["opportunity_score", "economic_score", "health_score", "housing_score"],
        format_func=lambda x: x.replace("_", " ").title(),
        label_visibility="collapsed"
    )

    st.markdown("---")

    # Filter data
    filtered = df[
        (df["opportunity_score"] >= score_range[0]) &
        (df["opportunity_score"] <= score_range[1])
    ]
    if selected_tier != "All":
        filtered = filtered[filtered["tier"] == selected_tier]

    st.markdown(f"""
    <div class="sidebar-section">
        <div class="sidebar-label">Active Filter</div>
        <div style="font-size:22px; font-weight:800; color:#0a2342">{len(filtered):,}</div>
        <div style="font-size:12px; color:#64748b">tracts shown</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("""
    <div style="font-size:12px; color:#64748b; line-height:1.8;">
        <strong style="color:#0a2342;">Joshua Mlongecha</strong><br>
        University of Connecticut<br>
        B.S. Data Science, 2028<br><br>
        <strong style="color:#0a2342;">Data Sources</strong><br>
        · U.S. Census ACS 5-Year (2022)<br>
        · CDC PLACES (2023)<br>
        · TIGER/Line Shapefiles
    </div>
    """, unsafe_allow_html=True)

# ─────────────────────────────────────────────
# METRIC CARDS
# ─────────────────────────────────────────────

st.markdown('<div class="section-title">Key Metrics</div>', unsafe_allow_html=True)

m1, m2, m3, m4, m5 = st.columns(5)

cards = [
    (m1, "Total Tracts", f"{len(filtered):,}", "", "#2e86c1"),
    (m2, "Avg Opportunity Score", f"{filtered['opportunity_score'].mean():.1f}", "/ 100", "#0a2342"),
    (m3, "Very High Opportunity", f"{(filtered['tier'] == 'Very High').sum():,}", "tracts", "#16a34a"),
    (m4, "Low Opportunity", f"{(filtered['tier'] == 'Low').sum():,}", "tracts", "#ea580c"),
    (m5, "Very Low Opportunity", f"{(filtered['tier'] == 'Very Low').sum():,}", "tracts", "#dc2626"),
]

for col, label, value, sub, color in cards:
    with col:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{value}</div>
            <div style="font-size:12px; color:#94a3b8;">{sub}</div>
            <div class="metric-accent" style="background:{color};"></div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("---")

# ─────────────────────────────────────────────
# TABS
# ─────────────────────────────────────────────

tab1, tab2, tab3 = st.tabs(["🗺️  Opportunity Map", "📊  Analytics", "📋  Data Table"])

# ── TAB 1: MAP ──
with tab1:
    map_col, rank_col = st.columns([3, 1])

    with map_col:
        st.markdown('<div class="content-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Interactive Opportunity Map</div>', unsafe_allow_html=True)
        st.markdown("Hover over any census tract to see its full score breakdown.", unsafe_allow_html=True)
        st.markdown("---")

        m = folium.Map(
            location=[41.85, -87.75],
            zoom_start=10,
            tiles="CartoDB positron"
        )

        color_scale = {
            "Very High": "#15803d",
            "High":      "#4ade80",
            "Moderate":  "#facc15",
            "Low":       "#f97316",
            "Very Low":  "#dc2626",
        }

        filtered_geoids = set(filtered["GEOID"].astype(str))
        filtered_geojson = {
            "type": "FeatureCollection",
            "features": [
                f for f in geojson["features"]
                if str(f["properties"].get("GEOID", "")) in filtered_geoids
            ]
        }

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
                    feature["properties"].get("tier", "Moderate"), "#facc15"
                ),
                "color": "#ffffff",
                "weight": 0.5,
                "fillOpacity": 0.75,
            },
            highlight_function=lambda feature: {
                "weight": 2,
                "color": "#0a2342",
                "fillOpacity": 0.9,
            },
            tooltip=folium.GeoJsonTooltip(
                fields=["GEOID", "opportunity_score", "economic_score",
                        "health_score", "housing_score", "tier"],
                aliases=["📍 Tract ID", "⭐ Opportunity", "💰 Economic",
                         "🏥 Health", "🏠 Housing", "🏷️ Tier"],
                localize=True,
                sticky=False,
                style="""
                    background-color: white;
                    border: 1px solid #e2e8f0;
                    border-radius: 8px;
                    box-shadow: 0 4px 12px rgba(0,0,0,0.1);
                    font-family: Inter, sans-serif;
                    font-size: 13px;
                    color: #ffffff;
                    padding: 8px;
                """
            )
        ).add_to(m)

        legend_html = """
        <div style="position:fixed; bottom:24px; left:24px; z-index:1000;
                    background:white; padding:16px 20px; border-radius:12px;
                    border:1px solid #e2e8f0; box-shadow:0 4px 16px rgba(0,0,0,0.1);
                    font-family:Inter,sans-serif; font-size:13px; color:#1a1f36;">
            <div style="font-weight:700; margin-bottom:10px; font-size:13px;">Opportunity Tier</div>
            <div><span style="color:#15803d; font-size:16px;">■</span>&nbsp; Very High &nbsp;<span style="color:#94a3b8; font-size:11px;">80–100</span></div>
            <div><span style="color:#4ade80; font-size:16px;">■</span>&nbsp; High &nbsp;<span style="color:#94a3b8; font-size:11px;">65–80</span></div>
            <div><span style="color:#facc15; font-size:16px;">■</span>&nbsp; Moderate &nbsp;<span style="color:#94a3b8; font-size:11px;">45–65</span></div>
            <div><span style="color:#f97316; font-size:16px;">■</span>&nbsp; Low &nbsp;<span style="color:#94a3b8; font-size:11px;">25–45</span></div>
            <div><span style="color:#dc2626; font-size:16px;">■</span>&nbsp; Very Low &nbsp;<span style="color:#94a3b8; font-size:11px;">0–25</span></div>
        </div>
        """
        m.get_root().html.add_child(folium.Element(legend_html))
        st_folium(m, width=None, height=560, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with rank_col:
        st.markdown('<div class="content-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Rankings</div>', unsafe_allow_html=True)

        st.markdown("**🟢 Top 5 Tracts**")
        top = filtered.nlargest(5, "opportunity_score")[
            ["GEOID", "opportunity_score", "tier"]
        ].reset_index(drop=True)
        top.columns = ["Tract", "Score", "Tier"]
        st.dataframe(top, use_container_width=True, hide_index=True)

        st.markdown("<br>**🔴 Bottom 5 Tracts**")
        bottom = filtered.nsmallest(5, "opportunity_score")[
            ["GEOID", "opportunity_score", "tier"]
        ].reset_index(drop=True)
        bottom.columns = ["Tract", "Score", "Tier"]
        st.dataframe(bottom, use_container_width=True, hide_index=True)
        st.markdown('</div>', unsafe_allow_html=True)

# ── TAB 2: ANALYTICS ──
with tab2:
    st.markdown('<div class="content-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Score Analytics</div>', unsafe_allow_html=True)

    c1, c2 = st.columns(2)

    with c1:
        st.markdown("**Tracts by Opportunity Tier**")
        tier_order = ["Very Low", "Low", "Moderate", "High", "Very High"]
        tier_counts = filtered["tier"].value_counts().reindex(tier_order).fillna(0)
        st.bar_chart(tier_counts, color="#2e86c1")

    with c2:
        st.markdown("**Average Score by Component**")
        avg_scores = pd.DataFrame({
            "Score": [
                filtered["economic_score"].mean(),
                filtered["health_score"].mean(),
                filtered["housing_score"].mean(),
                filtered["opportunity_score"].mean(),
            ]
        }, index=["Economic", "Health", "Housing", "Overall"])
        st.bar_chart(avg_scores, color="#0a2342")

    st.markdown("<br>")

    c3, c4 = st.columns(2)
    with c3:
        st.markdown("**Score Distribution**")
        hist_data = pd.DataFrame({"Opportunity Score": filtered["opportunity_score"]})
        st.bar_chart(hist_data["Opportunity Score"].value_counts(bins=10).sort_index())

    with c4:
        st.markdown("**Summary Statistics**")
        stats = filtered["opportunity_score"].describe().round(2)
        stats_df = pd.DataFrame({"Statistic": stats.index, "Value": stats.values})
        st.dataframe(stats_df, use_container_width=True, hide_index=True)

    st.markdown('</div>', unsafe_allow_html=True)

# ── TAB 3: DATA TABLE ──
with tab3:
    st.markdown('<div class="content-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Full Dataset</div>', unsafe_allow_html=True)

    col_search, col_sort, col_dl = st.columns([2, 2, 1])
    with col_sort:
        sort_col = st.selectbox(
            "Sort by",
            ["opportunity_score", "economic_score", "health_score", "housing_score"],
            format_func=lambda x: x.replace("_", " ").title()
        )
    with col_dl:
        st.markdown("---")
        st.download_button(
            "⬇️ Export CSV",
            data=filtered.to_csv(index=False),
            file_name="chicago_opportunity_scores.csv",
            mime="text/csv",
            use_container_width=True
        )

    st.dataframe(
        filtered.sort_values(sort_col, ascending=False),
        use_container_width=True,
        hide_index=True,
        height=500
    )
    st.markdown('</div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────

st.markdown("""
<div class="footer">
    <strong>Chicago Neighborhood Opportunity Index</strong> · Built by Joshua Mlongecha · University of Connecticut · Data Science 2028<br>
    Data: U.S. Census Bureau ACS 5-Year Estimates (2022) · CDC PLACES Health Data (2023) · U.S. Census TIGER/Line Shapefiles<br>
    <span style="color:#cbd5e1;">Last updated: June 2026 · For portfolio and research purposes only</span>
</div>
""", unsafe_allow_html=True)