# ============================================================
# Neighborhood Health & Wealth Index — Phase 4: ML Model
# Goal: Predict which neighborhoods are "At Risk"
# Author: Joshua Mlongecha
# Run with: python3 phase4_ml_model.py
# ============================================================

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import (classification_report, confusion_matrix,
                             roc_auc_score, roc_curve)
from sklearn.preprocessing import StandardScaler
import os

OUTPUT_DIR = "data"
PLOTS_DIR = "plots"
os.makedirs(PLOTS_DIR, exist_ok=True)

# ─────────────────────────────────────────────
# 1. LOAD DATA
# ─────────────────────────────────────────────

print("📂 Loading data...")
scores_df = pd.read_csv("data/chicago_opportunity_scores.csv")
raw_df = pd.read_csv("data/chicago_tracts_raw.csv")

scores_df["GEOID"] = scores_df["GEOID"].astype(str)
raw_df["GEOID"] = raw_df["GEOID"].astype(str)

df = pd.merge(raw_df, scores_df[["GEOID", "opportunity_score", "tier"]], on="GEOID")
print(f"   ✅ {len(df)} tracts loaded")

# ─────────────────────────────────────────────
# 2. CREATE TARGET VARIABLE
#    "At Risk" = opportunity score below 55
#    "Stable"  = opportunity score 55 or above
# ─────────────────────────────────────────────

print("\n🎯 Creating target variable...")
THRESHOLD = 55
df["at_risk"] = (df["opportunity_score"] < THRESHOLD).astype(int)

at_risk_count = df["at_risk"].sum()
stable_count = len(df) - at_risk_count
print(f"   At Risk:  {at_risk_count} tracts ({at_risk_count/len(df)*100:.1f}%)")
print(f"   Stable:   {stable_count} tracts ({stable_count/len(df)*100:.1f}%)")

# ─────────────────────────────────────────────
# 3. FEATURES
# ─────────────────────────────────────────────

FEATURES = [
    "median_household_income",
    "median_home_value",
    "total_population",
    "poverty_rate",
    "unemployment_rate",
    "college_rate",
    "renter_rate",
    "uninsured_pct",
    "diabetes_pct",
    "physical_inactivity_pct",
    "poor_mental_health_pct",
    "obesity_pct",
]

df = df.dropna(subset=FEATURES + ["at_risk"])

# Fix negative home values
df["median_home_value"] = df["median_home_value"].replace(-666666666, np.nan)
df["median_home_value"] = df["median_home_value"].fillna(df["median_home_value"].median())

X = df[FEATURES]
y = df["at_risk"]

print(f"\n   Features: {len(FEATURES)}")
print(f"   Samples:  {len(X)}")

# ─────────────────────────────────────────────
# 4. TRAIN / TEST SPLIT
# ─────────────────────────────────────────────

print("\n✂️  Splitting data...")
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)
print(f"   Train: {len(X_train)} | Test: {len(X_test)}")

# Scale for logistic regression
scaler = StandardScaler()
X_train_sc = scaler.fit_transform(X_train)
X_test_sc = scaler.transform(X_test)

# ─────────────────────────────────────────────
# 5. TRAIN MODELS
# ─────────────────────────────────────────────

print("\n🤖 Training models...")

models = {
    "Random Forest": RandomForestClassifier(
        n_estimators=200, max_depth=8, random_state=42, class_weight="balanced"
    ),
    "Gradient Boosting": GradientBoostingClassifier(
        n_estimators=200, max_depth=4, random_state=42
    ),
    "Logistic Regression": LogisticRegression(
        max_iter=1000, random_state=42, class_weight="balanced"
    ),
}

results = {}
for name, model in models.items():
    if name == "Logistic Regression":
        model.fit(X_train_sc, y_train)
        y_pred = model.predict(X_test_sc)
        y_prob = model.predict_proba(X_test_sc)[:, 1]
    else:
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        y_prob = model.predict_proba(X_test)[:, 1]

    cv_scores = cross_val_score(
        model,
        X_train_sc if name == "Logistic Regression" else X_train,
        y_train, cv=5, scoring="roc_auc"
    )

    results[name] = {
        "model": model,
        "y_pred": y_pred,
        "y_prob": y_prob,
        "auc": roc_auc_score(y_test, y_prob),
        "cv_auc": cv_scores.mean(),
        "report": classification_report(y_test, y_pred, target_names=["Stable", "At Risk"])
    }
    print(f"   ✅ {name} — AUC: {results[name]['auc']:.3f} | CV AUC: {results[name]['cv_auc']:.3f}")

# ─────────────────────────────────────────────
# 6. BEST MODEL REPORT
# ─────────────────────────────────────────────

best_name = max(results, key=lambda k: results[k]["auc"])
best = results[best_name]
print(f"\n🏆 Best Model: {best_name} (AUC: {best['auc']:.3f})")
print("\n📊 Classification Report:")
print(best["report"])

# ─────────────────────────────────────────────
# 7. FEATURE IMPORTANCE
# ─────────────────────────────────────────────

print("📈 Computing feature importance...")
rf_model = results["Random Forest"]["model"]
importances = pd.DataFrame({
    "Feature": FEATURES,
    "Importance": rf_model.feature_importances_
}).sort_values("Importance", ascending=False)

print("\n   Top Features:")
print(importances.to_string(index=False))

