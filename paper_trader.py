"""
paper_trader.py
-----------------
Simulates a portfolio with fake money. No real trades happen here.
State is saved to portfolio.json, which GitHub Actions commits
back to the repo after every run - so your fake portfolio
persists between scheduled runs.
"""

import json
import os
from datetime import datetime, timezone

PORTFOLIO_FILE = "portfolio.json"
TRADE_LOG_FILE = "trade_log.csv"


def load_portfolio(starting_balance: float) -> dict:
    if os.path.exists(PORTFOLIO_FILE):
        with open(PORTFOLIO_FILE, "r") as f:
            return json.load(f)

    return {
        "cash_usd": starting_balance,
        "positions": {},  # e.g. {"XBTUSD": {"qty": 0.01, "entry_price": 60000}}
        "history": [],
    }


def save_portfolio(portfolio: dict):
    with open(PORTFOLIO_FILE, "w") as f:
        json.dump(portfolio, f, indent=2)


def log_trade(pair, action, price, qty, reason):
    is_new_file = not os.path.exists(TRADE_LOG_FILE)
    with open(TRADE_LOG_FILE, "a") as f:
        if is_new_file:
            f.write("timestamp,pair,action,price,qty,reason\n")
        ts = datetime.now(timezone.utc).isoformat()
        f.write(f"{ts},{pair},{action},{price},{qty},{reason}\n")


def buy(portfolio: dict, pair: str, price: float, position_size_pct: float, reason: str):
    if pair in portfolio["positions"]:
        return  # already holding this pair, don't double up

    spend = portfolio["cash_usd"] * position_size_pct
    if spend < 1 or spend > portfolio["cash_usd"]:
        return

    qty = spend / price
    portfolio["cash_usd"] -= spend
    portfolio["positions"][pair] = {"qty": qty, "entry_price": price}
    log_trade(pair, "BUY", price, qty, reason)


def sell(portfolio: dict, pair: str, price: float, reason: str):
    position = portfolio["positions"].get(pair)
    if not position:
        return

    qty = position["qty"]
    proceeds = qty * price
    portfolio["cash_usd"] += proceeds
    log_trade(pair, "SELL", price, qty, reason)
    del portfolio["positions"][pair]


def portfolio_value(portfolio: dict, current_prices: dict) -> float:
    total = portfolio["cash_usd"]
    for pair, pos in portfolio["positions"].items():
        price = current_prices.get(pair, pos["entry_price"])
        total += pos["qty"] * price
    return total
