import requests
import pandas as pd
import hmac
import hashlib
import base64
from datetime import datetime
import json
import pickle
import os

class Token:
    '''
    This is a class that can retrive the token data (basic token info, floor 
    listing, or trade histroy) either by loading from a saved pickle file or by 
    making a request to the GeniiData and Okx APIs.

    Then, it can save the token data to a pickle file for later use.

    It has 6 methods: 
        - get_token_info 
        - get_top_20_holders
        - get_floor_listing
        - get_trade_history
        - save_token
        - load_token

    When initialized, it will automatically run 
        - get_token_info()
        - get_top_20_holders()
        
    If load=True is passed, it will also run 
        - load_token()
    '''
    def __init__(self, tick: str, load: bool = True):
        self.__okx_base_url = "https://www.okx.com"
        self.__genii_base_url = "https://api.geniidata.com"
        self.tick = tick
        self.get_token_info()
        self.get_top_20_holders()
        if load:
            self.load_token()

    def get_token_info(self) -> dict:
        request_path = "/api/1/brc20/tickinfo/" + self.tick
        url = self.__genii_base_url + request_path
        headers = {
            "accept": "application/json",
            "api-key": "142cf1b0-1ca7-11ee-bb5e-9d74c2e854ac"
        }
        with requests.get(url, headers=headers) as response:
            data = response.json()["data"]
        
        self.__dict__.update(data)
        return data
    
    def _get_holders_df(self) -> pd.DataFrame:
        self.get_token_info()
        request_path = "/api/1/brc20/balance"
        url = self.__genii_base_url + request_path
        params = {
            "limit": self.holders,
            "offset": 0,
            "tick": self.tick
        }
        headers = {
            "accept": "application/json",
            "api-key": "142cf1b0-1ca7-11ee-bb5e-9d74c2e854ac"
        }
        with requests.get(url, headers=headers, params=params) as response:
            holders_df = pd.DataFrame(
                response.json()["data"]["list"]
            )
            cols_to_numeric = [
                "overall_balance",
                "transferable_balance",
                "available_balance"
            ]
            for col in cols_to_numeric:
                holders_df[col] = pd.to_numeric(holders_df[col])
            cols_to_string = ["tick", "address"]
            for col in cols_to_string:
                holders_df[col] = holders_df[col].astype(str)
            holders_df.sort_values(
                by="overall_balance",
                ascending=False,
                ignore_index=True,
                inplace=True
            )
        setattr(self, "holders_df", holders_df)
        return holders_df
    
    def get_top_20_holders(self) -> pd.DataFrame:
        if getattr(self, "holders_df", None) is None:
            self._get_holders_df()
            setattr(self, "top_20_holders_df", self.holders_df.head(20))
        return self.top_20_holders_df
    
    def _sign_okx_request(self, prehash: str, secret_key: str) -> str:
        signature = hmac.new(
            secret_key.encode(), 
            prehash.encode(), 
            hashlib.sha256
        ).digest()
        return base64.b64encode(signature).decode()

    def _create_okx_request_headers(
            self, 
            method: str, 
            request_path:str, 
            body: json,
            okx_api_key: str,
            okx_secret_key: str,
            okx_password: str
        ) -> dict:
        curr_time = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3]+"Z"
        prehash = curr_time + method + request_path + body
        signature  = self._sign_okx_request(prehash, okx_secret_key)
        
        headers = {
            'OK-ACCESS-KEY': okx_api_key,
            'OK-ACCESS-TIMESTAMP': curr_time,
            'OK-ACCESS-PASSPHRASE': okx_password,
            'OK-ACCESS-SIGN': signature,
            'Content-Type': 'application/json'
        }
        return headers

    def get_floor_listing(
            self,
            okx_api_key: str,
            okx_secret_key: str,
            okx_password: str
        ) -> dict:
        method = "POST"
        request_path = "/api/v5/mktplace/nft/ordinals/listings"
        url = self.__okx_base_url + request_path
        body = json.dumps({"slug":self.tick, "limit":1, "sort":"unit_price_asc"})
        headers = self._create_okx_request_headers(
            method, 
            request_path, 
            body, 
            okx_api_key, 
            okx_secret_key,
            okx_password
        )

        with requests.post(url, headers=headers, data=body) as response:
            data = response.json()["data"]["data"][0]
        floor_listing = {
            "amount": float(data["amount"]),
            "unit_price": float(data["unitPrice"]),
            "total_price": float(data["price"]),
            "listing_time": datetime.fromtimestamp(data["listingTime"])
        }
        setattr(self, "floor_listing", floor_listing)
        return floor_listing
    
    def get_trade_history(
            self, 
            okx_api_key: str,
            okx_secret_key: str,
            okx_password: str,
            start: str = "2023-12-15"
        ) -> pd.DataFrame:
        method = "POST"
        request_path = "/api/v5/mktplace/nft/ordinals/trade-history"
        url = self.__okx_base_url + request_path
        trade_history = pd.DataFrame()
        last_datetime = datetime.utcnow()
        start_datetime = datetime.strptime(start, "%Y-%m-%d")
        cursor = None
        while cursor != "" and last_datetime > start_datetime:
            body = {"slug": self.tick, "limit": 100}
            body["cursor"] = cursor if cursor is not None else ""
            body = json.dumps(body)
            headers = self._create_okx_request_headers(
                method,
                request_path,
                body,
                okx_api_key,
                okx_secret_key,
                okx_password
            )

            with requests.post(url, headers=headers, data=body) as response:
                query = response.json()["data"]
            cursor = query["cursor"]
            data = query["data"]
            data = pd.DataFrame(
                map(
                    lambda x: {
                        "amount": float(x["amount"]),
                        "unit_price": float(x["unitPrice"]),
                        "total_price": float(x["price"]),
                        "time": datetime.fromtimestamp(x["timestamp"])
                    }, data
                )
            )
            trade_history = pd.concat(
                [trade_history, data], 
                ignore_index=True
            )
            last_datetime = trade_history["time"].min()

        setattr(self, "trade_history", trade_history)
        return trade_history

    def save_token(self) -> None:
        current_directory = os.path.dirname(os.path.abspath(__file__))
        parent_directory = os.path.dirname(current_directory)
        saved_token_directory = os.path.join(parent_directory, "saved_tokens")
        os.makedirs(saved_token_directory, exist_ok=True)
        file_path = os.path.join(saved_token_directory, self.tick + ".pkl")
        
        with open(file_path, "wb") as file:
            pickle.dump(self, file)

    def load_token(self) -> object | None:
        current_directory = os.path.dirname(os.path.abspath(__file__))
        parent_directory = os.path.dirname(current_directory)
        saved_token_directory = os.path.join(parent_directory, "saved_tokens")
        os.makedirs(saved_token_directory, exist_ok=True)
        file_path = os.path.join(saved_token_directory, self.tick + ".pkl")

        if os.path.exists(file_path):
            with open(file_path, "rb") as file:
                loaded_object = pickle.load(file)
                self.__dict__.update(loaded_object.__dict__)
                return loaded_object
        else:
            print(f"No saved data found for {self.tick}")