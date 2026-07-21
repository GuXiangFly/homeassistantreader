import json
import logging
import os
import time
from datetime import datetime, timezone

import requests
from dotenv import load_dotenv

from src.dao.homeassistant_pgsql_dao import HomeAssistantPgsqlDao

load_dotenv()

logger = logging.getLogger(__name__)


class HomeAssistantReader:
    def __init__(self, url: str, token: str):
        self.url = url.rstrip("/")
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }

    def get_state(self, entity_id: str) -> dict:
        resp = requests.get(
            f"{self.url}/api/states/{entity_id}",
            headers=self.headers,
        )
        resp.raise_for_status()
        return resp.json()

    def get_states(self) -> list[dict]:
        """
        获取 Home Assistant 中所有实体的状态列表.

        @auther guxiang
        @date 2026-07-21
        """
        resp = requests.get(
            f"{self.url}/api/states",
            headers=self.headers,
        )
        resp.raise_for_status()
        return resp.json()

    def get_states_by_entity_list(self, entity_id_list: list[str]) -> list[dict]:
        """
        根据实体 ID 列表获取状态（先拉取全部再本地过滤）.

        @auther guxiang
        @date 2026-07-21
        """
        all_states = self.get_states()
        print("end get_states_by_entity_list")
        entity_set = set(entity_id_list)
        return [s for s in all_states if s.get("entity_id") in entity_set]

    def get_power(self, entity_id: str) -> tuple[str, str]:
        data = self.get_state(entity_id)
        return data["state"], data["attributes"]["unit_of_measurement"]

    def _collect_and_store(self, entity_id: str, dao: HomeAssistantPgsqlDao) -> None:
        """读取指定传感器功率并写入数据库."""
        try:
            state, unit = self.get_power(entity_id)
            logger.info("entity_id: %s 当前功率: %s %s", entity_id, state, unit)

            try:
                power_value = float(state)
                dao.insert_metric(
                    metric_time=datetime.now(timezone.utc),
                    sensor_name=entity_id,
                    sensor_value=power_value,
                )
            except ValueError:
                logger.warning("功率值无法转换为数字: %s", state)
            except Exception:
                logger.exception("数据库写入失败")

        except requests.RequestException:
            logger.exception("请求失败")

    def _collect_entity_list_and_batch_store(
        self,
        entity_id_list: list[str],
        dao: HomeAssistantPgsqlDao,
    ) -> None:
        """
        批量读取指定传感器列表的功率并写入数据库.

        @auther guxiang
        @date 2026-07-21
        """
        try:
            states = self.get_states_by_entity_list(entity_id_list)
        except requests.RequestException:
            logger.exception("批量请求失败")
            return

        logger.info("_collect_entity_list_and_batch_store.entity_id_list: %s", entity_id_list)

        records = []
        for data in states:
            entity_id = data.get("entity_id")
            try:
                state = data["state"]
                unit = data["attributes"]["unit_of_measurement"]
                logger.info("entity_id: %s 当前功率: %s %s", entity_id, state, unit)
                power_value = float(state)
                records.append(
                    (
                        datetime.now(timezone.utc),
                        entity_id,
                        power_value,
                    )
                )
            except (ValueError, KeyError):
                logger.warning("功率值无法解析: %s", data.get("state"))
            except Exception:
                logger.exception("数据处理失败: %s", entity_id)

        if records:
            try:
                dao.insert_metrics_batch(records)
                logger.info("批量写入 %d 条记录", len(records))
            except Exception:
                logger.exception("数据库批量写入失败")

    def main_process(self) -> None:
        dao = HomeAssistantPgsqlDao()
        print("start_init_table")
        dao.init_table()
        print("end_init_table")

        raw_entity_ids = os.getenv(
            "HA_ENTITY_IDS",
            "sensor.iot_cn_2047343303_padw2p_electric_power_p_3_3,"
            "sensor.cuco_cn_534987372_cp5prd_electric_power_p_10_5,"
            "sensor.cuco_cn_699137676_v3_electric_power_p_11_2",
        )
        entity_id_list = [e.strip() for e in raw_entity_ids.split(",") if e.strip()]

        while True:
            start_time = time.perf_counter()
            self._collect_entity_list_and_batch_store(entity_id_list, dao)
            elapsed = time.perf_counter() - start_time
            sleep_time = max(0, 5 - elapsed)
            logger.info("本轮采集耗时: %.3f s   sleep_time  %.3f s", elapsed,sleep_time)
            time.sleep(sleep_time)


if __name__ == "__main__":

    reader = HomeAssistantReader(
        url=os.getenv("HA_URL", "http://192.168.31.222:8123"),
        token=os.getenv("HA_TOKEN", ""),
    )
    reader.main_process()
