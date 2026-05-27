# Mahiro Invest

> A personalized NSE stock screener and portfolio tracker — built to replace my father's 16-criteria Excel-based stock evaluation workflow.

<!-- Replace this with a real screenshot/GIF once UI is built -->
<p align="center">
  <em>📸 Hero screenshot / demo GIF coming soon</em>
</p>

---

## The Problem

My father manages a personal stock portfolio across **65+ NSE-listed companies** and tracks a watchlist of **900+ stocks**. His investment methodology is rigorous — he evaluates every stock against **16 hand-picked criteria** spanning fundamental, technical, and macro signals.

But the workflow lives in Excel. Every evaluation means:

- Manually pulling P/E, ROE, debt ratios, cash flow data from screener.in
- Cross-checking technical signals (20-DMA vs 200-DMA) on TradingView
- Reading earnings dates from NSE
- Repeating this for *every single stock* on the watchlist

It takes **~30 minutes per stock**. At 900 stocks, complete coverage is impossible. He ends up evaluating only a small subset.

**Mahiro Invest is built to do this evaluation automatically — for the entire NSE universe — in seconds.**

---

## What It Does

Three integrated modules:

### 1. Stock Screener
Scans the NSE universe (~900 stocks) and returns the handful that pass all 15 hard-filter criteria, ranked by composite score.

### 2. Portfolio Tracker
Tracks current holdings, computes live P&L, and **alerts immediately** when any holding starts violating the user's criteria (e.g., debt suddenly increases).

### 3. Earnings Calendar
Surfaces stocks with upcoming earnings (next 7 days) that currently match all criteria — supporting the "buy before earnings" strategy.

---

## The Persona Engine (Core Novelty)

The heart of the app is a **configurable investor persona** — a JSON schema that captures *exactly* how a specific investor evaluates stocks.

Persona #1 is my father — a long-term quality investor. His persona is structured as:

| # | Hard Filter | Rule |
|---|---|---|
| 1 | Market Cap | ≥ ₹5,000 Cr (no small-caps) |
| 2 | P/E Ratio | Between 20 – 25 |
| 3 | Revenue Growth (YoY) | > 10%, sustained over 3+ years |
| 4 | Profit Margin | > 10% |
| 5 | EPS | Increasing every year, last 3+ years |
| 6 | Working Capital Ratio | ≥ 2 |
| 7 | Quick Ratio | > 1 |
| 8 | Debt-to-Equity | < 1 |
| 9 | P/B Ratio | < 2 |
| 10 | Debtor Days | < 100 |
| 11 | Public Holding | < 35% |
| 12 | Cash Flow | Positive and growing YoY |
| 13 | FII + DII Holding | Increasing trend |
| 14 | 20DMA vs 200DMA | Golden Cross (20DMA > 200DMA) |
| 15 | ROE | ≥ 15% |

Stocks that pass all filters are then ranked by a weighted composite score across his top-5 most important metrics: revenue growth, profit margin, EPS growth, debt-to-equity, and ROE.

**Why this is interesting:** Different investors weigh metrics differently. Instead of hardcoding rules, the persona engine lets any user (or AI assistant) configure their own quality-investing strategy. My dad becomes Persona #1; a dividend hunter would be Persona #2; an aggressive swing trader, Persona #3.

---

## Novelty Features

Beyond the screener basics, three differentiators:

### 🤖 ML-based Anomaly Detection
An Isolation Forest model trained on 5 years of quarterly fundamentals across ~100 NSE stocks flags companies whose current metrics look *unusual versus their own history* — e.g., "debt jumped 40% YoY despite passing the static D/E filter." Catches problems that threshold-based rules miss.

### 💬 LLM-generated Explanations
For each ranked stock, an LLM (Gemini Flash) generates a 3-line plain-English summary explaining *why* it scored high or low, citing actual metric values. Makes the app usable by my father without him reading raw tables.

### 🔔 Persona-driven Alerts
The portfolio tracker enforces my father's stated rule — *"sell immediately if any criterion is violated"* — by re-evaluating holdings against the persona daily and pushing alerts when any hard filter flips to fail.

