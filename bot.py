"""
bot.py
-----------------
Main entrypoint. This is what GitHub Actions runs on a schedule.

Flow each run:
  1. Load config
  2. For each coin: get price momentum + news sentiment
  3. Decide BUY / SELL / HOLD
  4. Check stop-loss / take-profit on existing positions
  5. Simulate the trade (paper money only)
  6. Save updated portfolio + print a summary
"""

import yaml

import kraken_client
import news_fetcher
import sentiment
import paper_trader


def load_config():
    with open("config.yaml", "r") as f:
        return yaml.safe_load(f)


def decide_signal(momentum_pct, sentiment_score, cfg):
    momentum_bullish = momentum_pct >= cfg["momentum_buy_threshold_pct"]
    momentum_bearish = momentum_pct <= cfg["momentum_sell_threshold_pct"]
    sentiment_bullish = sentiment_score >= cfg["sentiment_buy_threshold"]
    sentiment_bearish = sentiment_score <= cfg["sentiment_sell_threshold"]

    if cfg["require_signal_agreement"]:
        if momentum_bullish and sentiment_bullish:
            return "BUY"
        if momentum_bearish and sentiment_bearish:
            return "SELL"
    else:
        if momentum_bullish or sentiment_bullish:
            return "BUY"
        if momentum_bearish or sentiment_bearish:
            return "SELL"

    return "HOLD"


def check_stop_loss_take_profit(portfolio, pair, current_price, cfg):
    position = portfolio["positions"].get(pair)
    if not position:
        return

    entry = position["entry_price"]
    change_pct = ((current_price - entry) / entry) * 100

    if change_pct <= cfg["stop_loss_pct"]:
        paper_trader.sell(portfolio, pair, current_price, reason="stop_loss")
        print(f"  -> STOP-LOSS triggered on {pair} ({change_pct:.2f}%)")
    elif change_pct >= cfg["take_profit_pct"]:
        paper_trader.sell(portfolio, pair, current_price, reason="take_profit")
        print(f"  -> TAKE-PROFIT triggered on {pair} ({change_pct:.2f}%)")


def main():
    cfg = load_config()
    portfolio = paper_trader.load_portfolio(cfg["starting_balance_usd"])
    current_prices = {}

    print("=" * 60)
    print("CRYPTO PAPER TRADING BOT - RUN START")
    print("=" * 60)

    for coin in cfg["pairs"]:
        pair = coin["symbol"]
        news_query = coin["news_query"]

        try:
            price = kraken_client.get_current_price(pair)
            momentum_pct = kraken_client.get_momentum_pct(
                pair, lookback_hours=cfg["momentum_lookback_hours"]
            )
        except Exception as e:
            print(f"[{pair}] Skipping - price data error: {e}")
            continue

        current_prices[pair] = price

        try:
            headlines = news_fetcher.get_recent_headlines(news_query, hours=12)
            sentiment_score = sentiment.score_headlines(headlines)
        except Exception as e:
            print(f"[{pair}] News fetch failed, treating sentiment as neutral: {e}")
            headlines = []
            sentiment_score = 0.0

        print(f"\n[{pair}] price=${price:,.2f} | momentum={momentum_pct:+.2f}% "
              f"| sentiment={sentiment_score:+.2f} | headlines_found={len(headlines)}")

        # First check if an existing position needs to be stopped out / cashed in
        check_stop_loss_take_profit(portfolio, pair, price, cfg)

        signal = decide_signal(momentum_pct, sentiment_score, cfg)
        print(f"  -> Signal: {signal}")

        if signal == "BUY":
            paper_trader.buy(
                portfolio, pair, price, cfg["position_size_pct"],
                reason=f"momentum={momentum_pct:.2f},sentiment={sentiment_score:.2f}",
            )
        elif signal == "SELL":
            paper_trader.sell(
                portfolio, pair, price,
                reason=f"momentum={momentum_pct:.2f},sentiment={sentiment_score:.2f}",
            )

    paper_trader.save_portfolio(portfolio)

    total_value = paper_trader.portfolio_value(portfolio, current_prices)
    starting = cfg["starting_balance_usd"]
    pnl_pct = ((total_value - starting) / starting) * 100

    print("\n" + "=" * 60)
    print(f"Portfolio value: ${total_value:,.2f}  (P&L: {pnl_pct:+.2f}%)")
    print(f"Cash: ${portfolio['cash_usd']:,.2f} | Open positions: {list(portfolio['positions'].keys())}")
    print("=" * 60)


if __name__ == "__main__":
    main()
