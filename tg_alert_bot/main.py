import sys
import os
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

from configparser import ConfigParser
import requests
import time
from ordinals.classes import AddressMonitor

config = ConfigParser()
config.read('config.ini')
api_key = config.get("telegram_alert_bot", "api_key")
chat_id = config.get("telegram_alert_bot", "chat_id")
base_url = f"https://api.telegram.org/bot{api_key}/sendMessage"

params = {
    "chat_id": chat_id,
    "text": "gm world"
}

while True:
    text = "gm"
    params["text"] = text
    requests.get(base_url, params=params)
    time.sleep(3)