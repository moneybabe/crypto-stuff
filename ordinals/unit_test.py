from classes import *
from configparser import ConfigParser


class TestToken:

    config = ConfigParser()
    config.read("config.ini")
    okx_api_key = config["okx"]["api_key"]
    okx_secret_key = config["okx"]["secret_key"]
    okx_password = config["okx"]["password"]

    def test_get_token_info(self):
        ordi = Token("ordi")
        ordi_data = {
            "tick": "ordi", 
            "inscription_id": "b61b0172d95e266c18aea0c624db987e971a5d6d4ebc2aaed85da4642d635735i0", 
            "inscription_number": 348020, 
            "max": "21000000.000000000000000000", 
            "limit": "1000.000000000000000000", 
            "decimals": 18, 
            "minted": "21000000.000000000000000000", 
            "mint_progress": "1.000000", 
            "transactions": 227603, 
            "holders": 13711, 
            "deployer": "bc1pxaneaf3w4d27hl2y93fuft2xk6m4u3wc4rafevc6slgd7f5tq2dqyfgy06", 
            "deploy_time": 1678248991
        }
        ordi.get_token_info()
        for key, value in ordi_data.items():
            if key != "transactions" and key != "holders":
                assert getattr(ordi, key) == value

        rats = Token("rats")
        rats_data = {
            "tick": "rats", 
            "inscription_id": "77df24c9f1bd1c6a606eb12eeae3e2a2db40774d54b839b5ae11f438353ddf47i0", 
            "inscription_number": 398115, 
            "max": "1000000000000.000000000000000000", 
            "limit": "1000000.000000000000000000", 
            "decimals": 18, 
            "minted": "1000000000000.000000000000000000", 
            "mint_progress": "1.000000", 
            "transactions": 1171647, 
            "holders": 12134, 
            "deployer": "bc1p9g0r0sw547dknyhkzdu8rhg58455c3ruekkcpckc9rverz4zrjvquc6nxg", 
            "deploy_time": 1678468314
        }
        rats.get_token_info()
        for key, value in rats_data.items():
            if key != "transactions" and key != "holders":
                assert getattr(rats, key) == value

    def test_get_floor_listing(self):
        ordi = Token("ordi")
        floor_listing = ordi.get_floor_listing(
            self.okx_api_key,
            self.okx_secret_key,
            self.okx_password
        )
        assert type(floor_listing) == dict
        assert len(floor_listing) == 4
        assert ordi.floor_listing == floor_listing

        rats = Token("rats")
        floor_listing = rats.get_floor_listing(
            self.okx_api_key,
            self.okx_secret_key,
            self.okx_password
        )
        assert type(floor_listing) == dict
        assert len(floor_listing) == 4
        assert rats.floor_listing == floor_listing

    def test_get_trade_histroy(self):
        ordi = Token("ordi")
        trade_history = ordi.get_trade_history(
            self.okx_api_key,
            self.okx_secret_key,
            self.okx_password
        )
        assert type(trade_history) == pd.DataFrame
        assert len(trade_history) > 0
        assert trade_history.shape[1] == 4

        eight = Token("8888")
        trade_history = eight.get_trade_history(
            self.okx_api_key,
            self.okx_secret_key,
            self.okx_password
        )
        assert type(trade_history) == pd.DataFrame
        assert len(trade_history) > 0 
        assert trade_history.shape[1] == 4

    def test_save_and_load_token(self):
        ordi = Token("ordi")
        ordi.get_floor_listing(
            self.okx_api_key,
            self.okx_secret_key,
            self.okx_password
        )
        ordi.get_trade_history(
            self.okx_api_key,
            self.okx_secret_key,
            self.okx_password
        )
        ordi.save_token()
        ordi_loaded = ordi.load_token()
        for key, value in ordi_loaded.floor_listing.items():
            assert ordi_loaded.floor_listing[key] == value
        assert ordi_loaded.trade_history.shape == ordi.trade_history.shape

        eight = Token("8888")
        eight.get_floor_listing(
            self.okx_api_key,
            self.okx_secret_key,
            self.okx_password
        )
        eight.get_trade_history(
            self.okx_api_key,
            self.okx_secret_key,
            self.okx_password
        )
        eight.save_token()
        eight_loaded = eight.load_token()
        for key, value in eight_loaded.floor_listing.items():
            assert eight_loaded.floor_listing[key] == value
        assert eight_loaded.trade_history.shape == eight.trade_history.shape