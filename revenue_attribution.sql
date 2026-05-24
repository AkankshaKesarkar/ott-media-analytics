-- ============================================================
-- revenue_attribution.sql
-- Revenue KPIs: ARPU, MRR, Genre attribution, Regional revenue
-- ============================================================

-- 1. Monthly Recurring Revenue (MRR) Trend
SELECT
    r.month,
    r.plan_type,
    SUM(r.amount)                            AS monthly_revenue,
    COUNT(DISTINCT r.subscriber_id)          AS paying_subscribers,
    ROUND(SUM(r.amount) /
          COUNT(DISTINCT r.subscriber_id), 2) AS arpu,
    ROUND(SUM(r.amount) * 100.0 /
          SUM(SUM(r.amount)) OVER (PARTITION BY r.month), 2) AS revenue_share_pct
FROM revenue r
GROUP BY r.month, r.plan_type
ORDER BY r.month, monthly_revenue DESC;


-- 2. ARPU by Region
SELECT
    s.region,
    COUNT(DISTINCT s.subscriber_id)           AS subscribers,
    ROUND(SUM(r.amount), 2)                   AS total_revenue,
    ROUND(SUM(r.amount) /
          COUNT(DISTINCT s.subscriber_id), 2) AS arpu,
    ROUND(AVG(s.monthly_revenue), 2)          AS avg_plan_value
FROM subscribers s
LEFT JOIN revenue r ON s.subscriber_id = r.subscriber_id
GROUP BY s.region
ORDER BY arpu DESC;


-- 3. Revenue Attribution by Genre (What genres drive viewership that correlates with revenue)
SELECT
    c.genre,
    COUNT(DISTINCT ws.subscriber_id)          AS engaged_subscribers,
    SUM(r_agg.total_revenue)                  AS attributed_revenue,
    ROUND(AVG(ws.completion_pct), 2)          AS avg_engagement,
    ROUND(SUM(r_agg.total_revenue) * 100.0 /
          SUM(SUM(r_agg.total_revenue)) OVER (), 2) AS revenue_share_pct
FROM watch_sessions ws
JOIN content c ON ws.content_id = c.content_id
JOIN (
    SELECT subscriber_id, SUM(amount) AS total_revenue
    FROM revenue
    GROUP BY subscriber_id
) r_agg ON ws.subscriber_id = r_agg.subscriber_id
GROUP BY c.genre
ORDER BY attributed_revenue DESC;


-- 4. Subscriber Lifetime Value (LTV) Estimation
SELECT
    s.plan_type,
    s.region,
    COUNT(DISTINCT s.subscriber_id)                AS subscribers,
    ROUND(AVG(s.monthly_revenue), 2)               AS avg_monthly_revenue,
    ROUND(AVG(
        CASE
            WHEN s.churn_date IS NOT NULL
            THEN julianday(s.churn_date) - julianday(s.join_date)
            ELSE julianday('now') - julianday(s.join_date)
        END
    ) / 30.0, 1)                                   AS avg_tenure_months,
    ROUND(AVG(s.monthly_revenue) * AVG(
        CASE
            WHEN s.churn_date IS NOT NULL
            THEN julianday(s.churn_date) - julianday(s.join_date)
            ELSE julianday('now') - julianday(s.join_date)
        END
    ) / 30.0, 2)                                   AS estimated_ltv
FROM subscribers s
GROUP BY s.plan_type, s.region
ORDER BY estimated_ltv DESC;
