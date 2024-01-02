import sys
import os
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

from configparser import ConfigParser
import requests
import time
from datetime import datetime
from ordinals.classes.AddressMonitor import AddressMonitor
import pandas as pd

def setup_address_monitors():
    parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    whales_df = pd.read_csv(os.path.join(parent_dir, "ordinals/whales/whales.csv"))
    whales_df["related_tokens"] = whales_df["related_tokens"].apply(eval)

    address_monitors = {}
    for address in whales_df["address"]:
        address_monitors[address] = AddressMonitor(address)
    for monitor in address_monitors.values():
        monitor.get_activity(n_activity=100)
    return whales_df, address_monitors
    
def gen_text(address: str, activity: dict, whales_df: pd.DataFrame) -> str:
    txt_template = "\
        NEW ACTIVITY FROM {}\n\
        event time: {}\n\
        now time: {}\n\
        actual address: {}\n\
        whale's related tokens: {}\n\
        token: {}\n\
        event: {}\n\
        amount: {}\n\
        from_address: {}\n\
        to_address: {}\
        "
    return txt_template.format(
        whales_df.loc[whales_df["address"] == address, "nickname"].iloc[0],
        datetime.fromtimestamp(activity["block_time"]),
        datetime.now(),
        address,
        whales_df.loc[whales_df["address"] == address, "related_tokens"].iloc[0],
        activity["tick"],
        activity["event"],
        activity["amount"],
        activity["from_address"],
        activity["to_address"]
    )

def main():
    parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    config = ConfigParser()
    config.read(os.path.join(parent_dir, 'config.ini'))
    api_key = config.get("telegram_api", "api_key")
    chat_id = config.get("telegram_api", "chat_id")
    base_url = f"https://api.telegram.org/bot{api_key}/sendMessage"

    params = {
        "chat_id": chat_id,
        "text": "gm world"
    }
    requests.get(base_url, params=params)
    
    try:
        whales_df, address_monitors = setup_address_monitors()
        
        while True:
            for address, monitor in address_monitors.items():
                new_act = monitor.get_new_activity()
                if len(new_act) > 0:
                    for _, act in new_act.iterrows():
                        params["text"] = gen_text(address, act, whales_df)
                        requests.get(base_url, params=params)

            print("sleeping for 30s")
            time.sleep(30)
    except:
        params["text"] = "something's wrong"
        requests.get(base_url, params=params)

def test_main():
    parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    config = ConfigParser()
    config.read(os.path.join(parent_dir, 'config.ini'))
    api_key = config.get("telegram_api", "api_key")
    chat_id = config.get("telegram_api", "chat_id")
    base_url = f"https://api.telegram.org/bot{api_key}/sendMessage"

    params = {
        "chat_id": chat_id,
        "text": "gm world"
    }
    print(params)
    
    whales_df, address_monitors = setup_address_monitors()
    
    while True:
        for address, monitor in address_monitors.items():
            new_act = monitor.get_new_activity()
            if len(new_act) > 0:
                for _, act in new_act.iterrows():
                    params["text"] = gen_text(address, act, whales_df)
                    print(params)

            print("sleeping for 30s")
            time.sleep(30)


main()