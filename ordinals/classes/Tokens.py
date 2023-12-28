from .Token import Token

class Tokens:
    '''
    This is a class that aggregates a list of tokens by storing each Token 
    object in a dictionary as an attribute of the Tokens object. It provides an 
    easier way to manage a list of tokens.

    It has 4 methods:
        - get_floor_listing
        - get_trade_history
        - add_token
        - save_tokens
    '''

    def __init__(self, tick_list: list, load: bool = True):
        self._get_tokens(tick_list, load)

    def _get_tokens(self, tick_list: list, load: bool) -> dict[str, Token]:
        token_dict = {}
        for tick in tick_list:
            token_dict[tick] = Token(tick, load=load)
        setattr(self, "tokens", token_dict)
        return token_dict

    def get_floor_listing(
            self, 
            okx_api_key: str, 
            okx_secret_key: str, 
            okx_password: str,
            start: str = "2023-12-15", 
        ) -> dict[str, Token]:
        for token in self.tokens.values():
            token.get_floor_listing(
                okx_api_key,
                okx_secret_key,
                okx_password,
                start=start
            )
        return self.tokens  

    def get_trade_history(
            self, 
            okx_api_key: str, 
            okx_secret_key: str, 
            okx_password: str,
            start: str = "2023-12-15", 
        ) -> dict[str, Token]:
        for token in self.tokens.values():
            token.get_trade_history(
                okx_api_key,
                okx_secret_key,
                okx_password,
                start=start
            )
        return self.tokens

    def add_token(self, tick: str, load: bool = True) -> Token:
        self.tokens[tick] = Token(tick, load=load)
        return self.tokens[tick]

    def save_tokens(self) -> None:
        for token in self.tokens.values():
            token.save_token()