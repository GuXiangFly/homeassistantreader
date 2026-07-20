import os
import time

import requests
from dotenv import load_dotenv

load_dotenv()


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


def main() -> None:
    reader = HomeAssistantReader(
        url=os.getenv("HA_URL", "http://192.168.31.222:8123"),
        token=os.getenv("HA_TOKEN", ""),
    )
    entity_id = "sensor.iot_cn_2047343303_padw2p_electric_power_p_3_3"

    while True:
        try:
            state, unit = reader.get_power(entity_id)
            print(f"当前功率: {state} {unit}")
        except requests.RequestException as e:
            print(f"请求失败: {e}")
        time.sleep(5)


if __name__ == "__main__":
    main()