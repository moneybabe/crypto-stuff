import requests
import pandas as pd

class AddressMonitor:
    '''
    This is a class that helps monitor the ordinals activity of a targeted BTC 
    address.

    It has 2 methods:
        - get_activity
        - get_new_activity
    '''

    def __init__(self, address: str):
        self.__genii_base_url = "https://api.geniidata.com"
        self.address = address

    def get_activity(
            self, 
            tick: str = None, 
            event: str = None,
            n_activity: int = 2000
        ) -> pd.DataFrame:
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
            if event is not None:
                params["event"] = event

            headers = {
                "accept": "application/json",
                "api-key": "142cf1b0-1ca7-11ee-bb5e-9d74c2e854ac"
            }

            with requests.get(url, headers=headers, params=params) as response:
                data = pd.DataFrame(response.json()["data"]["list"])
                if len(data) == 0 or n + 100 > response.json()["data"]["count"]:
                    break

                data["amount"] = pd.to_numeric(data["amount"])
                data["time"] = pd.to_datetime(data["block_time"], unit="s")
                activity_df = pd.concat(
                    [activity_df, data],
                    ignore_index=True
                )

        setattr(self, "activity", activity_df)
        return activity_df
    
    def get_new_activity(
            self,
            tick: str = None,
            event: str = None,
            n_activity: int = 2000
        ) -> pd.DataFrame | None:
        request_path = "/api/1/brc20/activities"
        url = self.__genii_base_url + request_path
        
        new_activity_df = pd.DataFrame()
        for n in range(0, n_activity, 100):
            params = {
                "limit": 100,
                "offset": n,
                "address": self.address,
                "order": "desc"
            }
            if tick is not None:
                params["tick"] = tick
            if event is not None:
                params["event"] = event

            headers = {
                "accept": "application/json",
                "api-key": "142cf1b0-1ca7-11ee-bb5e-9d74c2e854ac"
            }

            with requests.get(url, headers=headers, params=params) as response:
                data = pd.DataFrame(response.json()["data"]["list"])
                if len(data) == 0 or n + 100 > response.json()["data"]["count"]:
                    break

                data["amount"] = pd.to_numeric(data["amount"])
                new_activity_df = pd.concat(
                    [new_activity_df, data],
                    ignore_index=True
                )

                if set(data['block_hash']).intersection(self.activity['block_hash']):
                    break

        merged_df = pd.merge(
            new_activity_df, 
            self.activity, 
            how='outer', 
            indicator=True
        )
        unique_new = merged_df[merged_df['_merge'] == 'left_only'].drop(columns=['_merge'])
        merged_df = merged_df.drop(columns=['_merge']).head(2000)
        setattr(self, "activity", merged_df)
        return unique_new