-- 传感器指标表
CREATE TABLE IF NOT EXISTS sensor_metrics (
    id              BIGSERIAL PRIMARY KEY,
    metric_time     TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    sensor_name     VARCHAR(256) NOT NULL,
    sensor_value    DOUBLE PRECISION NOT NULL
);

-- 按时间查询（最近 N 条、时间段范围）
CREATE INDEX idx_sensor_metrics_time
    ON sensor_metrics(metric_time DESC);

-- 按传感器 + 时间查询（单个传感器的历史趋势）
CREATE INDEX idx_sensor_metrics_name_time
    ON sensor_metrics(sensor_name, metric_time DESC);