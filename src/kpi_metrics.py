"""
kpi_metrics.py
Core KPI calculation engine for OTT media analytics.
Computes: DAU, MAU, ARPU, Churn Rate, Content Completion Rate,
          Genre Performance, Regional Breakdown, Prime Time Analysis.
"""

import pandas as pd
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import seaborn as sns
import os

matplotlib.use("Agg")
OUTPUT_DIR = "outputs"
os.makedirs(OUTPUT_DIR, exist_ok=True)


def compute_kpi_scorecard(subscribers_df, sessions_df, revenue_df):
    """Compute and print top-level KPI scorecard."""
    print("\n[KPI] Computing Business KPI Scorecard...")
    print("=" * 55)

    # MAU — unique subscribers with at least 1 session in last 30 days
    sessions_df["watch_date"] = pd.to_datetime(sessions_df["watch_date"])
    latest = sessions_df["watch_date"].max()
    mau_df = sessions_df[sessions_df["watch_date"] >=
                         latest - pd.Timedelta(days=30)]
    mau    = mau_df["subscriber_id"].nunique()

    # DAU — unique subscribers on most recent date
    last_day = sessions_df[sessions_df["watch_date"] == latest]
    dau      = last_day["subscriber_id"].nunique()

    # ARPU — Average Revenue Per User
    total_rev = revenue_df["amount"].sum()
    total_sub = subscribers_df["subscriber_id"].nunique()
    arpu      = round(total_rev / total_sub, 2)

    # Churn rate
    churned   = subscribers_df["churn_date"].notna().sum()
    churn_rate = round(churned / total_sub * 100, 2)

    # Avg content completion rate
    avg_completion = round(sessions_df["completion_pct"].mean(), 2)

    # Total watch hours
    total_watch_hrs = round(sessions_df["watch_mins"].sum() / 60, 0)

    kpis = {
        "Monthly Active Users (MAU)":      f"{mau:,}",
        "Daily Active Users (DAU)":        f"{dau:,}",
        "Avg Revenue Per User (ARPU)":     f"₹{arpu:,}",
        "Subscriber Churn Rate":           f"{churn_rate}%",
        "Avg Content Completion Rate":     f"{avg_completion}%",
        "Total Watch Hours (All Time)":    f"{total_watch_hrs:,.0f} hrs",
        "Total Revenue":                   f"₹{total_rev:,.0f}",
        "Total Subscribers":               f"{total_sub:,}",
    }

    for k, v in kpis.items():
        print(f"  {k:<38} {v:>12}")
    print("=" * 55)
    return kpis


def plot_viewership_trends(sessions_df):
    """Monthly viewership trend line chart."""
    sessions_df["month"] = sessions_df["watch_date"].dt.to_period("M")
    monthly = (sessions_df.groupby("month")
               .agg(sessions=("session_id", "count"),
                    unique_viewers=("subscriber_id", "nunique"),
                    total_watch_hrs=("watch_mins",
                                     lambda x: round(x.sum() / 60, 1)))
               .reset_index())
    monthly["month"] = monthly["month"].astype(str)

    fig, axes = plt.subplots(1, 3, figsize=(18, 5))
    fig.suptitle("Monthly Viewership Trends — OTT Platform",
                 fontsize=14, fontweight="bold")

    metrics = ["sessions", "unique_viewers", "total_watch_hrs"]
    titles  = ["Total Sessions", "Unique Viewers", "Total Watch Hours"]
    colors  = ["#1E88E5", "#43A047", "#FB8C00"]

    for ax, metric, title, color in zip(axes, metrics, titles, colors):
        ax.plot(monthly["month"], monthly[metric],
                color=color, linewidth=2.5, marker="o", markersize=5)
        ax.fill_between(monthly["month"], monthly[metric],
                         alpha=0.15, color=color)
        ax.set_title(title, fontsize=11)
        ax.set_xlabel("Month")
        ax.tick_params(axis="x", rotation=45)
        ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(f"{OUTPUT_DIR}/viewership_trends.png",
                dpi=150, bbox_inches="tight")
    plt.close()
    print("[KPI] Saved → viewership_trends.png")


