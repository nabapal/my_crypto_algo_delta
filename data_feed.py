"""
Enhanced Data Feed for Paper Trading Bot
"""

import requests
import pandas as pd
import logging
from datetime import datetime
from config import BASE_URL, SYMBOL

class DataFeed:
    def __init__(self):
        # Use configuration from config file
        self.base_url = BASE_URL
        self.symbol = SYMBOL
        self.session = requests.Session()
        
        # Set up basic logging
        self.logger = logging.getLogger('DataFeed')
        
    def _make_request(self, endpoint, params=None, retries=3):
        """Make API request with error handling and retries"""
        url = f"{self.base_url}{endpoint}"
        
        for attempt in range(retries):
            try:
                response = self.session.get(url, params=params, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    return data
                elif response.status_code == 429:
                    # Rate limiting
                    import time
                    wait_time = 2 ** attempt
                    print(f"Rate limited. Waiting {wait_time} seconds...")
                    time.sleep(wait_time)
                    continue
                else:
                    print(f"HTTP Error {response.status_code}: {response.text}")
                    return None
                    
            except requests.exceptions.RequestException as e:
                print(f"Request failed (attempt {attempt + 1}): {str(e)}")
                if attempt < retries - 1:
                    import time
                    time.sleep(2 ** attempt)
                else:
                    return None
                    
        return None
    
    def fetch_historical_candles(self, resolution="1h", count=100):
        """
        Fetch historical 1H candle data for strategy calculations
        """
        try:
            # Calculate timestamp for 'count' periods ago
            end_time = int(datetime.now().timestamp())
            start_time = end_time - (count * 3600)  # For 1h candles
            
            endpoint = f"/v2/history/candles"
            params = {
                'symbol': self.symbol,
                'resolution': resolution,
                'start': start_time,
                'end': end_time
            }
            
            data = self._make_request(endpoint, params)
            
            if data and 'result' in data:
                candles = data['result']
                
                # Convert list of dictionaries to DataFrame
                if candles and len(candles) > 0:
                    df = pd.DataFrame(candles)
                    
                    # Rename columns to match our strategy expectations
                    df = df.rename(columns={
                        'time': 'Timestamp',
                        'open': 'Open',
                        'high': 'High', 
                        'low': 'Low',
                        'close': 'Close',
                        'volume': 'Volume'
                    })
                    
                    # Convert timestamp to datetime
                    df['Timestamp'] = pd.to_datetime(df['Timestamp'], unit='s')
                    
                    # Convert price columns to float
                    price_columns = ['Open', 'High', 'Low', 'Close']
                    for col in price_columns:
                        df[col] = pd.to_numeric(df[col], errors='coerce')
                    
                    df['Volume'] = pd.to_numeric(df['Volume'], errors='coerce')
                    
                    # Sort by timestamp (oldest first)
                    df = df.sort_values('Timestamp').reset_index(drop=True)
                    
                    print(f"Fetched {len(df)} candles. Latest: {df.iloc[-1]['Timestamp']}")
                    print(f"Price range: ${df['Low'].min():.2f} - ${df['High'].max():.2f}")
                    return df
                else:
                    print("Empty DataFrame returned from API")
                    return None
            else:
                print("No candle data in API response")
                return None
                
        except Exception as e:
            print(f"Error fetching historical candles: {str(e)}")
            return None
        
    def fetch_live_price(self):
        """Fetch current live price"""
        try:
            endpoint = f"/v2/tickers/{self.symbol}"
            url = f"{self.base_url}{endpoint}"
            
            response = self.session.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if 'result' in data:
                    ticker = data['result']
                    
                    live_data = {
                        'symbol': ticker.get('symbol'),
                        'last_price': float(ticker.get('close', 0)),
                        'bid': float(ticker.get('bid', 0)),
                        'ask': float(ticker.get('ask', 0)),
                        'timestamp': datetime.now()
                    }
                    
                    return live_data
            
            return None
                
        except Exception as e:
            print(f"Error fetching live price: {str(e)}")
            return None

    def validate_data(self, df):
        """
        Validate data quality and completeness
        """
        try:
            if df is None or df.empty:
                print("Data validation failed: Empty or None DataFrame")
                return False
            
            required_columns = ['Timestamp', 'Open', 'High', 'Low', 'Close', 'Volume']
            missing_columns = [col for col in required_columns if col not in df.columns]
            
            if missing_columns:
                print(f"Data validation failed: Missing columns {missing_columns}")
                return False
            
            # Check for reasonable price ranges
            price_columns = ['Open', 'High', 'Low', 'Close']
            for col in price_columns:
                if (df[col] <= 0).any():
                    print(f"Data validation failed: Invalid prices in {col}")
                    return False
            
            print("Data validation passed")
            return True
            
        except Exception as e:
            print(f"Data validation error: {str(e)}")
            return False

if __name__ == "__main__":
    # Test the data feed
    df = DataFeed()
    price = df.fetch_live_price()
    if price:
        print(f"Live BTC price: ${price['last_price']:.2f}")
    else:
        print("Failed to fetch price")
