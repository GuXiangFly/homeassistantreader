import os
from contextlib import contextmanager
from datetime import datetime
from typing import Optional

import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv()


class HomeAssistantPgsqlDao:
    """Home Assistant 传感器数据 PostgreSQL 存储."""

    def __init__(self) -> None:
        self.conn_params = {
            "host": os.getenv("PG_HOST", "192.168.31.109"),
            "port": os.getenv("PG_PORT", "5432"),
            "dbname": os.getenv("PG_DBNAME", "homeassistant_reader_db"),
            "user": os.getenv("PG_USER", "teslamate"),
            "password": os.getenv("PG_PASSWORD", "password"),
        }

    @contextmanager
    def _get_cursor(self, cursor_factory=None):
        """获取数据库游标的上下文管理器，自动处理提交/回滚/关闭."""
        conn = psycopg2.connect(**self.conn_params)
        cursor = None
        try:
            cursor = conn.cursor(cursor_factory=cursor_factory)
            yield cursor
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            if cursor is not None:
                cursor.close()
            conn.close()

    def init_table(self) -> None:
        """初始化表结构（若不存在则创建）."""
        sql = """
        CREATE TABLE IF NOT EXISTS sensor_metrics (
            id              BIGSERIAL PRIMARY KEY,
            metric_time     TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            sensor_name     VARCHAR(256) NOT NULL,
            sensor_value    DOUBLE PRECISION NOT NULL
        );

        CREATE INDEX IF NOT EXISTS idx_sensor_metrics_time
            ON sensor_metrics(metric_time DESC);

        CREATE INDEX IF NOT EXISTS idx_sensor_metrics_name_time
            ON sensor_metrics(sensor_name, metric_time DESC);
        """
        with self._get_cursor() as cur:
            cur.execute(sql)

    def insert_metric(
        self,
        metric_time: datetime,
        sensor_name: str,
        sensor_value: float,
    ) -> None:
        """插入一条传感器指标记录."""
        sql = """
        INSERT INTO sensor_metrics (metric_time, sensor_name, sensor_value)
        VALUES (%s, %s, %s)
        """
        with self._get_cursor() as cur:
            cur.execute(sql, (metric_time, sensor_name, sensor_value))

    def get_latest_metric(self, sensor_name: str) -> Optional[dict]:
        """获取指定传感器的最新一条记录."""
        sql = """
        SELECT id, metric_time, sensor_name, sensor_value
        FROM sensor_metrics
        WHERE sensor_name = %s
        ORDER BY metric_time DESC
        LIMIT 1
        """
        with self._get_cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(sql, (sensor_name,))
            return cur.fetchone()

    def get_metrics_by_time_range(
        self,
        sensor_name: str,
        start: datetime,
        end: datetime,
    ) -> list[dict]:
        """按时间范围查询指定传感器的历史记录."""
        sql = """
        SELECT id, metric_time, sensor_name, sensor_value
        FROM sensor_metrics
        WHERE sensor_name = %s AND metric_time BETWEEN %s AND %s
        ORDER BY metric_time DESC
        """
        with self._get_cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(sql, (sensor_name, start, end))
            return cur.fetchall()