def plot_genre_performance(sessions_df, content_df):
    """Genre-level engagement and watch time analysis."""
    merged = sessions_df.merge(
        content_df[["content_id", "genre", "production_cost"]],
        on="content_id", how="left"
    )
    genre_stats = (merged.groupby("genre")
                   .agg(total_views=("session_id", "count"),
                        avg_completion=("completion_pct", "mean"),
                        total_watch_hrs=("watch_mins",
                                         lambda x: round(x.sum() / 60, 1)),
                        avg_cost=("production_cost", "mean"))
                   .reset_index()
                   .sort_values("total_views", ascending=False))

    fig, axes = plt.subplots(1, 3, figsize=(18, 6))
    fig.suptitle("Genre Performance Analysis", fontsize=14, fontweight="bold")

    palette = sns.color_palette("tab10", len(genre_stats))

    # Total views
    axes[0].barh(genre_stats["genre"], genre_stats["total_views"],
                 color=palette, edgecolor="white")
    axes[0].set_title("Total Views by Genre")
    axes[0].set_xlabel("Views")

    # Avg completion rate
    axes[1].barh(genre_stats["genre"], genre_stats["avg_completion"].round(1),
                 color=palette, edgecolor="white")
    axes[1].set_title("Avg Completion Rate (%) by Genre")
    axes[1].set_xlabel("Completion %")

    # Total watch hours
    axes[2].barh(genre_stats["genre"], genre_stats["total_watch_hrs"],
                 color=palette, edgecolor="white")
    axes[2].set_title("Total Watch Hours by Genre")
    axes[2].set_xlabel("Hours")

    for ax in axes:
        ax.grid(True, axis="x", alpha=0.3)

    plt.tight_layout()
    plt.savefig(f"{OUTPUT_DIR}/genre_performance.png",
                dpi=150, bbox_inches="tight")
    plt.close()
    print("[KPI] Saved → genre_performance.png")


def plot_churn_analysis(subscribers_df, revenue_df):
    """Churn rate by plan type and region."""
    churn = subscribers_df.copy()
    churn["churned"] = churn["churn_date"].notna().astype(int)

    fig, axes = plt.subplots(1, 2, figsize=(16, 6))
    fig.suptitle("Subscriber Churn Analysis",
                 fontsize=14, fontweight="bold")

    # By plan type
    plan_churn = (churn.groupby("plan_type")
                  .agg(total=("subscriber_id", "count"),
                       churned=("churned", "sum"))
                  .assign(churn_rate=lambda x:
                          (x["churned"] / x["total"] * 100).round(2))
                  .reset_index())
    colors_plan = ["#E53935", "#FB8C00", "#43A047"]
    axes[0].bar(plan_churn["plan_type"], plan_churn["churn_rate"],
                color=colors_plan, edgecolor="white", width=0.5)
    for i, (_, row) in enumerate(plan_churn.iterrows()):
        axes[0].text(i, row["churn_rate"] + 0.2,
                     f"{row['churn_rate']}%", ha="center", fontsize=10)
    axes[0].set_title("Churn Rate by Plan Type")
    axes[0].set_ylabel("Churn Rate (%)")
    axes[0].grid(True, axis="y", alpha=0.3)

    # By region
    region_churn = (churn.groupby("region")
                    .agg(total=("subscriber_id", "count"),
                         churned=("churned", "sum"))
                    .assign(churn_rate=lambda x:
                            (x["churned"] / x["total"] * 100).round(2))
                    .sort_values("churn_rate", ascending=True)
                    .reset_index())
    axes[1].barh(region_churn["region"], region_churn["churn_rate"],
                 color="#1E88E5", edgecolor="white")
    axes[1].set_title("Churn Rate by Region")
    axes[1].set_xlabel("Churn Rate (%)")
    axes[1].grid(True, axis="x", alpha=0.3)

    plt.tight_layout()
    plt.savefig(f"{OUTPUT_DIR}/churn_analysis.png",
                dpi=150, bbox_inches="tight")
    plt.close()
    print("[KPI] Saved → churn_analysis.png")


def plot_primetime_heatmap(sessions_df):
    """Content completion heatmap by hour and day of week."""
    sessions_df["day_of_week"] = sessions_df["watch_date"].dt.day_name()
    day_order = ["Monday", "Tuesday", "Wednesday",
                 "Thursday", "Friday", "Saturday", "Sunday"]

    pivot = (sessions_df.groupby(["day_of_week", "watch_hour"])
             ["completion_pct"].mean()
             .unstack(fill_value=0))
    pivot = pivot.reindex(day_order)

    fig, ax = plt.subplots(figsize=(18, 6))
    sns.heatmap(pivot, ax=ax, cmap="YlOrRd", linewidths=0.3,
                cbar_kws={"label": "Avg Completion %"},
                fmt=".0f", annot=False)
    ax.set_title("Content Completion Rate Heatmap — Day vs Hour",
                 fontsize=14, fontweight="bold")
    ax.set_xlabel("Hour of Day")
    ax.set_ylabel("Day of Week")

    plt.tight_layout()
    plt.savefig(f"{OUTPUT_DIR}/content_completion_heatmap.png",
                dpi=150, bbox_inches="tight")
    plt.close()
    print("[KPI] Saved → content_completion_heatmap.png")
