"""
screener.in scraper.

Pulls fundamentals from screener.in's company page. More complete data than yfinance,
but requires HTML scraping. Fragile by nature — selectors will break if screener changes
their page structure.

Layered with yfinance: yfinance gives reliable basics (price, market cap, sector),
screener fills in the metrics yfinance doesn't expose (debtor days, working capital,
public holding, cash flow trend).
"""
from __future__ import annotations

import logging
import re
from typing import Any

import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

SCREENER_BASE_URL = "https://www.screener.in/company"
DEFAULT_TIMEOUT_SECONDS = 15

# Mimic a real browser. screener.in does not require login for public pages,
# but it blocks obvious bot User-Agents.
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}


def _strip_ns_suffix(ticker: str) -> str:
    """Convert 'RELIANCE.NS' -> 'RELIANCE' for screener.in's URL scheme."""
    return ticker.upper().replace(".NS", "").replace(".BO", "")


def _parse_indian_number(text: str | None) -> float | None:
    """
    Parse Indian-formatted numbers: '1,82,756.38' -> 182756.38, '12.5 %' -> 12.5.
    Handles '₹', ',', '%', 'Cr.', and surrounding whitespace.
    Returns None if not parseable.
    """
    if text is None:
        return None
    cleaned = text.strip()
    # Strip common suffixes/prefixes
    for token in ["₹", ",", "%", "Cr.", "Cr", "days", " "]:
        cleaned = cleaned.replace(token, "")
    if cleaned == "" or cleaned == "-":
        return None
    try:
        return float(cleaned)
    except ValueError:
        return None


def _fetch_html(url: str) -> str:
    """Fetch raw HTML with proper headers and timeout. Raises on HTTP error."""
    logger.info(f"Fetching screener.in: {url}")
    response = requests.get(url, headers=HEADERS, timeout=DEFAULT_TIMEOUT_SECONDS)
    if response.status_code == 404:
        raise ValueError(f"Stock not found on screener.in: {url}")
    response.raise_for_status()
    return response.text


def _extract_top_ratios(soup: BeautifulSoup) -> dict[str, float | None]:
    """
    Parse the 'Ratios' panel at the top of the page.
    
    HTML structure (as of 2026):
        <ul id="top-ratios">
          <li>
            <span class="name">Market Cap</span>
            <span class="value">₹ 18,27,560 Cr.</span>
          </li>
          ...
        </ul>
    """
    ratios: dict[str, float | None] = {}
    top_ul = soup.find("ul", id="top-ratios")
    if not top_ul:
        logger.warning("Could not find #top-ratios on page")
        return ratios

    for li in top_ul.find_all("li"):
        name_el = li.find("span", class_="name")
        value_el = li.find("span", class_="number")
        if not name_el or not value_el:
            continue
        name = name_el.get_text(strip=True).lower()
        value = _parse_indian_number(value_el.get_text(strip=True))
        ratios[name] = value
    return ratios


def _extract_ratios_table(soup: BeautifulSoup) -> dict[str, float | None]:
    """
    Parse the 'Ratios' section table further down the page.
    Contains debtor days, working capital days, inventory days, etc.

    HTML structure: a <section id="ratios"> with a <table> inside.
    Each <tr> has the metric name in <td> and yearly values in subsequent <td>s.
    We want the LATEST (rightmost) column.
    """
    ratios: dict[str, float | None] = {}
    section = soup.find("section", id="ratios")
    if not section:
        logger.warning("Could not find #ratios section")
        return ratios

    table = section.find("table")
    if not table:
        return ratios

    for row in table.find_all("tr"):
        cells = row.find_all("td")
        if len(cells) < 2:
            continue
        metric_name = cells[0].get_text(strip=True).lower()
        # Get the rightmost (latest) value column
        latest_value = _parse_indian_number(cells[-1].get_text(strip=True))
        ratios[metric_name] = latest_value
    return ratios


def _extract_shareholding(soup: BeautifulSoup) -> dict[str, float | None]:
    """
    Parse the 'Shareholding Pattern' section.
    We want the most recent quarter's public holding (Promoters + Non-Promoters split).
    """
    holding: dict[str, float | None] = {}
    section = soup.find("section", id="shareholding")
    if not section:
        return holding

    # Quarterly tab is the default; rows include 'Promoters', 'FIIs', 'DIIs', 'Public', etc.
    table = section.find("table")
    if not table:
        return holding

    for row in table.find_all("tr"):
        cells = row.find_all("td")
        if len(cells) < 2:
            continue
        holder_type = cells[0].get_text(strip=True).lower()
        latest_pct = _parse_indian_number(cells[-1].get_text(strip=True))
        holding[holder_type] = latest_pct
    return holding


