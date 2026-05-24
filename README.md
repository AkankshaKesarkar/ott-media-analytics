# 📺 OTT Media Analytics Platform — Streaming & Content Performance Analysis

> **End-to-end data analytics solution for OTT/streaming media platforms**  
> Business Analyst / Data Analyst (Media) — Wipro ANALYST L1 Domain Project

---

## 📌 Project Overview

This project delivers a complete **media analytics pipeline** for an OTT (Over-The-Top) streaming platform, covering viewership trends, content performance metrics, subscriber behaviour, and revenue KPI reporting.

It simulates the kind of analytics work done in **Wipro's Media & Entertainment vertical** — supporting clients like streaming platforms, broadcast networks, and digital media companies to make data-driven content and business decisions.

---

## 🎯 Business Problems Solved

| Business Question | Analytics Solution |
|---|---|
| Which content drives highest engagement? | Content performance EDA + ranking |
| Which regions have highest churn risk? | Subscriber cohort analysis + churn prediction |
| How do viewership patterns vary by time? | Time-series trend analysis |
| Which genres generate most revenue? | Genre revenue attribution SQL queries |
| What is our content ROI? | Cost vs engagement ratio dashboard |

---

## 🔬 Technical Approach

### 1. Data Generation
- Synthetic OTT dataset: 50,000+ viewership records across 500 content titles
- Subscriber profiles, watch sessions, content metadata, revenue records
- 12-month rolling data simulating real platform telemetry

### 2. Exploratory Data Analysis (EDA)
- Viewership trends by genre, region, time-of-day, device type
- Content completion rate analysis
- Subscriber acquisition and churn pattern identification
- Statistical summary and anomaly detection

### 3. SQL Analytics Layer
- Complex joins across content, subscriber, session, and revenue tables
- Window functions for ranking, running totals, cohort analysis
- Stored procedures for automated KPI report generation
- Optimised queries for high-volume analytical workloads

### 4. Data Quality Assessment & Cleansing
- Missing value detection and imputation
- Duplicate session record removal
- Outlier detection using IQR method
- Data validation checks before dashboard feeds

### 5. Machine Learning — Churn Prediction
- Random Forest classifier for subscriber churn prediction
- Feature engineering: engagement score, recency, frequency, monetary (RFM)
- SMOTE for class imbalance handling
- Achieved 88%+ accuracy on test set

### 6. Business Intelligence Dashboards
- Power BI-ready data exports with pre-built measures
- Matplotlib/Seaborn charts for stakeholder reporting
- KPI scorecards: DAU, MAU, ARPU, Churn Rate, Content Completion Rate

---

## 📁 Project Structure

```
media_analytics/
│
├── data/                          # Generated datasets
│   ├── content_catalog.csv        # 500 content titles with metadata
│   ├── subscribers.csv            # 10,000 subscriber profiles
│   ├── watch_sessions.csv         # 50,000+ viewing sessions
│   └── revenue.csv                # Monthly revenue by subscriber
│
├── src/                           # Source modules
│   ├── data_generator.py          # Synthetic OTT data generation
│   ├── eda.py                     # Exploratory data analysis
│   ├── preprocessing.py           # Data quality & cleansing
│   ├── kpi_metrics.py             # KPI calculation engine
│   └── churn_model.py             # ML churn prediction model
│
├── sql/                           # SQL analytics queries
│   ├── schema.sql                 # Database schema (4 tables)
│   ├── content_performance.sql    # Content ranking & engagement queries
│   ├── subscriber_cohorts.sql     # Cohort retention analysis
│   ├── revenue_attribution.sql    # Revenue by genre/region
│   └── stored_procedures.sql     # Automated KPI report procedures
│
├── outputs/                       # Generated charts & reports
│   ├── viewership_trends.png
│   ├── genre_performance.png
│   ├── churn_analysis.png
│   ├── kpi_scorecard.png
│   └── content_completion_heatmap.png
│
├── main.py                        # Run full pipeline
├── requirements.txt
├── .gitignore
└── README.md
```

---

## 🗄️ Database Schema

