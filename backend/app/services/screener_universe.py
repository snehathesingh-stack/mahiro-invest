from __future__ import annotations

import re
from datetime import date
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

from app.models import FundamentalSnapshot, Stock
from app.services.defaults import sample_fundamentals

SCREENER_ALL_LISTED_URL = "https://www.screener.in/screens/357649/all-listed-companies/"


def _number(value: str | None) -> float | None:
    if not value:
        return None
    cleaned = value.replace(",", "").strip()
    if not cleaned:
        return None
    try:
        return float(cleaned)
    except ValueError:
        return None


def _symbol_from_company_href(href: str) -> str | None:
    match = re.search(r"/company/([^/]+)/?", href or "")
    if not match:
        return None
    code = match.group(1).strip().upper()
    if not code:
        return None
    return f"BSE:{code}" if code.isdigit() else f"{code}.NS"


def _fetch_page(page: int, timeout: int) -> tuple[list[dict], int | None]:
    response = requests.get(
        SCREENER_ALL_LISTED_URL,
        params={"page": page},
        headers={"User-Agent": "Mozilla/5.0", "Accept": "text/html,*/*"},
        timeout=timeout,
    )
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")
    text = soup.get_text(" ", strip=True)
    page_count = None
    page_match = re.search(r"Showing page\s+\d+\s+of\s+(\d+)", text)
    if page_match:
        page_count = int(page_match.group(1))

    rows: list[dict] = []
    for tr in soup.select("table tr"):
        cells = [cell.get_text(" ", strip=True) for cell in tr.select("td")]
        link = tr.select_one('a[href*="/company/"]')
        if len(cells) < 11 or not link:
            continue
        href = urljoin(SCREENER_ALL_LISTED_URL, link.get("href", ""))
        symbol = _symbol_from_company_href(href)
        if not symbol:
            continue
        rows.append(
            {
                "symbol": symbol,
                "company_name": cells[1],
                "cmp": _number(cells[2]),
                "pe_ratio": _number(cells[3]),
                "market_cap_cr": _number(cells[4]),
                "dividend_yield": _number(cells[5]),
                "quarterly_net_profit_cr": _number(cells[6]),
                "quarterly_profit_growth_pct": _number(cells[7]),
                "quarterly_sales_cr": _number(cells[8]),
                "quarterly_sales_growth_pct": _number(cells[9]),
                "roce_pct": _number(cells[10]),
                "screener_url": href,
            }
        )
    return rows, page_count


def sync_screener_all_listed(db, max_pages: int | None = None, timeout: int = 15) -> dict:
    first_rows, page_count = _fetch_page(1, timeout)
    total_pages = page_count or 1
    if max_pages:
        total_pages = min(total_pages, max_pages)

    rows = first_rows
    for page in range(2, total_pages + 1):
        page_rows, _ = _fetch_page(page, timeout)
        rows.extend(page_rows)

    added = 0
    updated = 0
    seen: set[str] = set()
    for row in rows:
        symbol = row["symbol"]
        if symbol in seen:
            continue
        seen.add(symbol)
        fallback = sample_fundamentals(symbol)
        stock = db.query(Stock).filter(Stock.symbol == symbol).first()
        if not stock:
            stock = Stock(symbol=symbol, company_name=row["company_name"], sector="Screener Listed")
            db.add(stock)
            db.flush()
            added += 1
        else:
            updated += 1
        stock.company_name = row["company_name"] or stock.company_name
        stock.sector = stock.sector or "Screener Listed"
        if row["market_cap_cr"] is not None:
            stock.market_cap = row["market_cap_cr"] * 10_000_000
        if row["cmp"] is not None:
            stock.last_price = row["cmp"]

        snapshot = fallback["snapshot"].copy()
        snapshot.update(
            {
                "pe_ratio": row["pe_ratio"] if row["pe_ratio"] is not None else snapshot["pe_ratio"],
                "dividend_yield": row["dividend_yield"] if row["dividend_yield"] is not None else snapshot["dividend_yield"],
                "raw_json": {
                    **snapshot["raw_json"],
                    "source_date": date.today().isoformat(),
                    "screener": row,
                },
            }
        )
        db.add(FundamentalSnapshot(stock_id=stock.id, source="screener", **snapshot))

    db.commit()
    return {
        "source": SCREENER_ALL_LISTED_URL,
        "pages_scanned": total_pages,
        "rows_seen": len(rows),
        "symbols_synced": len(seen),
        "added": added,
        "updated": updated,
        "stock_count": db.query(Stock).count(),
    }