---

## Tech Stack

| Layer | Tech | Why |
|---|---|---|
| Frontend | React (Vite) + Tailwind + Recharts | Fast dev, clean charts |
| Backend | FastAPI (Python) | Same language as ML code, fast |
| Database | PostgreSQL | Relational, perfect for stock/persona data |
| Cache | Redis | Aggressive caching of API responses |
| Data Sources | yfinance + screener.in + NSE site | Layered fallbacks for messy Indian data |
| ML | scikit-learn (Isolation Forest) | Anomaly detection on fundamentals |
| LLM | Gemini Flash (with response caching) | Cheap, fast explanations |
| Auth | Clerk / Supabase Auth | No reinventing the wheel |
| Deploy | Vercel (frontend) + Render (backend) + Neon (DB) | Free tiers cover the demo |

---

## Architecture

```
┌─────────────────────────────────────────────────────┐
│  React Frontend (Vercel)                            │
│  Dashboard · Persona Builder · Stock Detail         │
└────────────────────┬────────────────────────────────┘
                     │ REST
┌────────────────────▼────────────────────────────────┐
│  FastAPI Backend (Render)                           │
│  ┌──────────────┐ ┌──────────────┐ ┌─────────────┐  │
│  │ Data Fetcher │ │  Scoring     │ │  ML Module  │  │
│  │ (yfinance,   │ │  Engine      │ │  (anomaly   │  │
│  │  scraper)    │ │  (persona-   │ │   detection)│  │
│  │              │ │   driven)    │ │             │  │
│  └──────┬───────┘ └──────┬───────┘ └──────┬──────┘  │
│         │                │                │         │
│  ┌──────▼────────────────▼────────────────▼──────┐  │
│  │  LLM Explainer (Gemini Flash + Cache)         │  │
│  └───────────────────────────────────────────────┘  │
└──────┬──────────────────────────────┬───────────────┘
       │                              │
   PostgreSQL                      Redis
   (Neon — users, personas,    (Upstash — API cache,
    watchlists, holdings,       LLM cache, ML preds)
    historical fundamentals)
```

---

## Roadmap

This is a 4-week solo build. Status updates per phase:

### Week 1 — Foundation & Data Pipeline ⏳
- Project scaffold, deployment skeleton end-to-end
- Data fetcher: yfinance + screener.in fallback
- Redis caching layer
- Technical indicator computation (pandas-ta)

### Week 2 — Scoring Engine + Persona System ⏳
- Persona JSON schema + CRUD APIs
- Scoring engine: hard filters + weighted composite ranking
- Dashboard UI: paste watchlist, pick persona, see ranked table
- Per-stock detail view

### Week 3 — ML Anomaly Detection + LLM Explanations ⏳
- Train Isolation Forest on 5 yrs quarterly fundamentals
- LLM-generated stock explanations (with caching)
- Portfolio violation alerts

### Week 4 — Polish, Deploy, Document ⏳
- Auth, error handling, loading states
- Production deployment
- Demo video + final README polish

---

## Project Status

🚧 **Currently in Week 1 (Foundation & Data Pipeline).**

Follow commits for daily progress.

---

## Why This Project Exists (The Real Story)

This isn't a CRUD app or a tutorial follow-along. It started because my father handed me his Excel sheet of 65 stocks and a list of criteria, and asked me to manually evaluate each one. Halfway through stock #3, I realized this had to be automated.

The whole point of Mahiro Invest is to take **one specific person's** real, hard-won investment methodology, encode it precisely, and execute it at scale. The "Persona Engine" exists because that methodology shouldn't be hardcoded — it should be portable, so any investor can capture *their own* rules.

If it works for my father, the next step is making it work for anyone who has a strategy and a watchlist.

---

## License

MIT

---

## Disclaimer

Mahiro Invest is an **analysis tool**, not a financial advisory or buy/sell recommender. All outputs are informational. Investment decisions are the user's own. Past performance does not guarantee future results.

---

## About the Name

**Mahiro** combines the names of two people who matter to me — **Mahi** and **Shiro**. The project itself is dedicated to my father (Persona #1) and the family.
