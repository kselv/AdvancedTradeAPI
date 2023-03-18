
import json, hmac, hashlib, time
import http.client
import websockets


class AdvancedTrade:
   
    secretKey = None
    publicKey = None

    ##########################
    ######## WEBSOCKET #######
    ##########################
    # Current minimal version
    # TODO - Extend and improve
    WS_API_URL = 'wss://advanced-trade-ws.coinbase.com'
    
    async def main(self):
        async with websockets.connect(self.WS_API_URL) as websocket:
            data_to_send = json.dumps(self.get_subscribe_msg())
            msg = await websocket.send(data_to_send)
            print(msg)
            while True:
                msg = await websocket.recv()
                data = json.loads(msg)
                try:
                    print(data['events'][0]['tickers'][0]['price'])
                    print(data['events'][0]['tickers'][0]['volume_24_h'])
                except:
                    print()
    
    
    def timestampAndSign(self, message, channel, products = []):
        
        timestamp = str(int(time.time())) 
        
        # message = str(timestamp) + method + endpoint + payload
        temp_products=','.join(str(p) for p in products)
        strToSign = '{}{}{}'.format(timestamp, channel, temp_products)
        sig = hmac.new(self.secretKey.encode('utf-8'), strToSign.encode('utf-8'), digestmod=hashlib.sha256).digest()
        
        message.update({
                'timestamp': timestamp,
                'signature': sig.hex()
            }
        )
        
        return message
    

    def get_subscribe_msg(self,type='subscribe', channel='ticker', product_ids=["BTC-USDT"]):
        
        message = {
            'type': type,
            'channel': channel,
            'api_key': self.publicKey,
            "product_ids": product_ids
        }
        
        self.timestampAndSign( message, channel, product_ids)
        
        
        return message
        
        
    
    ##########################
    #### API ENDPOINTS #######
    ##########################
    BASE_API = '/api/v3/brokerage/'
    
    # GET
    GET_ACCOUNTS_API = BASE_API + 'accounts/' # GET
    GET_PRODUCTS_API = BASE_API + 'products/' # GET
    GET_LIST_ORDERS_API = BASE_API + 'orders/historical/batch' # GET
    GET_ORDER_BY_ID = BASE_API + 'orders/historical/'
    GET_TRANSACTION_SUMMARY_API = BASE_API + 'transaction_summary/' # GET
    
    # POST
    POST_ORDER = BASE_API + "orders/"
    POST_CANCEL_ORDER = BASE_API + "orders/batch_cancel/"
    
    conn = http.client.HTTPSConnection("api.coinbase.com")
    
    def __init__(self, publicKey, secretKey):
        self.publicKey = publicKey
        self.secretKey = secretKey

    
    
    '''
    Create an order with a specified product_id (asset-pair), side (buy/sell), etc.
    '''
    def order(self, product_id, order_id, size, type):
        #request.method = GET or POST
        endpoint = self.POST_ORDER
        
        order_configuration = {
                    'market_market_ioc': {
                        'quote_size': str(size) if type == 'BUY' else None, # BUY
                        'base_size':  str(size) if type == 'SELL' else None # SELL
                    },
                }
        

        payload = self.get_order_payload(self, order_id, product_id, type, order_configuration)
        
        return self.endpoint_call(endpoint=endpoint, payload=payload, method="POST")
    
    
    '''
    Initiate cancel requests for one or more orders.
    '''
    def cancel_orders(self, order_ids):
        payload =   {
                        "order_ids": order_ids
                    }
        return self.endpoint_call(endpoint=self.POST_CANCEL_ORDER, payload=payload, method="POST")
    
    def cancel_order(self, order_id: str):
        return self.cancel_orders([order_id])
        
    def buy(self, product_id, order_id, size):
        self.order(product_id=product_id, order_id=order_id, size=size, type="BUY")
    
    def sell(self, product_id, order_id, size):
        self.order(product_id=product_id, order_id=order_id, size=size, type="SELL")
            
    def order_limit(self, product_id, order_id, size, limit_size, type, post_only=False):
        
        endpoint = self.POST_ORDER
        
        order_configuration = {
                    'limit_limit_gtc': {
                        'base_size': size,
                        'limit_price': limit_size,
                        'post_only': post_only
                    }
                }
        
        payload = self.get_order_payload(self, order_id, product_id, type, order_configuration)

        return self.endpoint_call(endpoint=endpoint, payload=payload, method="POST")
        
    
    def buy_order_limit(self, product_id, order_id, size, limit_size, post_only=False):
        return self.order_limit(product_id, order_id, size, limit_size, "Buy", post_only)
    
    def sell_order_limit(self, product_id, order_id, size, limit_size, post_only=False):
        return self.order_limit(product_id, order_id, size, limit_size, "Sell", post_only)
        
        
    def list_orders(self, limit):
        params = "?limit={}".format(limit)
        return self.endpoint_call(endpoint=self.GET_LIST_ORDERS_API+params.format(limit), payload='', method="GET")
    
    def get_order_id(self, id):
        endpoint = self.GET_ORDER_BY_ID + id
        
        return self.endpoint_call(endpoint=endpoint, payload='', method="GET")
        
    
    def products(self):
        return self.endpoint_call(endpoint=self.GET_PRODUCTS_API, payload='', method="GET")
    
    
    def get_product(self, product_id):
        return self.endpoint_call(endpoint=self.GET_PRODUCTS_API + product_id, payload='', method="GET")
    
    def list_accounts(self):
        return self.endpoint_call(endpoint=self.GET_ACCOUNTS_API, payload='', method="GET")
    
    def get_account(self, uuid):
        return self.endpoint_call(endpoint=self.GET_ACCOUNTS_API+uuid, payload='', method="GET")
        
    def get_market_trades(self, product_id, limit=10):
        params="?limit={}".format(limit)
        endpoint = self.BASE_API + 'products/{}/ticker'.format(product_id)
        return self.endpoint_call(endpoint=endpoint, payload='', method="GET")
        
            
        
    
    # GENERIC FUNCTIONS 
    def endpoint_call(self, endpoint, payload, method):    
        # Make sure payload is dumped 
        payload = json.dumps(payload)
        
        method = method.upper()
        
        # Make sure method is "GET" or "POST"
        if method != 'POST' and method != 'GET':
            raise Exception("Only POST or GET method allowed")
        
        data = self.get_response(endpoint=endpoint, payload=payload, method=method)
        
        print(data)
        
        return data
    
    
    def get_order_payload(self, order_id, product_id, type, order_configuration):
        payload = {
            'client_order_id': str(order_id),
            'product_id': product_id,
            'side': type,
            'order_configuration': order_configuration
        }
        
        return json.dumps(payload)
        
    
    def get_response(self, method, endpoint, payload):
        
        timestamp = str(int(time.time())) 
        
        message = str(timestamp) + method + endpoint + payload
        signature = hmac.new(self.secretKey.encode('utf-8'), message.encode('utf-8'), digestmod=hashlib.sha256).digest()
        print(signature.hex(), timestamp)
        
        
        headers = {
                    'Content-Type': 'application/json',
                    'CB-ACCESS-KEY': self.publicKey,
                    'CB-ACCESS-SIGN':signature.hex(),
                    'CB-ACCESS-TIMESTAMP': timestamp
                 }
        
        
        self.conn.request(method, endpoint, payload, headers)

        # r = requests.get(self.url, headers=headers)
        res = self.conn.getresponse()
        data = res.read()
        data = data.decode("utf-8")
        try:
            data = json.loads(data)
        except Exception as e:
            print(e)
                
        return data
    
