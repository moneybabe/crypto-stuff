from classes.Token import Token
from classes.Tokens import Tokens
from classes.AddressMonitor import AddressMonitor
from configparser import ConfigParser
import pandas as pd
import os

class TestToken:

    current_directory = os.path.dirname(os.path.abspath(__file__))
    parent_directory = os.path.dirname(current_directory)
    config_file_path = os.path.join(parent_directory, "config.ini")
    config = ConfigParser()
    config.read(config_file_path)
    okx_api_key = config["okx_api"]["api_key"]
    okx_secret_key = config["okx_api"]["secret_key"]
    okx_password = config["okx_api"]["password"]

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
            "transactions": 227603,     # not fixed
            "holders": 13711,           # not fixed
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
            "transactions": 1171647,    # not fixed
            "holders": 12134,           # not fixed
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

    def test_get_trade_history(self):
        ordi = Token("ordi")
        trade_history = ordi.get_trade_history(
            self.okx_api_key,
            self.okx_secret_key,
            self.okx_password
        )
        assert type(trade_history) == pd.DataFrame
        assert len(trade_history) > 0

        eight = Token("8888")
        trade_history = eight.get_trade_history(
            self.okx_api_key,
            self.okx_secret_key,
            self.okx_password
        )
        assert type(trade_history) == pd.DataFrame
        assert len(trade_history) > 0 

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
            assert ordi.floor_listing[key] == value
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
            assert eight.floor_listing[key] == value
        assert eight_loaded.trade_history.shape == eight.trade_history.shape

    def test_get_top_20_holder(self):
        ordi = Token("ordi")
        ordi.get_top_20_holders()
        assert type(ordi.top_20_holders) == pd.DataFrame
        assert ordi.top_20_holders.shape == (20, 5)
        assert ordi.top_20_holders.columns.tolist() == [
            "tick",
            "address",
            "overall_balance",
            "transferable_balance",
            "available_balance"
        ]
        assert ordi.top_20_holders.iloc[-1]["overall_balance"] > 0
        
        eight = Token("8888")
        eight.get_top_20_holders()
        assert type(eight.top_20_holders) == pd.DataFrame
        assert eight.top_20_holders.shape == (20, 5)
        assert eight.top_20_holders.columns.tolist() == [
            "tick",
            "address",
            "overall_balance",
            "transferable_balance",
            "available_balance"
        ]
        assert eight.top_20_holders.iloc[-1]["overall_balance"] > 0

class TestTokens:

    def test_initialize(self):
        tick_list = ["ordi", "8888"]
        tokens = Tokens(tick_list)
        assert type(tokens.tokens) == dict
        assert len(tokens.tokens) == 2
        for token in tokens.tokens.values():
            assert type(token) == Token
            assert token.tick in ["ordi", "8888"]

    def test_add_token(self):
        tick_list = ["ordi", "8888"]
        tokens = Tokens(tick_list)
        assert len(tokens.tokens) == 2
        tokens.add_token("rats")
        assert len(tokens.tokens) == 3

    def test_save_tokens(self):
        tick_list = ["ordi", "8888"]
        tokens = Tokens(tick_list)
        tokens.save_tokens()
        tokens_loaded = Tokens(tick_list, load=True)
        for tick, token in tokens_loaded.tokens.items():
            assert tokens.tokens[tick].holders == token.holders
            assert tokens.tokens[tick].transactions == token.transactions

class TestAddressMonitor:

    def test_get_activity(self):
        address = "bc1qhuv3dhpnm0wktasd3v0kt6e4aqfqsd0uhfdu7d"
        monitor = AddressMonitor(address)
        monitor.get_activity(n_activity=300)
        assert type(monitor.activity) == pd.DataFrame
        assert len(monitor.activity) > 0

        monitor.get_activity(tick="sats", n_activity=300)
        assert type(monitor.activity) == pd.DataFrame
        assert len(monitor.activity) == 300