import requests
from datetime import datetime, timezone, timedelta
import logging
from config import BASE_URL, SYMBOL

def fetch_ohlc_candles(symbol: str, resolution: str, start: int, end: int):
    """
    Fetch historical OHLC candles from Delta Exchange public API.
    Timestamps must be in UTC seconds.
    Returns a list of candles or None on error.
    """
    url = f"{BASE_URL}/v2/history/candles"
    params = {
        'symbol': symbol,
        'resolution': resolution,
        'start': start,
        'end': end
    }
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        if data.get('success'):
            return data['result']
        else:
            logging.error(f"Delta API error: {data}")
            return None
    except Exception as e:
        logging.error(f"Failed to fetch candles: {e}")
        return None

if __name__ == "__main__":
    # Example: fetch last 20 1H candles up to now (UTC)
    now = datetime.now(timezone.utc)
    end = int(now.timestamp())
    start = end - 20 * 3600
    candles = fetch_ohlc_candles(SYMBOL, '1h', start, end)
    if candles:
        print(f"Fetched {len(candles)} candles:")
        for c in candles:
            print(c)
    else:
        print("Failed to fetch candles.")
