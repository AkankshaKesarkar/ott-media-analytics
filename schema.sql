-- ============================================================
-- schema.sql — OTT Media Analytics Platform Database Schema
-- Compatible: SQLite / MySQL / PostgreSQL
-- ============================================================

CREATE TABLE IF NOT EXISTS content (
    content_id      VARCHAR(10)     PRIMARY KEY,
    title           VARCHAR(200)    NOT NULL,
    genre           VARCHAR(50)     NOT NULL,
    content_type    VARCHAR(20)     NOT NULL,
    release_year    INTEGER         NOT NULL,
    duration_mins   INTEGER         NOT NULL,
    language        VARCHAR(30)     NOT NULL,
    production_cost DECIMAL(12,2)
);

CREATE TABLE IF NOT EXISTS subscribers (
    subscriber_id   VARCHAR(10)     PRIMARY KEY,
    region          VARCHAR(50)     NOT NULL,
    device_type     VARCHAR(30)     NOT NULL,
    plan_type       VARCHAR(20)     NOT NULL,
    join_date       DATE            NOT NULL,
    churn_date      DATE,
    monthly_revenue DECIMAL(8,2)    NOT NULL
);

CREATE TABLE IF NOT EXISTS watch_sessions (
    session_id      VARCHAR(15)     PRIMARY KEY,
    subscriber_id   VARCHAR(10)     NOT NULL,
    content_id      VARCHAR(10)     NOT NULL,
    watch_date      DATE            NOT NULL,
    watch_hour      INTEGER         NOT NULL,
    watch_mins      INTEGER         NOT NULL,
    completion_pct  DECIMAL(5,2)    NOT NULL,
    FOREIGN KEY (subscriber_id) REFERENCES subscribers(subscriber_id),
    FOREIGN KEY (content_id)    REFERENCES content(content_id)
);

CREATE TABLE IF NOT EXISTS revenue (
    revenue_id      INTEGER         PRIMARY KEY AUTOINCREMENT,
    subscriber_id   VARCHAR(10)     NOT NULL,
    month           VARCHAR(7)      NOT NULL,
    amount          DECIMAL(8,2)    NOT NULL,
    plan_type       VARCHAR(20)     NOT NULL,
    FOREIGN KEY (subscriber_id) REFERENCES subscribers(subscriber_id)
);

-- Indexes for analytical query performance
CREATE INDEX IF NOT EXISTS idx_sessions_date    ON watch_sessions(watch_date);
CREATE INDEX IF NOT EXISTS idx_sessions_sub     ON watch_sessions(subscriber_id);
CREATE INDEX IF NOT EXISTS idx_sessions_content ON watch_sessions(content_id);
CREATE INDEX IF NOT EXISTS idx_revenue_month    ON revenue(month);
CREATE INDEX IF NOT EXISTS idx_sub_plan         ON subscribers(plan_type);
