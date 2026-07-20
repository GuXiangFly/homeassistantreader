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

    def main_process(self) -> None:
        dao = HomeAssistantPgsqlDao()
        dao.init_table()

        entity_id_list = [
            "sensor.iot_cn_2047343303_padw2p_electric_power_p_3_3",
            "sensor.cuco_cn_534987372_cp5prd_electric_power_p_10_5",
        ]

        while True:
            for entity_id in entity_id_list:
                self._collect_and_store(entity_id, dao)
            time.sleep(5)


if __name__ == "__main__":

    reader = HomeAssistantReader(
        url=os.getenv("HA_URL", "http://192.168.31.222:8123"),
        token=os.getenv("HA_TOKEN", ""),
    )
    reader.main_process()