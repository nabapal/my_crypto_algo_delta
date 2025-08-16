import requests
import hmac
import hashlib
import time
import json
from datetime import datetime, timezone
import logging
import websocket
import threading
from typing import Dict, Any, Optional, Callable, List

from config import API_KEY, API_SECRET, BASE_URL, WEBSOCKET_URL, SYMBOL

class DeltaExchangeAPI:
    def get_klines(self, symbol: str, resolution: str, start: int, end: int) -> Dict[str, Any]:
        """Get historical OHLC candles from Delta Exchange API (UTC timestamps in seconds)."""
        params = {
            'symbol': symbol,
            'resolution': resolution,
            'start': start,
            'end': end
        }
        return self._make_request('GET', '/v2/history/candles', params=params)
    def __init__(self):
        self.api_key = API_KEY
        self.api_secret = API_SECRET
        self.base_url = BASE_URL
        self.ws_url = WEBSOCKET_URL
        self.timeout = 10
        # WebSocket connection variables
        self.ws = None
        self.ws_connected = False
        self.callbacks = {}
        self.reconnect_attempts = 0
        self.max_reconnect_attempts = 10
        self.reconnect_delay = 2
        self._shutdown = False
        self._reconnect_scheduled = False
        self.last_heartbeat = 0
        self.heartbeat_interval = 30
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        self._start_heartbeat_thread()

    def _start_heartbeat_thread(self):
        def heartbeat_loop():
            while not self._shutdown:
                try:
                    if self.ws_connected and self.ws:
                        current_time = time.time()
                        if current_time - self.last_heartbeat > self.heartbeat_interval:
                            try:
                                self.ws.send('{"type": "ping"}')
                                self.last_heartbeat = current_time
                                self.logger.debug("💓 Sent WebSocket heartbeat")
                            except Exception as e:
                                self.logger.error(f"❌ Failed to send heartbeat: {e}")
                    time.sleep(10)
                except Exception as e:
                    self.logger.error(f"❌ Heartbeat error: {e}")
        heartbeat_thread = threading.Thread(target=heartbeat_loop)
        heartbeat_thread.daemon = True
        heartbeat_thread.start()

    def _create_signature(self, method: str, path: str, body: str = "") -> Dict[str, str]:
        timestamp = str(int(time.time()))
        message = f"{method}{path}{body}{timestamp}"
        signature = hmac.new(
            self.api_secret.encode('utf-8'),
            message.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        return {
            'api-key': self.api_key,
            'signature': signature,
            'timestamp': timestamp
        }

    def _make_request(self, method: str, endpoint: str, params: Optional[Dict] = None, data: Optional[Dict] = None) -> Dict[str, Any]:
        url = f"{self.base_url}{endpoint}"
        body = ""
        if data:
            body = json.dumps(data)
        headers = self._create_signature(method, endpoint, body)
        headers['Content-Type'] = 'application/json'
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, params=params, timeout=self.timeout)
            elif method == 'POST':
                response = requests.post(url, headers=headers, json=data, timeout=self.timeout)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers, timeout=self.timeout)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            self.logger.error(f"❌ API request failed: {e}")
            return {'success': False, 'error': str(e)}
        except json.JSONDecodeError as e:
            self.logger.error(f"❌ JSON decode error: {e}")
            return {'success': False, 'error': 'Invalid JSON response'}

    def get_profile(self) -> Dict[str, Any]:
        return self._make_request('GET', '/v2/profile')

    def get_balance(self) -> Dict[str, Any]:
        return self._make_request('GET', '/v2/wallet/balance')

    def get_products(self) -> Dict[str, Any]:
        return self._make_request('GET', '/v2/products')

    def get_ticker(self, symbol: str) -> Dict[str, Any]:
        return self._make_request('GET', f'/v2/tickers/{symbol}')

    # ... (other methods from your script can be added as needed)

if __name__ == "__main__":
    api = DeltaExchangeAPI()
    if api.get_profile().get('success'):
        print("🎉 API connection successful!")
        products = api.get_products()
        btc_product = None
        for product in products.get('result', []):
            if product.get('symbol') == SYMBOL:
                btc_product = product
                break
        if btc_product:
            print(f"📊 Found {SYMBOL}: Product ID {btc_product['id']}")
            print(f"   Description: {btc_product['description']}")
            print(f"   Trading Status: {btc_product['trading_status']}")
        ticker = api.get_ticker(SYMBOL)
        if ticker.get('success'):
            result = ticker['result']
            print(f"💰 {SYMBOL} Price: ${result.get('mark_price', 'N/A')}")
    else:
        print("❌ API connection failed. Please check your credentials.")
