# -*- coding: utf-8 -*-
# created by @kapipara180 edited by @snufkin0866
# changed base url ,added some functions, fixed bugs(mainly about nonce)
# and so on, by @snufkin0866
# main part was created by @kapipara180, thanks!


import json
import requests
import time
import urllib
import jwt
import configparser
import traceback
from logging import getLogger, StreamHandler, FileHandler, Formatter, DEBUG

# -*- coding: utf-8 -*-

logger = getLogger(name="pyliquid")
logger.setLevel(DEBUG)
handler1 = StreamHandler()
handler1.setFormatter(Formatter("%(asctime)s %(levelname)8s %(message)s"))
handler2 = FileHandler(filename="pyliquid.log")  # handler2はファイル出力
handler2.setFormatter(Formatter("%(asctime)s %(levelname)8s %(message)s"))
logger.addHandler(handler1)
logger.addHandler(handler2)


class AuthException(Exception):

    def __init__(self):
        msg = "Please specify your valid API Key and API Secret."
        super(AuthException, self).__init__(msg)


class API(object):

    def __init__(self, api_key=None, api_secret=None):
        self.api_url = "https://api.liquid.com"
        self.api_key = api_key
        self.api_secret = api_secret

    def request(self, endpoint, method="GET", params=None):
        url = self.api_url + endpoint
        body = ""
        auth_header = None
        path = endpoint
        if method == "POST":
            body = json.dumps(params)
        elif method == "PUT":
            body = json.dumps(params)
        else:
            if params:
                body = "?" + urllib.parse.urlencode(params)
                path += body
        if self.api_key and self.api_secret:
            nonce = str(round(time.time()*10**7))
            api_secret = str.encode(self.api_secret)
            token_id = self.api_key
            auth_payload = {
                "path": path,
                "nonce": nonce,
                "token_id": token_id
            }
            signature = jwt.encode(auth_payload, api_secret, 'HS256')
            auth_header = {
                "X-Quoine-API-Version": "2",
                "X-Quoine-Auth": signature,
                "Content-Type": "application/json"
            }
        try:
            with requests.Session() as s:
                if auth_header:
                    s.headers.update(auth_header)

                if method == "GET":
                    response = s.get(url, params=params)
                elif method == "POST":
                    response = s.post(url, data=json.dumps(params))
                else:  # put
                    response = s.put(url, data=json.dumps(params))
        except requests.RequestException as e:
            print(e)
            raise e
        content = ""
        if len(response.content) > 0:
            try:
                content = json.loads(response.content.decode("utf-8"))

            except json.decoder.JSONDecodeError as e:
                print(response.content)
        return content

    """HTTP Public API"""

    def get_products(self, **params):  # test済
        """
        Get the list of all available products.
        """
        endpoint = "/products"
        return self.request(endpoint, params=params)

    def get_a_product(self, id=1):  # test済
        """
        PARAMETERS:
        Parameters	Optional?	Description
        id		Product ID
        """
        endpoint = "/products/" + str(id)
        return self.request(endpoint)

    def get_orderbook(self, id=1):  # test済
        """
        PARAMETERS:
        Parameters	Optional?	Description
        id		Product ID
        full	yes	1 to get all price levels (default is 20 each side)
        FORMAT
        Each price level follows: [price, amount]
        """
        endpoint = "/products/" + str(id) + "/price_levels"
        return self.request(endpoint)

    def get_executions(self, **params):  # test済
        """
        Get a list of recent executions from a product (Executions are sorted in DESCENDING order - Latest first)

        Parameters	Optional?	Description
        product_id		Product ID
        limit	yes	How many executions should be returned. Must be <= 1000. Default is 20
        page	yes	From what page the executions should be returned, e.g if limit=20 and page=2, the response would start from the 21st execution. Default is 1

        or

        Get a list of executions after a particular time (Executions are sorted in ASCENDING order)

        Parameters	Optional?	Description
        currency_pair_code		e.g. BTCJPY
        timestamp		Only show executions at or after this timestamp (Unix timestamps in seconds)
        limit	yes	How many executions should be returned. Must be <= 1000. Default is 20

        """
        endpoint = "/executions"
        return self.request(endpoint, params=params)

    def get_interest_rates(self, **params):  # 済
        """
        Get Interest Rate Ladder for a currency
        FORMAT
        Each level follows: [rate, amount]
        """
        endpoint = "/ir_ladders/USD"
        return self.request(endpoint, params=params)

    """HTTP Authenticated API"""

    def create_order(self, **params):
        """
        PARAMETERS
        Parameters	Optional?	Description
        order_type		limit, market or market_with_range
        product_id		Product ID
        side		buy or sell
        quantity		quantity to buy or sell
        price		price per unit of cryptocurrency
        price_range	true	For order_type of market_with_range only, slippage of the order.
        MARGIN ORDER PARAMETERS
        Parameters	Optional?	Description
        leverage_level		Valid levels: 2,4,5,10,25
        funding_currency		Currency used to fund the trade with. Default is quoted currency (e.g a trade in BTCUSD product will use USD as the funding currency as default)
        order_direction	true	one_direction, two_direction, netout
        """
        if not all([self.api_key, self.api_secret]):
            raise AuthException()

        endpoint = "/orders/"
        return self.request(endpoint, "POST", params=params)

    def get_order(self, id=1):  # test済
        """
        Parameters	Optional?	Description
        id		Order ID
        """
        if not all([self.api_key, self.api_secret]):
            raise AuthException()

        endpoint = "/orders/" + str(id)
        return self.request(endpoint)

    def get_orders(self, **params):  # test 済
        """
        PARAMETERS:
        Parameters	Optional?	Description
        funding_currency	yes	filter orders based on funding currency
        product_id	yes	filter orders based on product
        status	yes	filter orders based on status
        with_details	yes	return full order details (attributes between *) including executions if set to 1
       """
        if not all([self.api_key, self.api_secret]):
            raise AuthException()

        endpoint = "/orders"
        return self.request(endpoint, params=params)

    def cancel_order(self, id=1, **params):
        """
        PARAMETERS:
        Parameters	Optional?	Description
        id		Order ID
        """
        if not all([self.api_key, self.api_secret]):
            raise AuthException()

        endpoint = "/orders/" + str(id) + "/cancel"
        return self.request(endpoint, method="PUT", params=params)

    def edit_live_order(self, id=1, **params):
        """
        PARAMETERS:
        Parameters	Optional?	Description
        id		Order ID
        """

        if not all([self.api_key, self.api_secret]):
            raise AuthException()

        endpoint = "/orders/" + str(id)
        return self.request(endpoint, method="PUT", params=params)

    def get_orders_trade(self, id=1, **params):
        """
        PARAMETERS:
        Parameters	Optional?	Description
        id		Order ID
        """
        if not all([self.api_key, self.api_secret]):
            raise AuthException()

        endpoint = "/orders/" + str(id) + "/trades"
        return self.request(endpoint)

    def get_my_execution(self, **params):
        """
        PARAMETERS:
        Parameters	Optional?	Description
        product_id		Product ID
        """
        if not all([self.api_key, self.api_secret]):
            raise AuthException()

        endpoint = " /executions/me"
        return self.request(endpoint, params=params)

    def get_crypto_account(self, **params):
        """
        Get Crypto Accounts
        """
        if not all([self.api_key, self.api_secret]):
            raise AuthException()

        endpoint = "/crypto_accounts"
        return self.request(endpoint, params=params)

    def get_fiat_account(self, **params):
        """
        Get Fiat Accounts
        """
        if not all([self.api_key, self.api_secret]):
            raise AuthException()

        endpoint = "/fiat_accounts"
        return self.request(endpoint, params=params)

    def get_all_acountbalance(self, **params):
        """
        Get all Account Balances
        """
        if not all([self.api_key, self.api_secret]):
            raise AuthException()

        endpoint = "/accounts/balance"
        return self.request(endpoint, params=params)

    # Assets Lendingは後で

    def get_trading_accounts(self, **params):
        """
        Get Trading Accounts
        """
        if not all([self.api_key, self.api_secret]):
            raise AuthException()

        endpoint = "/trading_accounts"
        return self.request(endpoint, params=params)

    def get_trading_account(self, id=1, **params):
        """
        PARAMETERS:
        Parameters	Optional?	Description
        id		Trading Account ID
        """
        if not all([self.api_key, self.api_secret]):
            raise AuthException()

        endpoint = "/trading_accounts/" + str(id)
        return self.request(endpoint, params=params)

    def update_leverage(self, id=1, **params):
        """
        PARAMETERS:
        Parameters	Optional?	Description
        id		Trading account ID
        leverage_level		New leverage leve

        {
           "trading_account": {
               "leverage_level": 25
        }
        }
        """
        if not all([self.api_key, self.api_secret]):
            raise AuthException()

        endpoint = "/trading_accounts/" + str(id)
        return self.request(endpoint, method="PUT", params=params)

    def get_trades(self, **params):
        """
        PARAMETERS:
        Parameters	Optional?	Description
        funding_currency	yes	get trades of a particular funding currency
        status	yes	open or closed
        /trades?funding_currency=:funding_currency&status=:status
        """
        if not all([self.api_key, self.api_secret]):
            raise AuthException()

        endpoint = "/trades/"
        return self.request(endpoint, params=params)

    def close_a_trade(self, id=1, **params):
        """
        PARAMETERS:
        Parameters	Optional?	Description
        id		Trade ID
        closed_quantity	yes	The quantity you want to close
        """
        if not all([self.api_key, self.api_secret]):
            raise AuthException()

        endpoint = "/trades/" + str(id) + "/close"
        return self.request(endpoint, method="PUT", params=params)

    def close_all_trades(self, **params):
        """
        PARAMETERS:
        Parameters	Optional?	Description
        side	yes	Close all trades of this side. Close trades of both side if left blank
        """
        if not all([self.api_key, self.api_secret]):
            raise AuthException()

        endpoint = "/trades/close_all"
        return self.request(endpoint, method="PUT", params=params)

    def update_a_trade(self, id=1, **params):
        """
        Parameters	Optional?	Description
        id		Trade ID
        stop_loss		Stop Loss price
        take_profit		Take Profit price

        {
          "trade": {
            "stop_loss": "300",
            "take_profit": "600"
          }
        }
        """
        if not all([self.api_key, self.api_secret]):
            raise AuthException()

        endpoint = "/trades/" + str(id)
        return self.request(endpoint, method="PUT", params=params)

    def get_a_trade_loan(self, id=1, **params):
        """
        Parameters	Optional?	Description
        id		Trade ID
        """
        if not all([self.api_key, self.api_secret]):
            raise AuthException()

        endpoint = "/trades/" + str(id) + "/loans"
        return self.request(endpoint, params=params)

    def get_btcjpy_id(self):
        """
        return the product id of btcjpy
        """
        products = self.get_products()
        for p in products:
            if p['currency_pair_code'] == 'BTCJPY':
                id = p['id']
        return id

    def get_jpy_account(self):
        """
        return your jpy trading account
        """
        accounts = self.get_trading_accounts()
        if type(accounts) == dict:
            return {"Error": "Unexpected error while getting your jpy account", "Content": accounts}
        elif type(accounts) == bytes:
            time.sleep(1)
            self.get_jpy_account()
        elif accounts is None:
            logger.debug('Variable "accounts" is None. Retrying ')
            time.sleep(1)
            self.get_jpy_account()
        else:
            try:
                return [i for i in accounts if i['funding_currency'] == 'JPY'][0]
            except IndexError:
                logger.debug(f'Index Error occured. accounts: {accounts}')

    def get_btcjpy_price(self):
        btcjpy_id = self.get_btcjpy_id()
        product = self.get_a_product(id=btcjpy_id)
        ltp = product['last_traded_price']
        best_bid = product['market_bid']
        best_ask = product['market_ask']
        return ltp, best_bid, best_ask

    def get_available_jpy(self):
        jpy_account = self.get_jpy_account()
        if jpy_account is None:
            self.get_available_jpy()
        return jpy_account['free_margin']

    def get_pos_size(self):
        jpy_account = self.get_jpy_account()
        if jpy_account is None:
            time.sleep(1)
            self.get_pos_size()
        elif 'Error' in jpy_account.keys():
            logger.debug(jpy_account)
            raise ValueError('API returned error message.')
        elif not jpy_account:
            time.sleep(1)
            self.get_pos_size()
        else:
            pos_size = jpy_account['position']
            if pos_size is None:
                self.get_pos_size()
            return float(pos_size)