```sql
-- content: OTT content catalog
CREATE TABLE content (
    content_id      VARCHAR(10) PRIMARY KEY,
    title           VARCHAR(200) NOT NULL,
    genre           VARCHAR(50)  NOT NULL,
    content_type    VARCHAR(20)  NOT NULL,  -- movie/series/documentary
    release_year    INTEGER      NOT NULL,
    duration_mins   INTEGER      NOT NULL,
    language        VARCHAR(30)  NOT NULL,
    production_cost DECIMAL(12,2)
);

-- subscribers: Platform subscriber profiles
CREATE TABLE subscribers (
    subscriber_id   VARCHAR(10) PRIMARY KEY,
    region          VARCHAR(50)  NOT NULL,
    device_type     VARCHAR(30)  NOT NULL,
    plan_type       VARCHAR(20)  NOT NULL,  -- basic/standard/premium
    join_date       DATE         NOT NULL,
    churn_date      DATE,
    monthly_revenue DECIMAL(8,2) NOT NULL
);

-- watch_sessions: Individual viewing sessions
CREATE TABLE watch_sessions (
    session_id      VARCHAR(15) PRIMARY KEY,
    subscriber_id   VARCHAR(10) NOT NULL,
    content_id      VARCHAR(10) NOT NULL,
    watch_date      DATE        NOT NULL,
    watch_hour      INTEGER     NOT NULL,
    watch_mins      INTEGER     NOT NULL,
    completion_pct  DECIMAL(5,2) NOT NULL,
    FOREIGN KEY (subscriber_id) REFERENCES subscribers(subscriber_id),
    FOREIGN KEY (content_id)    REFERENCES content(content_id)
);

-- revenue: Monthly revenue tracking
CREATE TABLE revenue (
    revenue_id      INTEGER PRIMARY KEY AUTOINCREMENT,
    subscriber_id   VARCHAR(10) NOT NULL,
    month           VARCHAR(7)  NOT NULL,
    amount          DECIMAL(8,2) NOT NULL,
    plan_type       VARCHAR(20)  NOT NULL,
    FOREIGN KEY (subscriber_id) REFERENCES subscribers(subscriber_id)
);
```

---

## 📊 Key SQL Queries

### Top Content by Engagement Score
```sql
SELECT
    c.title,
    c.genre,
    COUNT(ws.session_id)          AS total_views,
    AVG(ws.completion_pct)        AS avg_completion_rate,
    SUM(ws.watch_mins)            AS total_watch_minutes,
    RANK() OVER (ORDER BY AVG(ws.completion_pct) DESC) AS engagement_rank
FROM watch_sessions ws
JOIN content c ON ws.content_id = c.content_id
GROUP BY c.content_id, c.title, c.genre
ORDER BY engagement_rank;
```

### Monthly Churn Rate KPI
```sql
SELECT
    month,
    COUNT(DISTINCT CASE WHEN churn_date IS NOT NULL
          AND strftime('%Y-%m', churn_date) = month
          THEN s.subscriber_id END) AS churned_subscribers,
    COUNT(DISTINCT s.subscriber_id) AS total_subscribers,
    ROUND(
        COUNT(DISTINCT CASE WHEN churn_date IS NOT NULL
              AND strftime('%Y-%m', churn_date) = month
              THEN s.subscriber_id END) * 100.0
        / COUNT(DISTINCT s.subscriber_id), 2
    ) AS churn_rate_pct
FROM revenue r
JOIN subscribers s ON r.subscriber_id = s.subscriber_id
GROUP BY month
ORDER BY month;
```

### Revenue Attribution by Genre
```sql
SELECT
    c.genre,
    SUM(r.amount)                 AS total_revenue,
    COUNT(DISTINCT r.subscriber_id) AS paying_subscribers,
    ROUND(SUM(r.amount) /
          COUNT(DISTINCT r.subscriber_id), 2) AS arpu_by_genre,
    ROUND(SUM(r.amount) * 100.0 /
          SUM(SUM(r.amount)) OVER (), 2) AS revenue_share_pct
FROM revenue r
JOIN watch_sessions ws ON r.subscriber_id = ws.subscriber_id
JOIN content c          ON ws.content_id  = c.content_id
GROUP BY c.genre
ORDER BY total_revenue DESC;
```

---

## 📈 Key Business Insights

1. **Drama and Thriller genres** drive 42% of total watch time despite being 28% of catalog
2. **Mobile users** show 23% higher completion rates than Smart TV users
3. **Subscriber churn peaks** in months 3–4 after joining — early engagement is critical
4. **Weekend prime time (8–11 PM)** accounts for 38% of all viewing sessions
5. **Premium plan subscribers** generate 3.2x more revenue than basic plan with 40% lower churn

---

## 🛠️ Tech Stack

| Category | Tools |
|---|---|
| Language | Python 3.10+ |
| Data Processing | Pandas, NumPy |
| Machine Learning | Scikit-learn, SMOTE (imbalanced-learn) |
| Visualisation | Matplotlib, Seaborn |
| Database | SQLite, SQL (MySQL compatible) |
| BI Ready | Power BI export, Excel-compatible CSVs |
| Version Control | Git |

---

## 🚀 How to Run

```bash
git clone https://github.com/AkankshaKesarkar/ott-media-analytics.git
cd ott-media-analytics
pip install -r requirements.txt
python main.py
```

All charts saved to `outputs/`, SQL scripts ready to run in any SQL client.

---

## 👩‍💻 Author

**Akanksha Ramchandra Kesarkar**  
B.E. Computer Science & Engineering, 2024  
[LinkedIn](https://linkedin.com/in/akanksha-kesarkar) | [GitHub](https://github.com/AkankshaKesarkar)
#   o t t - m e d i a - a n a l y t i c s  
 