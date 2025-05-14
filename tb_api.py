import requests

class TbApi:
    def __init__(self, url, username, password):
        self.url = url
        self.username = username
        self.password = password
        self.token = self.login()

    def login(self):
        login_url = f"{self.url}/api/auth/login"
        payload = {"username": self.username, "password": self.password}
        response = requests.post(login_url, json=payload)
        response.raise_for_status()
        return response.json()['token']

    def get_headers(self):
        return {'X-Authorization': f'Bearer {self.token}'}

    def get_device_by_name(self, device_name):
        url = f"{self.url}/api/tenant/devices?deviceName={device_name}"
        response = requests.get(url, headers=self.get_headers())
        response.raise_for_status()
        data = response.json()
        if data and 'id' in data:
            return TbDevice(self.url, self.get_headers(), data)
        else:
            raise Exception(f"Device '{device_name}' not found.")


class TbDevice:
    def __init__(self, base_url, headers, device_data):
        self.base_url = base_url
        self.headers = headers
        self.device_id = device_data['id']['id']

    def get_data(self):
        url = f"{self.base_url}/api/plugins/telemetry/DEVICE/{self.device_id}/values/timeseries"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()
