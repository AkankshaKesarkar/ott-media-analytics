"""
churn_model.py
ML model to predict subscriber churn using RFM features.
Random Forest + SMOTE for class imbalance.
"""

import pandas as pd
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import os

matplotlib.use("Agg")

from sklearn.ensemble         import RandomForestClassifier
from sklearn.model_selection  import train_test_split, cross_val_score
from sklearn.metrics          import (classification_report,
                                      confusion_matrix,
                                      roc_auc_score, roc_curve)
from sklearn.preprocessing    import StandardScaler

OUTPUT_DIR = "outputs"
os.makedirs(OUTPUT_DIR, exist_ok=True)


def build_rfm_features(subscribers_df, sessions_df, revenue_df):
    """Build RFM (Recency, Frequency, Monetary) + engagement features."""
    print("\n[Churn] Building RFM feature set...")

    sessions_df["watch_date"] = pd.to_datetime(sessions_df["watch_date"])
    latest = sessions_df["watch_date"].max()

    # Recency — days since last session
    recency = (sessions_df.groupby("subscriber_id")["watch_date"]
               .max()
               .reset_index()
               .rename(columns={"watch_date": "last_seen"}))
    recency["recency_days"] = (latest - recency["last_seen"]).dt.days

    # Frequency — total sessions
    frequency = (sessions_df.groupby("subscriber_id")["session_id"]
                 .count()
                 .reset_index()
                 .rename(columns={"session_id": "total_sessions"}))

    # Monetary — total revenue
    monetary = (revenue_df.groupby("subscriber_id")["amount"]
                .sum()
                .reset_index()
                .rename(columns={"amount": "total_revenue"}))

    # Avg completion rate
    completion = (sessions_df.groupby("subscriber_id")["completion_pct"]
                  .mean()
                  .reset_index()
                  .rename(columns={"completion_pct": "avg_completion"}))

    # Merge all features
    features = (subscribers_df[["subscriber_id", "plan_type", "churn_date"]]
                .merge(recency[["subscriber_id", "recency_days"]], on="subscriber_id", how="left")
                .merge(frequency, on="subscriber_id", how="left")
                .merge(monetary,  on="subscriber_id", how="left")
                .merge(completion, on="subscriber_id", how="left"))

    features["churned"]      = features["churn_date"].notna().astype(int)
    features["is_premium"]   = (features["plan_type"] == "Premium").astype(int)
    features["is_standard"]  = (features["plan_type"] == "Standard").astype(int)
    features = features.fillna(0)

    print(f"[Churn] Feature set shape: {features.shape}")
    print(f"[Churn] Churn rate in data: "
          f"{features['churned'].mean()*100:.1f}%")
    return features


def train_churn_model(features_df):
    """Train Random Forest churn classifier."""
    feature_cols = ["recency_days", "total_sessions", "total_revenue",
                    "avg_completion", "is_premium", "is_standard"]

    X = features_df[feature_cols].values
    y = features_df["churned"].values

    # Handle class imbalance with class_weight
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y)

    scaler  = StandardScaler()
    X_train = scaler.fit_transform(X_train)
    X_test  = scaler.transform(X_test)

    model = RandomForestClassifier(
        n_estimators=100,
        max_depth=8,
        class_weight="balanced",
        random_state=42,
        n_jobs=-1
    )
    model.fit(X_train, y_train)

    # Evaluate
    preds  = model.predict(X_test)
    proba  = model.predict_proba(X_test)[:, 1]
    auc    = roc_auc_score(y_test, proba)
    cv_acc = cross_val_score(model, X_train, y_train,
                             cv=5, scoring="accuracy").mean()

    print("\n[Churn] Model Evaluation")
    print("=" * 45)
    print(f"  Cross-val Accuracy : {cv_acc*100:.2f}%")
    print(f"  ROC-AUC Score      : {auc:.4f}")
    print("\n  Classification Report:")
    print(classification_report(y_test, preds,
                                target_names=["Retained", "Churned"],
                                digits=3))

    _plot_churn_model(model, X_test, y_test, proba, feature_cols)
    return model, scaler


def _plot_churn_model(model, X_test, y_test, proba, feature_cols):
    fig, axes = plt.subplots(1, 2, figsize=(16, 6))
    fig.suptitle("Churn Prediction Model — Random Forest",
                 fontsize=14, fontweight="bold")

    # ROC Curve
    fpr, tpr, _ = roc_curve(y_test, proba)
    auc          = roc_auc_score(y_test, proba)
    axes[0].plot(fpr, tpr, color="#1E88E5", lw=2.5,
                 label=f"ROC AUC = {auc:.3f}")
    axes[0].plot([0, 1], [0, 1], "r--", lw=1.5, label="Random baseline")
    axes[0].set_title("ROC Curve")
    axes[0].set_xlabel("False Positive Rate")
    axes[0].set_ylabel("True Positive Rate")
    axes[0].legend()
    axes[0].grid(True, alpha=0.3)

    # Feature importances
    importances = pd.Series(model.feature_importances_, index=feature_cols)
    importances.sort_values().plot(kind="barh", ax=axes[1],
                                   color="#43A047", edgecolor="white")
    axes[1].set_title("Feature Importances")
    axes[1].set_xlabel("Importance Score")
    axes[1].grid(True, axis="x", alpha=0.3)

    plt.tight_layout()
    plt.savefig(f"{OUTPUT_DIR}/churn_model_analysis.png",
                dpi=150, bbox_inches="tight")
    plt.close()
    print("[Churn] Saved → churn_model_analysis.png")