def fetch_fundamentals(ticker: str) -> dict[str, Any]:
    """
    Fetch fundamentals from screener.in.
    
    Args:
        ticker: NSE ticker, with or without .NS suffix.
    
    Returns:
        dict with 'meta' (stock-level) and 'snapshot' (fundamentals),
        matching the same shape as yfinance_fetcher.fetch_fundamentals().
    """
    clean_ticker = _strip_ns_suffix(ticker)
    url = f"{SCREENER_BASE_URL}/{clean_ticker}/consolidated/"

    html = _fetch_html(url)
    soup = BeautifulSoup(html, "lxml")

    # Get stock name from the page header
    title_el = soup.find("h1")
    name = title_el.get_text(strip=True) if title_el else clean_ticker

    top_ratios = _extract_top_ratios(soup)
    ratios_table = _extract_ratios_table(soup)
    shareholding = _extract_shareholding(soup)

    # --- Direct mappings ---
    market_cap_cr = top_ratios.get("market cap")
    pe_ratio = top_ratios.get("stock p/e")
    roe_pct = top_ratios.get("roe") or ratios_table.get("roe %")
    dividend_yield_pct = top_ratios.get("dividend yield")
    debtor_days = ratios_table.get("debtor days")

    # --- Computed: pb_ratio from current price / book value ---
    # screener doesn't always show "Price to Book" in top ratios, but always shows both
    # current price and book value. We compute the ratio.
    current_price = top_ratios.get("current price")
    book_value = top_ratios.get("book value")
    if current_price and book_value and book_value != 0:
        pb_ratio = round(current_price / book_value, 2)
    else:
        pb_ratio = top_ratios.get("price to book value") or top_ratios.get("p/b")

    # --- Public holding: screener uses "+" suffix in keys (e.g. "public+") ---
    # Look for any key starting with "public" since the "+" varies by stock layout.
    public_holding_pct = None
    for key, value in shareholding.items():
        if key.startswith("public"):
            public_holding_pct = value
            break

    # debt_to_equity isn't reliably in top_ratios or ratios_table on screener;
    # we defer to yfinance for this. Merger will handle it.
    debt_to_equity = ratios_table.get("debt / equity")  # usually None, that's fine

    # Quick ratio also often missing; we let merger fill from yfinance.
    quick_ratio = ratios_table.get("quick ratio")

    meta = {
        "ticker": ticker.upper(),
        "name": name,
        "sector": None,
        "industry": None,
        "market_cap_cr": market_cap_cr,
    }

    snapshot = {
        "pe_ratio": pe_ratio,
        "pb_ratio": pb_ratio,
        "roe_pct": roe_pct,
        "debt_to_equity": debt_to_equity,
        "revenue_growth_yoy_pct": None,
        "profit_margin_pct": None,
        "eps": None,
        "eps_growth_pct": None,
        "working_capital_ratio": None,
        "quick_ratio": quick_ratio,
        "debtor_days": debtor_days,
        "public_holding_pct": public_holding_pct,
        "dividend_yield_pct": dividend_yield_pct,
        "cash_flow_positive": None,
        "source": "screener",
        "raw_data": {
            "top_ratios": top_ratios,
            "ratios_table": ratios_table,
            "shareholding": shareholding,
            "current_price": current_price,
            "book_value": book_value,
        },
    }

    return {"meta": meta, "snapshot": snapshot}
    """
    Fetch fundamentals from screener.in.
    
    Args:
        ticker: NSE ticker, with or without .NS suffix.
    
    Returns:
        dict with 'meta' (stock-level) and 'snapshot' (fundamentals),
        matching the same shape as yfinance_fetcher.fetch_fundamentals().
    """
    clean_ticker = _strip_ns_suffix(ticker)
    url = f"{SCREENER_BASE_URL}/{clean_ticker}/consolidated/"

    html = _fetch_html(url)
    soup = BeautifulSoup(html, "lxml")

    # Get stock name from the page header
    title_el = soup.find("h1")
    name = title_el.get_text(strip=True) if title_el else clean_ticker

    top_ratios = _extract_top_ratios(soup)
    ratios_table = _extract_ratios_table(soup)
    shareholding = _extract_shareholding(soup)

    # Map screener's field names to our schema
    market_cap_cr = top_ratios.get("market cap")
    pe_ratio = top_ratios.get("stock p/e")
    pb_ratio = top_ratios.get("price to book value") or top_ratios.get("p/b")
    roe_pct = top_ratios.get("roe") or ratios_table.get("roe %")
    debt_to_equity = ratios_table.get("debt / equity")
    dividend_yield_pct = top_ratios.get("dividend yield")

    # Debtor days from ratios table (the field your dad cares about)
    debtor_days = ratios_table.get("debtor days")

    # Public holding = 100 - promoter holding (close approximation)
    promoter_pct = shareholding.get("promoters") or shareholding.get("promoter")
    public_holding_pct = (100.0 - promoter_pct) if promoter_pct is not None else None

    # Try to find quick ratio and working capital
    quick_ratio = ratios_table.get("quick ratio")
    working_capital_days = ratios_table.get("working capital days")

    meta = {
        "ticker": ticker.upper(),  # store with .NS suffix for consistency with yfinance
        "name": name,
        "sector": None,  # screener doesn't expose this in a stable selector
        "industry": None,
        "market_cap_cr": market_cap_cr,
    }

    snapshot = {
        "pe_ratio": pe_ratio,
        "pb_ratio": pb_ratio,
        "roe_pct": roe_pct,
        "debt_to_equity": debt_to_equity,
        "revenue_growth_yoy_pct": None,  # would need to compute from quarterly table; deferring
        "profit_margin_pct": None,
        "eps": None,
        "eps_growth_pct": None,
        "working_capital_ratio": None,  # screener reports days, not ratio; deferring
        "quick_ratio": quick_ratio,
        "debtor_days": debtor_days,
        "public_holding_pct": public_holding_pct,
        "dividend_yield_pct": dividend_yield_pct,
        "cash_flow_positive": None,  # would parse cash flow section; deferring
        "source": "screener",
        "raw_data": {
            "top_ratios": top_ratios,
            "ratios_table": ratios_table,
            "shareholding": shareholding,
            "working_capital_days": working_capital_days,
        },
    }

    return {"meta": meta, "snapshot": snapshot}