# ─────────────────────────────────────────────
# 8. PLOTS
# ─────────────────────────────────────────────

print("\n🎨 Generating plots...")
plt.style.use("dark_background")
fig, axes = plt.subplots(2, 2, figsize=(16, 12))
fig.patch.set_facecolor("#0a0e1a")

# ── Feature Importance ──
ax1 = axes[0, 0]
colors = ["#2e86c1" if i == 0 else "#4a9fd4" for i in range(len(importances))]
bars = ax1.barh(importances["Feature"], importances["Importance"], color=colors)
ax1.set_facecolor("#111827")
ax1.set_title("Feature Importance (Random Forest)", color="white", fontsize=13, fontweight="bold", pad=12)
ax1.set_xlabel("Importance Score", color="#94a3b8")
ax1.tick_params(colors="white")
ax1.spines[["top", "right"]].set_visible(False)
for spine in ax1.spines.values():
    spine.set_color("#2d2f3e")

# ── ROC Curves ──
ax2 = axes[0, 1]
ax2.set_facecolor("#111827")
colors_roc = ["#2e86c1", "#00c853", "#f97316"]
for (name, res), color in zip(results.items(), colors_roc):
    fpr, tpr, _ = roc_curve(y_test, res["y_prob"])
    ax2.plot(fpr, tpr, label=f"{name} (AUC={res['auc']:.3f})", color=color, linewidth=2)
ax2.plot([0, 1], [0, 1], "w--", alpha=0.3)
ax2.set_title("ROC Curves — All Models", color="white", fontsize=13, fontweight="bold", pad=12)
ax2.set_xlabel("False Positive Rate", color="#94a3b8")
ax2.set_ylabel("True Positive Rate", color="#94a3b8")
ax2.tick_params(colors="white")
ax2.legend(facecolor="#1a1d27", labelcolor="white", fontsize=9)
ax2.spines[["top", "right"]].set_visible(False)
for spine in ax2.spines.values():
    spine.set_color("#2d2f3e")

# ── Confusion Matrix ──
ax3 = axes[1, 0]
cm = confusion_matrix(y_test, best["y_pred"])
sns.heatmap(cm, annot=True, fmt="d", cmap="Blues",
            xticklabels=["Stable", "At Risk"],
            yticklabels=["Stable", "At Risk"],
            ax=ax3, cbar=False,
            annot_kws={"size": 14, "color": "white"})
ax3.set_facecolor("#111827")
ax3.set_title(f"Confusion Matrix — {best_name}", color="white", fontsize=13, fontweight="bold", pad=12)
ax3.set_xlabel("Predicted", color="#94a3b8")
ax3.set_ylabel("Actual", color="#94a3b8")
ax3.tick_params(colors="white")

# ── Score Distribution by Risk ──
ax4 = axes[1, 1]
ax4.set_facecolor("#111827")
stable = df[df["at_risk"] == 0]["opportunity_score"]
at_risk = df[df["at_risk"] == 1]["opportunity_score"]
ax4.hist(stable, bins=30, alpha=0.7, color="#00c853", label="Stable", edgecolor="none")
ax4.hist(at_risk, bins=30, alpha=0.7, color="#f44336", label="At Risk", edgecolor="none")
ax4.axvline(THRESHOLD, color="white", linestyle="--", linewidth=1.5, label=f"Threshold ({THRESHOLD})")
ax4.set_title("Score Distribution by Risk Class", color="white", fontsize=13, fontweight="bold", pad=12)
ax4.set_xlabel("Opportunity Score", color="#94a3b8")
ax4.set_ylabel("Number of Tracts", color="#94a3b8")
ax4.tick_params(colors="white")
ax4.legend(facecolor="#1a1d27", labelcolor="white", fontsize=9)
ax4.spines[["top", "right"]].set_visible(False)
for spine in ax4.spines.values():
    spine.set_color("#2d2f3e")

plt.suptitle("Chicago Neighborhood Risk Model — Joshua Mlongecha",
             color="white", fontsize=15, fontweight="bold", y=1.01)
plt.tight_layout()
plot_path = os.path.join(PLOTS_DIR, "model_results.png")
plt.savefig(plot_path, dpi=150, bbox_inches="tight", facecolor="#0a0e1a")
print(f"   ✅ Saved: {plot_path}")

# ─────────────────────────────────────────────
# 9. SAVE PREDICTIONS
# ─────────────────────────────────────────────

print("\n💾 Saving predictions...")
rf = results["Random Forest"]["model"]
df["risk_probability"] = rf.predict_proba(X)[:, 1]
df["risk_prediction"] = rf.predict(X)
df["risk_label"] = df["risk_prediction"].map({0: "Stable", 1: "At Risk"})

output = df[["GEOID", "opportunity_score", "tier",
             "risk_probability", "risk_prediction", "risk_label"] + FEATURES]
output_path = os.path.join(OUTPUT_DIR, "chicago_risk_predictions.csv")
output.to_csv(output_path, index=False)
print(f"   ✅ Saved: {output_path}")

print("\n✅ Phase 4 complete! Ready for Phase 5 (GitHub + README).")
print(f"\n📊 Summary:")
print(f"   Best model:  {best_name}")
print(f"   AUC Score:   {best['auc']:.3f}")
print(f"   At-Risk tracts identified: {df['risk_prediction'].sum()}")
