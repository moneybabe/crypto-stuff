import requests
import pandas as pd

class AddressMonitor:
    '''
    This is a class that helps monitor the ordinals activity of a targeted BTC 
    address.

    It has 1 method:
        - get_activity
    '''

    def __init__(self, address: str):
        self.__genii_base_url = "https://api.geniidata.com"
        self.address = address

    def get_activity(self, tick: str = None, n_activity: int = 2000) -> dict:
        request_path = "/api/1/brc20/activities"
        url = self.__genii_base_url + request_path
        activity_df = pd.DataFrame()
        for n in range(0, n_activity, 100):
            params = {
                "limit": 100,
                "offset": n,
                "address": self.address,
                "order": "desc"
            }
            if tick is not None:
                params["tick"] = tick
            headers = {
                "accept": "application/json",
                "api-key": "142cf1b0-1ca7-11ee-bb5e-9d74c2e854ac"
            }
            with requests.get(url, headers=headers, params=params) as response:
                data = pd.DataFrame(response.json()["data"]["list"])
                data["amount"] = pd.to_numeric(data["amount"])
                activity_df = pd.concat(
                    [activity_df, data],
                    ignore_index=True
                )
        grouped = activity_df.groupby(by="tick", group_keys=True)
        activity = {name: group for name, group in grouped}
        setattr(self, "activity", activity)
        return activity