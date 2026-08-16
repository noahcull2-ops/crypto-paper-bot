# Crypto Paper Trading Bot

A bot that watches Bitcoin, Ethereum, and Solana prices on Kraken,
reads crypto news headlines, and makes **simulated (fake money)**
trades based on price momentum + news sentiment. Runs automatically
every hour using GitHub Actions — you don't need a server.

**This does NOT trade with real money.** It's a practice/testing
version. Read "Going Live Later" at the bottom before ever
connecting a real account.

---

## Setup (no coding required)

### 1. Create a GitHub account
Go to [github.com](https://github.com) and sign up if you don't
already have an account.

### 2. Create a new repository
- Click the **+** icon (top right) → **New repository**
- Name it something like `crypto-paper-bot`
- Set it to **Private** (recommended)
- Click **Create repository**

### 3. Upload these files
On your new repo's page:
- Click **Add file → Upload files**
- Drag in every file from this project, keeping the folder
  structure (the `.github/workflows/trade.yml` file must stay
  inside a folder path called exactly `.github/workflows/`)
- Click **Commit changes**

### 4. Turn on Actions
- Go to the **Actions** tab on your repo
- If prompted, click **"I understand my workflows, go ahead and
  enable them"**
- You should see "Run Paper Trading Bot" listed

### 5. Run it manually the first time
- Click on **Run Paper Trading Bot** → **Run workflow** → **Run workflow**
  (green button)
- Wait ~30 seconds, then click into the run to see the bot's output
- After it finishes, check your repo — you should see two new files:
  - `portfolio.json` — your fake cash + holdings
  - `trade_log.csv` — a running log of every simulated trade

That's it — it will now run automatically every hour on its own.

---

## Checking on it

- **See recent trades:** open `trade_log.csv` in the repo (or download
  and open in Excel/Google Sheets)
- **See current fake portfolio:** open `portfolio.json`
- **See what happened on any run:** go to the **Actions** tab, click
  any run, and read the printed summary

## Adjusting how it trades

Everything tunable lives in `config.yaml` — no code editing needed.
Common tweaks:
- `pairs` — add/remove coins
- `position_size_pct` — how much of the portfolio goes into one trade
- `stop_loss_pct` / `take_profit_pct` — risk controls
- `momentum_buy_threshold_pct` / `sentiment_buy_threshold` — how
  strong a signal needs to be before it acts

Edit the file on GitHub (pencil icon), commit, and the next run
will use your new settings.

## Changing how often it runs

In `.github/workflows/trade.yml`, the line `cron: "0 * * * *"`
controls timing (currently hourly, in UTC time). GitHub Actions
schedules can drift by a few minutes and are not real-time — this
setup is not built for sub-minute latency trading.

---

## Going Live Later (real money) — read this first

This starter bot is intentionally simple and is **not** production-
grade risk management. Before ever connecting real funds:

1. **Paper trade for weeks, not days.** Watch how it performs
   across different market conditions.
2. **Understand the strategy's real weaknesses:**
   - News RSS feeds and rule-based sentiment scoring are crude —
     they'll miss nuance and can be wrong on sarcasm, ratios, etc.
   - Hourly-scheduled GitHub Actions is not fast enough for any
     kind of latency/arbitrage trading — that requires dedicated,
     low-latency infrastructure most retail traders don't have.
   - This has no protection against flash crashes, exchange
     outages, or API rate-limit failures mid-trade.
3. **When ready, we'd add:**
   - An authenticated Kraken client using your API key/secret,
     stored as encrypted **GitHub Secrets** (never written in code)
   - Real order placement with proper error handling and retries
   - Much stricter position sizing and a maximum daily loss limit
     that halts trading automatically
   - Logging/alerts (e.g., email or Discord ping) if something
     goes wrong

Trading is risky and this bot can lose money once live — even a
well-tested strategy can perform very differently with real
capital, slippage, and fees involved. Only risk money you can
afford to lose, and treat any backtest or paper-trading result as
optimistic compared to live performance.
