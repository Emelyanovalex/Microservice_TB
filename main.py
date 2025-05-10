import os
from tb_api import TbApi
from dotenv import load_dotenv

load_dotenv()

url = os.getenv("TB_URL")
username = os.getenv("TB_USERNAME")
password = os.getenv("TB_PASSWORD")
device_name = os.getenv("TB_DEVICE_NAME")

tbapi = TbApi(url, username, password)
device = tbapi.get_device_by_name(device_name)
telemetry = device.get_telemetry()
print("telemetry: ", telemetry)
