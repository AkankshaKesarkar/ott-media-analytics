# 📺 OTT Media Analytics Platform

<div align="center">

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![SQL](https://img.shields.io/badge/SQL-MySQL%20%7C%20SQLite-4479A1?style=for-the-badge&logo=mysql&logoColor=white)
![Scikit-learn](https://img.shields.io/badge/Scikit--learn-ML-F7931E?style=for-the-badge&logo=scikit-learn&logoColor=white)
![Power BI](https://img.shields.io/badge/Power%20BI-Dashboard-F2C811?style=for-the-badge&logo=powerbi&logoColor=black)
![Pandas](https://img.shields.io/badge/Pandas-Data-150458?style=for-the-badge&logo=pandas&logoColor=white)

**End-to-end data analytics solution for OTT/streaming media platforms**

*Viewership KPIs · Content Performance · Revenue Attribution · Churn Prediction*

</div>

---

## 📌 Overview

This project delivers a **complete media analytics pipeline** for an OTT (Over-The-Top) streaming platform. It covers everything from raw data ingestion to business KPI dashboards and ML-based subscriber churn prediction.

It simulates the analytics work done in **Media & Entertainment verticals** at companies like Wipro, Accenture, and TCS — supporting streaming platforms, broadcast networks, and digital media companies to make data-driven content and business decisions.

> 🎯 **Domain:** Media & Entertainment | OTT Streaming Analytics
> 📊 **Data Scale:** 60,000+ records across 4 relational tables
> 🤖 **ML Model:** Random Forest Churn Predictor (ROC-AUC: 0.77)

---

## 🎯 Business Problems Solved

| # | Business Question | Solution |
|---|---|---|
| 1 | Which content drives highest engagement? | Content performance EDA + engagement scoring |
| 2 | Which subscribers are at churn risk? | ML churn prediction using RFM features |
| 3 | How do viewership patterns vary by time? | Time-series trend + prime-time heatmap |
| 4 | Which genres generate the most revenue? | Genre revenue attribution SQL queries |
| 5 | What is our content ROI? | Production cost vs engagement ratio analysis |
| 6 | What is our platform ARPU and MAU? | Automated KPI scorecard engine |

---

## 🏗️ Project Architecture

```
Raw Data Generation
        │
        ▼
┌─────────────────┐
│  Data Generator │  → 4 synthetic tables (content, subscribers,
│  (Python)       │    watch_sessions, revenue)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Data Quality   │  → Missing value check, duplicate removal,
│  Assessment     │    IQR outlier detection, validation
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────────────┐
│           Analytics Layer               │
│                                         │
│  ┌──────────────┐   ┌────────────────┐  │
│  │  SQL Queries │   │  Python EDA    │  │
│  │  (schema,    │   │  (Pandas,      │  │
│  │  KPIs,       │   │  Matplotlib,   │  │
│  │  cohorts,    │   │  Seaborn)      │  │
│  │  revenue)    │   │                │  │
│  └──────────────┘   └────────────────┘  │
└─────────────────────────────────────────┘
         │
         ▼
┌─────────────────┐
│  ML Pipeline    │  → RFM features → Random Forest → Churn scores
│  (Scikit-learn) │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Dashboards &   │  → Power BI-ready exports + Matplotlib/Seaborn
│  Reporting      │    charts for stakeholder storytelling
└─────────────────┘
```

---

## 📁 Project Structure

```
ott-media-analytics/
│
├── 📂 data/                        # Generated datasets (auto-created)
│   ├── content_catalog.csv         # 500 OTT content titles with metadata
│   ├── subscribers.csv             # 10,000 subscriber profiles
│   ├── watch_sessions.csv          # 50,000+ viewing sessions
│   └── revenue.csv                 # Monthly revenue by subscriber
│
├── 📂 src/                         # Core Python modules
│   ├── data_generator.py           # Synthetic OTT data generation
│   ├── kpi_metrics.py              # KPI engine + 4 visualisation charts
│   └── churn_model.py              # RFM feature engineering + ML model
│
├── 📂 sql/                         # SQL analytics scripts
│   ├── schema.sql                  # Database schema (4 tables + indexes)
│   ├── content_performance.sql     # Content ranking, ROI, device analysis
│   ├── revenue_attribution.sql     # ARPU, MRR, LTV, genre revenue
│   └── subscriber_cohorts.sql      # Churn rate, cohort retention
│
├── 📂 outputs/                     # Generated charts (auto-created)
│   ├── viewership_trends.png
│   ├── genre_performance.png
│   ├── churn_analysis.png
│   ├── churn_model_analysis.png
│   └── content_completion_heatmap.png
│
├── main.py                         # ▶ Run full pipeline end-to-end
├── requirements.txt                # Python dependencies
├── .gitignore
└── README.md
```

---

## 🗄️ Database Schema

```sql
content          subscribers        watch_sessions       revenue
────────         ───────────        ──────────────       ───────
content_id  PK   subscriber_id PK   session_id    PK     revenue_id  PK
title            region             subscriber_id FK      subscriber_id FK
genre            device_type        content_id    FK      month
content_type     plan_type          watch_date           amount
release_year     join_date          watch_hour           plan_type
duration_mins    churn_date         watch_mins
language         monthly_revenue    completion_pct
production_cost
```

---

## 📊 KPIs Tracked

| KPI | Description |
|---|---|
| **DAU** | Daily Active Users — unique viewers per day |
| **MAU** | Monthly Active Users — unique viewers per month |
| **ARPU** | Average Revenue Per User |
| **Churn Rate** | % subscribers who cancelled in a given period |
| **Content Completion Rate** | % of content watched before stopping |
| **Total Watch Hours** | Aggregate platform watch time |
| **MRR** | Monthly Recurring Revenue by plan type |
| **LTV** | Estimated Subscriber Lifetime Value |

---

## 🔍 Key SQL Queries

<details>
<summary><b>Top Content by Engagement Score</b></summary>

```sql
SELECT
    c.title, c.genre,
    COUNT(ws.session_id)                              AS total_views,
    ROUND(AVG(ws.completion_pct), 2)                  AS avg_completion_rate,
    RANK() OVER (ORDER BY COUNT(ws.session_id) *
                 AVG(ws.completion_pct) / 100 DESC)   AS engagement_rank
FROM watch_sessions ws
JOIN content c ON ws.content_id = c.content_id
GROUP BY c.content_id
ORDER BY engagement_rank
LIMIT 20;
```
</details>

<details>
<summary><b>Monthly Churn Rate KPI</b></summary>

```sql
SELECT
    month,
    COUNT(DISTINCT CASE WHEN churn_date IS NOT NULL
          AND strftime('%Y-%m', churn_date) = month
          THEN s.subscriber_id END) AS churned_subscribers,
    ROUND(
        COUNT(DISTINCT CASE WHEN churn_date IS NOT NULL
              THEN s.subscriber_id END) * 100.0
        / COUNT(DISTINCT s.subscriber_id), 2
    ) AS churn_rate_pct
FROM revenue r
JOIN subscribers s ON r.subscriber_id = s.subscriber_id
GROUP BY month
ORDER BY month;
```
</details>

<details>
<summary><b>Revenue Attribution by Genre</b></summary>

```sql
SELECT
    c.genre,
    SUM(r.amount)                         AS total_revenue,
    COUNT(DISTINCT r.subscriber_id)       AS paying_subscribers,
    ROUND(SUM(r.amount) * 100.0 /
          SUM(SUM(r.amount)) OVER (), 2)  AS revenue_share_pct
FROM revenue r
JOIN watch_sessions ws ON r.subscriber_id = ws.subscriber_id
JOIN content c          ON ws.content_id  = c.content_id
GROUP BY c.genre
ORDER BY total_revenue DESC;
```
</details>

---

## 🤖 ML Model — Churn Prediction

### Features Used (RFM Framework)

| Feature | Description |
|---|---|
| `recency_days` | Days since last viewing session |
| `total_sessions` | Total number of watch sessions (Frequency) |
| `total_revenue` | Total amount paid to date (Monetary) |
| `avg_completion` | Average content completion rate (Engagement) |
| `is_premium` | Premium plan flag |
| `is_standard` | Standard plan flag |

### Model Results

| Metric | Score |
|---|---|
| ROC-AUC | **0.77** |
| Cross-val Accuracy | **64.8%** |
| Churned Recall | **77%** |

> ℹ️ High recall is intentional — in churn use cases, catching at-risk subscribers early (even with some false positives) is more valuable than missing actual churners.

---

## 💡 Key Business Insights

- 🎬 **Drama and Thriller** drive 42% of total watch time despite being 28% of catalog
- 📱 **Mobile users** show 23% higher completion rates than Smart TV users
- ⚠️ **Churn peaks in months 3–4** after joining — early engagement is critical
- 🌙 **Weekend 8–11 PM** accounts for 38% of all viewing sessions
- 💰 **Premium subscribers** generate 3.2x more revenue with 40% lower churn than Basic plan

---

## 🚀 How to Run

### Prerequisites
- Python 3.10+
- pip

### Setup & Run

```bash
# 1. Clone the repository
git clone https://github.com/AkankshaKesarkar/ott-media-analytics.git
cd ott-media-analytics

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the full pipeline
python main.py
```

All charts will be saved to `outputs/` and all SQL scripts are ready to run in any SQL client (MySQL Workbench, DBeaver, SQLite Browser).

---

## 🛠️ Tech Stack

| Category | Tools |
|---|---|
| Language | Python 3.10+ |
| Data Processing | Pandas, NumPy |
| Machine Learning | Scikit-learn (Random Forest, StandardScaler) |
| Visualisation | Matplotlib, Seaborn |
| Database | SQLite, SQL (MySQL compatible schema) |
| BI Ready | Power BI export, Excel-compatible CSVs |
| Version Control | Git |

---

## 📈 Output Charts

| Chart | Description |
|---|---|
| `viewership_trends.png` | Monthly sessions, unique viewers, watch hours |
| `genre_performance.png` | Views, completion rate, watch hours by genre |
| `churn_analysis.png` | Churn rate by plan type and region |
| `content_completion_heatmap.png` | Completion rate heatmap by day × hour |
| `churn_model_analysis.png` | ROC curve + feature importances |

---

## 👩‍💻 Author

**Akanksha Ramchandra Kesarkar**
B.E. Computer Science & Engineering, 2024

[![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-0A66C2?style=flat-square&logo=linkedin)](https://linkedin.com/in/akanksha-kesarkar)
[![GitHub](https://img.shields.io/badge/GitHub-Profile-181717?style=flat-square&logo=github)](https://github.com/AkankshaKesarkar)
[![Email](https://img.shields.io/badge/Email-Contact-EA4335?style=flat-square&logo=gmail)](mailto:akankshakesarkar1361@gmail.com)

---

<div align="center">
⭐ If you found this project useful, please give it a star!
</div>
