import os
from fastapi import FastAPI, HTTPException
from dotenv import load_dotenv
from tb_api import TbApi

load_dotenv()

app = FastAPI()

url = os.getenv("TB_URL")
username = os.getenv("TB_USERNAME")
password = os.getenv("TB_PASSWORD")
device_name = os.getenv("TB_DEVICE_NAME")

try:
    tbapi = TbApi(url, username, password)
    device = tbapi.get_device_by_name(device_name)
except Exception as e:
    raise RuntimeError(f"Ошибка инициализации: {e}")

@app.get("/get_data")
def get_data():
    try:
        telemetry = device.get_data()
        keys = ["temperature", "volt", "sound_db"]
        clean = {}
        for key in keys:
            if key in telemetry and telemetry[key]:
                value = telemetry[key][0]["value"]
                try:
                    clean[key] = float(value)
                except (ValueError, TypeError):
                    clean[key] = None  # if the value is not convertible
        return clean
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))