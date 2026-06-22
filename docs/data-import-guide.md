# Data Import Guide

Mahiro Invest supports two stock-universe import paths. Use them depending on what you want to screen.

## NSE Universe

Use **Refresh NSE Universe** in the Screener page when you want symbols from NSE's official listed securities CSV.

This path is best for:

- NSE-focused screening.
- Symbols that map cleanly to yfinance with `.NS`.
- Faster refreshes.

Backend endpoint:

```http
POST /stocks/refresh-universe
```

## Screener All-Listed Universe

Use **Import Screener List** in the Screener page when you want the broader Screener.in all-listed companies screen.

This path reads:

```text
https://www.screener.in/screens/357649/all-listed-companies/
```

It imports the paginated table and stores available table values such as:

- Current market price.
- P/E.
- Market cap.
- Dividend yield.
- Quarterly profit and sales values in raw JSON.

Alphabetic Screener company codes are mapped to `.NS` symbols. Numeric company codes are stored as `BSE:CODE` so the app does not silently drop them.

Backend endpoint:

```http
POST /stocks/refresh-screener-universe
```

## Notes

- The Screener import can take longer because it walks many pages.
- Some values may still be estimated or missing because public data sources vary by company.
- Respect Screener.in's terms and rate limits when refreshing the full list.
