"""
main.py
OTT Media Analytics Platform — Full Pipeline Runner

Run: python main.py
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

import pandas as pd
from data_generator import generate_all
from kpi_metrics    import (compute_kpi_scorecard, plot_viewership_trends,
                             plot_genre_performance, plot_churn_analysis,
                             plot_primetime_heatmap)
from churn_model    import build_rfm_features, train_churn_model


def main():
    print("=" * 60)
    print("  OTT MEDIA ANALYTICS PLATFORM")
    print("  Business Analyst / Data Analyst (Media) — Wipro L1")
    print("  Author: Akanksha Ramchandra Kesarkar")
    print("=" * 60)

    # Step 1: Generate or load data
    DATA_FILES = ["data/content_catalog.csv", "data/subscribers.csv",
                  "data/watch_sessions.csv",  "data/revenue.csv"]

    if all(os.path.exists(f) for f in DATA_FILES):
        print("\n[Main] Loading existing datasets...")
        content_df     = pd.read_csv("data/content_catalog.csv")
        subscribers_df = pd.read_csv("data/subscribers.csv")
        sessions_df    = pd.read_csv("data/watch_sessions.csv")
        revenue_df     = pd.read_csv("data/revenue.csv")
    else:
        content_df, subscribers_df, sessions_df, revenue_df = generate_all()

    # Step 2: KPI Scorecard
    compute_kpi_scorecard(subscribers_df, sessions_df, revenue_df)

    # Step 3: Visualisations
    print("\n[Main] Generating analytics charts...")
    sessions_df["watch_date"] = pd.to_datetime(sessions_df["watch_date"])
    plot_viewership_trends(sessions_df)
    plot_genre_performance(sessions_df, content_df)
    plot_churn_analysis(subscribers_df, revenue_df)
    plot_primetime_heatmap(sessions_df)

    # Step 4: Churn prediction model
    print("\n[Main] Training churn prediction model...")
    features_df = build_rfm_features(subscribers_df, sessions_df, revenue_df)
    train_churn_model(features_df)

    print("\n" + "=" * 60)
    print("  PIPELINE COMPLETE")
    print("  All charts saved to → outputs/")
    print("  SQL scripts ready   → sql/")
    print("=" * 60)


if __name__ == "__main__":
    main()
