import requests
import logging
from tb_device import TbDevice

logger = logging.getLogger(__name__)

class TbApi:
    def __init__(self, url: str, username: str, password: str, is_customer: bool = False):
        self.url = url
        self.username = username
        self.password = password
        self.is_customer = is_customer
        self.token = self.login()

    def login(self) -> str:
        logger.info("Авторизация в ThingsBoard...")
        try:
            response = requests.post(
                f"{self.url}/api/auth/login",
                json={"username": self.username, "password": self.password}
            )
            response.raise_for_status()
            logger.info("Авторизация успешна.")
            return response.json().get("token")
        except requests.RequestException as e:
            logger.error(f"Ошибка авторизации: {e}")
            raise ConnectionError("Failed to authenticate with ThingsBoard") from e

    def get_headers(self) -> dict:
        return {"X-Authorization": f"Bearer {self.token}"}

    def get_device_by_name(self, device_name: str) -> TbDevice:
        return (
            self.get_device_by_name_customer(device_name)
            if self.is_customer
            else self.get_device_by_name_tenant(device_name)
        )

    def get_device_info_by_name(self, device_name: str) -> dict:
        return (
            self.get_device_info_by_name_customer(device_name)
            if self.is_customer
            else self.get_device_info_by_name_tenant(device_name)
        )

    def get_device_by_name_tenant(self, device_name: str) -> TbDevice:
        try:
            logger.info(f"[TENANT] Поиск устройства: {device_name}")
            response = requests.get(
                f"{self.url}/api/tenant/devices?deviceName={device_name}",
                headers=self.get_headers()
            )
            response.raise_for_status()
            data = response.json()
            if not data or "id" not in data or "id" not in data["id"]:
                raise ValueError(f"Device '{device_name}' not found.")
            return TbDevice(self.url, self.get_headers(), data)
        except requests.RequestException as e:
            logger.error(f"Ошибка получения tenant-устройства: {e}")
            raise

    def get_device_info_by_name_tenant(self, device_name: str) -> dict:
        return self._get_device_info(
            url=f"{self.url}/api/tenant/deviceInfos",
            device_name=device_name,
            role="TENANT"
        )

    def get_device_by_name_customer(self, device_name: str) -> TbDevice:
        customer_id = self._get_customer_id()
        try:
            logger.info(f"[CUSTOMER] Получение устройств для customerId: {customer_id}")
            response = requests.get(
                f"{self.url}/api/customer/{customer_id}/devices",
                params={"pageSize": 100, "page": 0},
                headers=self.get_headers()
            )
            response.raise_for_status()
            for device in response.json().get("data", []):
                if device.get("name") == device_name:
                    return TbDevice(self.url, self.get_headers(), device)
            raise ValueError(f"Device '{device_name}' not found.")
        except requests.RequestException as e:
            logger.error(f"Ошибка получения customer-устройства: {e}")
            raise

    def get_device_info_by_name_customer(self, device_name: str) -> dict:
        customer_id = self._get_customer_id()
        return self._get_device_info(
            url=f"{self.url}/api/customer/{customer_id}/deviceInfos",
            device_name=device_name,
            role="CUSTOMER"
        )

    def _get_customer_id(self) -> str:
        try:
            response = requests.get(
                f"{self.url}/api/auth/user",
                headers=self.get_headers()
            )
            response.raise_for_status()
            customer_id = response.json().get("customerId", {}).get("id")
            if not customer_id:
                raise ValueError("Customer ID not found for current user.")
            return customer_id
        except requests.RequestException as e:
            logger.error(f"Ошибка получения customerId: {e}")
            raise

    def _get_device_info(self, url: str, device_name: str, role: str) -> dict:
        try:
            logger.info(f"[{role}] Поиск устройства '{device_name}' через deviceInfos")
            response = requests.get(
                url,
                params={"pageSize": 100, "page": 0},
                headers=self.get_headers()
            )
            response.raise_for_status()
            for device in response.json().get("data", []):
                if device.get("name") == device_name:
                    logger.info(f"Устройство найдено. Active = {device.get('active')}")
                    return {
                        "id": device["id"]["id"],
                        "name": device["name"],
                        "type": device.get("type"),
                        "label": device.get("label"),
                        "deviceProfileName": device.get("deviceProfileName"),
                        "active": device.get("active", None)
                    }
            raise ValueError(f"Device '{device_name}' not found.")
        except requests.RequestException as e:
            logger.error(f"Ошибка получения deviceInfo ({role}): {e}")
            raise
