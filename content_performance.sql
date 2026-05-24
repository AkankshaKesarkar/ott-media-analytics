-- ============================================================
-- content_performance.sql
-- Content ranking, engagement metrics, and ROI queries
-- ============================================================

-- 1. Top 20 Content by Engagement Score (Completion Rate x Views)
SELECT
    c.content_id,
    c.title,
    c.genre,
    c.content_type,
    c.language,
    COUNT(ws.session_id)                              AS total_views,
    ROUND(AVG(ws.completion_pct), 2)                  AS avg_completion_rate,
    SUM(ws.watch_mins)                                AS total_watch_mins,
    ROUND(SUM(ws.watch_mins) / 60.0, 1)               AS total_watch_hours,
    ROUND(COUNT(ws.session_id) * AVG(ws.completion_pct) / 100, 2) AS engagement_score,
    RANK() OVER (ORDER BY COUNT(ws.session_id) *
                 AVG(ws.completion_pct) / 100 DESC)   AS engagement_rank
FROM watch_sessions ws
JOIN content c ON ws.content_id = c.content_id
GROUP BY c.content_id, c.title, c.genre, c.content_type, c.language
ORDER BY engagement_rank
LIMIT 20;


-- 2. Genre Performance Summary
SELECT
    c.genre,
    COUNT(DISTINCT c.content_id)         AS content_count,
    COUNT(ws.session_id)                 AS total_views,
    ROUND(AVG(ws.completion_pct), 2)     AS avg_completion_pct,
    ROUND(SUM(ws.watch_mins)/60.0, 1)    AS total_watch_hours,
    COUNT(DISTINCT ws.subscriber_id)     AS unique_viewers,
    ROUND(COUNT(ws.session_id) * 1.0 /
          COUNT(DISTINCT c.content_id), 1) AS views_per_title
FROM watch_sessions ws
JOIN content c ON ws.content_id = c.content_id
GROUP BY c.genre
ORDER BY total_views DESC;


-- 3. Content ROI — Production Cost vs Engagement
SELECT
    c.title,
    c.genre,
    c.production_cost,
    COUNT(ws.session_id)                           AS total_views,
    ROUND(SUM(ws.watch_mins)/60.0, 1)              AS watch_hours,
    ROUND(c.production_cost /
          NULLIF(COUNT(ws.session_id), 0), 2)      AS cost_per_view,
    ROUND(c.production_cost /
          NULLIF(SUM(ws.watch_mins)/60.0, 0), 2)   AS cost_per_watch_hour,
    CASE
        WHEN c.production_cost /
             NULLIF(COUNT(ws.session_id), 0) < 500 THEN 'High ROI'
        WHEN c.production_cost /
             NULLIF(COUNT(ws.session_id), 0) < 2000 THEN 'Medium ROI'
        ELSE 'Low ROI'
    END AS roi_category
FROM content c
LEFT JOIN watch_sessions ws ON c.content_id = ws.content_id
WHERE c.production_cost IS NOT NULL
GROUP BY c.content_id, c.title, c.genre, c.production_cost
ORDER BY cost_per_view ASC
LIMIT 30;


-- 4. Peak Viewing Hours Analysis
SELECT
    ws.watch_hour,
    COUNT(ws.session_id)                     AS total_sessions,
    COUNT(DISTINCT ws.subscriber_id)         AS unique_viewers,
    ROUND(AVG(ws.completion_pct), 2)         AS avg_completion_pct,
    ROUND(SUM(ws.watch_mins)/60.0, 1)        AS total_watch_hours,
    CASE
        WHEN ws.watch_hour BETWEEN 20 AND 22 THEN 'Prime Time'
        WHEN ws.watch_hour BETWEEN 12 AND 14 THEN 'Lunch Hour'
        WHEN ws.watch_hour BETWEEN 6  AND 9  THEN 'Morning'
        WHEN ws.watch_hour BETWEEN 23 AND 24
          OR ws.watch_hour BETWEEN 0  AND 2  THEN 'Late Night'
        ELSE 'Off Peak'
    END AS time_slot
FROM watch_sessions ws
GROUP BY ws.watch_hour
ORDER BY total_sessions DESC;


-- 5. Device Type Performance
SELECT
    s.device_type,
    COUNT(DISTINCT ws.subscriber_id)     AS unique_viewers,
    COUNT(ws.session_id)                 AS total_sessions,
    ROUND(AVG(ws.completion_pct), 2)     AS avg_completion_pct,
    ROUND(AVG(ws.watch_mins), 1)         AS avg_session_mins,
    ROUND(SUM(ws.watch_mins)/60.0, 1)    AS total_watch_hours
FROM watch_sessions ws
JOIN subscribers s ON ws.subscriber_id = s.subscriber_id
GROUP BY s.device_type
ORDER BY avg_completion_pct DESC;
