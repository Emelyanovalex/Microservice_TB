import requests
import logging

logger = logging.getLogger(__name__)

class TbDevice:
    def __init__(self, url: str, headers: dict, device_data: dict):
        self.url = url
        self.headers = headers
        self.device_id = device_data.get("id", {}).get("id")

        if not self.device_id:
            logger.error("Не удалось извлечь device_id из данных устройства.")
            raise ValueError("Invalid device data: missing device ID")

    def get_data(self) -> dict:
        logger.info(f"Получение телеметрии для устройства ID: {self.device_id}")
        try:
            response = requests.get(
                f"{self.url}/api/plugins/telemetry/DEVICE/{self.device_id}/values/timeseries",
                headers=self.headers
            )
            response.raise_for_status()
            logger.info("Телеметрия получена успешно.")
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Ошибка при получении телеметрии: {e}")
            raise ConnectionError("Failed to retrieve telemetry data") from e
