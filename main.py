import os
import logging
from typing import Any, Dict, Optional
from fastapi import FastAPI, HTTPException
from dotenv import load_dotenv
from tb_api import TbApi

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()
url = os.getenv("TB_URL")
username = os.getenv("TB_USERNAME")
password = os.getenv("TB_PASSWORD")
device_name = os.getenv("TB_DEVICE_NAME")
is_customer = "customer" in username.lower()

app = FastAPI()


@app.get("/get_data")
def get_data() -> Dict[str, Optional[Any]]:
    try:
        tbapi = TbApi(url, username, password, is_customer=is_customer)

        device = tbapi.get_device_by_name(device_name)
        telemetry = device.get_data()
        keys = ["temperature", "volt", "sound_db"]
        result = {
            key: telemetry[key][0]["value"] if key in telemetry and telemetry[key] else None
            for key in keys
        }

        device_info = tbapi.get_device_info_by_name(device_name)
        result["active"] = device_info.get("active", None)

        return result

    except ValueError as ve:
        logger.warning(f"Устройство не найдено: {ve}")
        raise HTTPException(status_code=404, detail=str(ve))
    except ConnectionError as ce:
        logger.error(f"Ошибка соединения: {ce}")
        raise HTTPException(status_code=503, detail="Устройство недоступно или ThingsBoard не отвечает")
    except Exception as e:
        logger.exception("Неизвестная ошибка")
        raise HTTPException(status_code=500, detail="Внутренняя ошибка сервера")
