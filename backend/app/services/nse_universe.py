from __future__ import annotations

import csv
import io

import requests

from app.services.defaults import fallback_equity_universe

NSE_EQUITY_LIST_URL = "https://archives.nseindia.com/content/equities/EQUITY_L.csv"


def fetch_nse_equity_universe(timeout: int = 12) -> list[tuple[str, str, str]]:
    """Fetch all NSE equity symbols from NSE's official equity list CSV.

    Returns tuples of (yfinance_symbol, company_name, sector). NSE's public equity
    list does not include sector, so sector is marked as "NSE Listed".
    """
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "text/csv,text/plain,*/*",
        "Referer": "https://www.nseindia.com/",
    }
    try:
        response = requests.get(NSE_EQUITY_LIST_URL, headers=headers, timeout=timeout)
        response.raise_for_status()
        reader = csv.DictReader(io.StringIO(response.text))
        rows: list[tuple[str, str, str]] = []
        for row in reader:
            symbol = (row.get("SYMBOL") or "").strip().upper()
            name = (row.get("NAME OF COMPANY") or symbol).strip()
            series = (row.get(" SERIES") or row.get("SERIES") or "").strip().upper()
            if symbol and series == "EQ":
                rows.append((f"{symbol}.NS", name, "NSE Listed"))
        return rows or fallback_equity_universe()
    except Exception:
        return fallback_equity_universe()
