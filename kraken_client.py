"""
kraken_client.py
-----------------
Talks to Kraken's PUBLIC API to get price data.
Public endpoints do NOT require an API key or account -
this is safe to run with zero secrets while paper trading.

When you're ready for LIVE trading later, a separate
authenticated client will be added that needs your API
key/secret (stored as GitHub Secrets, never in code).
"""

import requests
import time

KRAKEN_API_URL = "https://api.kraken.com/0/public"


def get_current_price(pair: str) -> float:
    """
    Get the latest traded price for a pair, e.g. 'XBTUSD'.
    """
    resp = requests.get(f"{KRAKEN_API_URL}/Ticker", params={"pair": pair}, timeout=10)
    resp.raise_for_status()
    data = resp.json()

    if data.get("error"):
        raise RuntimeError(f"Kraken API error for {pair}: {data['error']}")

    result = data["result"]
    key = list(result.keys())[0]  # Kraken renames pairs internally, grab whatever key came back
    last_trade_price = float(result[key]["c"][0])
    return last_trade_price


def get_ohlc(pair: str, interval_minutes: int = 60, lookback_hours: int = 6):
    """
    Get recent OHLC (open/high/low/close) candles for a pair.
    Returns a list of dicts: [{time, open, high, low, close, volume}, ...]
    """
    resp = requests.get(
        f"{KRAKEN_API_URL}/OHLC",
        params={"pair": pair, "interval": interval_minutes},
        timeout=10,
    )
    resp.raise_for_status()
    data = resp.json()

    if data.get("error"):
        raise RuntimeError(f"Kraken API error for {pair}: {data['error']}")

    result = data["result"]
    key = [k for k in result.keys() if k != "last"][0]
    candles = result[key]

    cutoff = time.time() - (lookback_hours * 3600)
    parsed = []
    for c in candles:
        candle_time = c[0]
        if candle_time >= cutoff:
            parsed.append({
                "time": candle_time,
                "open": float(c[1]),
                "high": float(c[2]),
                "low": float(c[3]),
                "close": float(c[4]),
                "volume": float(c[6]),
            })
    return parsed


def get_momentum_pct(pair: str, lookback_hours: int = 6) -> float:
    """
    Calculate % price change over the lookback window.
    Positive = price went up, Negative = price went down.
    """
    candles = get_ohlc(pair, interval_minutes=60, lookback_hours=lookback_hours)
    if len(candles) < 2:
        return 0.0

    start_price = candles[0]["open"]
    end_price = candles[-1]["close"]
    if start_price == 0:
        return 0.0

    return ((end_price - start_price) / start_price) * 100
