"""
data_generator.py
Generates synthetic OTT streaming platform data:
  - content catalog (500 titles)
  - subscriber profiles (10,000)
  - watch sessions (50,000+)
  - monthly revenue records
"""

import numpy as np
import pandas as pd
import os
import random
from datetime import date, timedelta

SEED = 42
np.random.seed(SEED)
random.seed(SEED)

GENRES         = ["Drama", "Thriller", "Comedy", "Action", "Documentary",
                  "Romance", "Sci-Fi", "Horror", "Animation", "Reality"]
LANGUAGES      = ["English", "Hindi", "Tamil", "Telugu", "Bengali", "Kannada"]
CONTENT_TYPES  = ["Movie", "Series", "Documentary", "Short Film"]
DEVICE_TYPES   = ["Mobile", "Smart TV", "Laptop", "Tablet", "Desktop"]
REGIONS        = ["North India", "South India", "East India",
                  "West India", "Maharashtra", "Karnataka"]
PLAN_TYPES     = ["Basic", "Standard", "Premium"]
PLAN_REVENUE   = {"Basic": 199, "Standard": 399, "Premium": 699}


def generate_content(n=500, save_path="data/content_catalog.csv"):
    os.makedirs("data", exist_ok=True)
    records = []
    for i in range(1, n + 1):
        genre        = np.random.choice(GENRES)
        ctype        = np.random.choice(CONTENT_TYPES,
                           p=[0.4, 0.35, 0.15, 0.1])
        duration     = (np.random.randint(80, 180) if ctype == "Movie"
                        else np.random.randint(20, 55))
        records.append({
            "content_id":      f"C{i:04d}",
            "title":           f"{genre} Title {i}",
            "genre":           genre,
            "content_type":    ctype,
            "release_year":    np.random.randint(2018, 2026),
            "duration_mins":   duration,
            "language":        np.random.choice(LANGUAGES),
            "production_cost": round(np.random.uniform(5e5, 5e7), 2)
        })
    df = pd.DataFrame(records)
    df.to_csv(save_path, index=False)
    print(f"[DataGen] Content catalog → {save_path} | {len(df)} titles")
    return df


def generate_subscribers(n=10000, save_path="data/subscribers.csv"):
    records = []
    start   = date(2024, 1, 1)
    for i in range(1, n + 1):
        plan      = np.random.choice(PLAN_TYPES, p=[0.5, 0.3, 0.2])
        join_date = start + timedelta(days=np.random.randint(0, 365))
        # 15% churn probability
        churned   = np.random.random() < 0.15
        churn_date = (join_date + timedelta(
                          days=np.random.randint(30, 180))
                      if churned else None)
        records.append({
            "subscriber_id":   f"S{i:06d}",
            "region":          np.random.choice(REGIONS),
            "device_type":     np.random.choice(DEVICE_TYPES,
                                   p=[0.35, 0.3, 0.2, 0.1, 0.05]),
            "plan_type":       plan,
            "join_date":       join_date,
            "churn_date":      churn_date,
            "monthly_revenue": PLAN_REVENUE[plan]
        })
    df = pd.DataFrame(records)
    df.to_csv(save_path, index=False)
    print(f"[DataGen] Subscribers → {save_path} | {len(df)} records")
    return df


def generate_watch_sessions(subscribers_df, content_df,
                             save_path="data/watch_sessions.csv"):
    records   = []
    sub_ids   = subscribers_df["subscriber_id"].tolist()
    cont_ids  = content_df["content_id"].tolist()
    cont_dur  = dict(zip(content_df["content_id"],
                         content_df["duration_mins"]))

    session_id = 1
    start = date(2024, 1, 1)

    for sub_id in sub_ids:
        n_sessions = np.random.randint(5, 80)
        for _ in range(n_sessions):
            content_id  = np.random.choice(cont_ids)
            max_dur     = cont_dur[content_id]
            watch_mins  = np.random.randint(5, max_dur + 1)
            comp_pct    = round(min(watch_mins / max_dur * 100, 100), 2)
            watch_date  = start + timedelta(days=np.random.randint(0, 365))
            # Prime time bias
            hour_probs  = np.ones(24)
            hour_probs[20:23] *= 4
            hour_probs[12:14] *= 2
            hour_probs  /= hour_probs.sum()
            records.append({
                "session_id":    f"WS{session_id:08d}",
                "subscriber_id": sub_id,
                "content_id":    content_id,
                "watch_date":    watch_date,
                "watch_hour":    np.random.choice(24, p=hour_probs),
                "watch_mins":    watch_mins,
                "completion_pct": comp_pct
            })
            session_id += 1

    df = pd.DataFrame(records)
    df.to_csv(save_path, index=False)
    print(f"[DataGen] Watch sessions → {save_path} | {len(df)} records")
    return df


def generate_revenue(subscribers_df, save_path="data/revenue.csv"):
    records = []
    months  = pd.period_range("2024-01", periods=12, freq="M")
    rid     = 1
    for _, row in subscribers_df.iterrows():
        for m in months:
            month_str = str(m)
            join_m    = pd.Period(str(row["join_date"])[:7], freq="M")
            if m < join_m:
                continue
            if row["churn_date"] is not None:
                churn_m = pd.Period(str(row["churn_date"])[:7], freq="M")
                if m > churn_m:
                    continue
            records.append({
                "revenue_id":    rid,
                "subscriber_id": row["subscriber_id"],
                "month":         month_str,
                "amount":        row["monthly_revenue"],
                "plan_type":     row["plan_type"]
            })
            rid += 1
    df = pd.DataFrame(records)
    df.to_csv(save_path, index=False)
    print(f"[DataGen] Revenue → {save_path} | {len(df)} records")
    return df


def generate_all():
    print("\n[DataGen] Generating OTT platform datasets...")
    content_df     = generate_content()
    subscribers_df = generate_subscribers()
    sessions_df    = generate_watch_sessions(subscribers_df, content_df)
    revenue_df     = generate_revenue(subscribers_df)
    print(f"\n[DataGen] Done. Total records: "
          f"{len(content_df)+len(subscribers_df)+len(sessions_df)+len(revenue_df):,}")
    return content_df, subscribers_df, sessions_df, revenue_df


if __name__ == "__main__":
    generate_all()
