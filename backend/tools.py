import os
import requests

FINNHUB_BASE = "https://finnhub.io/api/v1"
TAVILY_BASE = "https://api.tavily.com"


def _finnhub_headers():
    return {"X-Finnhub-Token": os.getenv("FINNHUB_API_KEY", "")}


def get_stock_price(symbol: str) -> dict:
    """Fetch real-time stock quote from Finnhub."""
    api_key = os.getenv("FINNHUB_API_KEY", "")
    if not api_key or api_key == "YOUR_FINNHUB_KEY":
        return _mock_stock_price(symbol)
    try:
        resp = requests.get(
            f"{FINNHUB_BASE}/quote",
            params={"symbol": symbol.upper()},
            headers=_finnhub_headers(),
            timeout=8,
        )
        data = resp.json()
        if data.get("c", 0) == 0:
            return _mock_stock_price(symbol)
        return {
            "symbol": symbol.upper(),
            "current_price": data["c"],
            "open": data["o"],
            "high": data["h"],
            "low": data["l"],
            "previous_close": data["pc"],
            "change": round(data["c"] - data["pc"], 2),
            "change_pct": round((data["c"] - data["pc"]) / data["pc"] * 100, 2) if data["pc"] else 0,
            "source": "Finnhub",
        }
    except Exception as e:
        print(f"[Tools] Finnhub error: {e}")
        return _mock_stock_price(symbol)


def get_company_profile(symbol: str) -> dict:
    """Fetch company profile from Finnhub."""
    api_key = os.getenv("FINNHUB_API_KEY", "")
    if not api_key or api_key == "YOUR_FINNHUB_KEY":
        return {"symbol": symbol, "name": symbol, "source": "mock"}
    try:
        resp = requests.get(
            f"{FINNHUB_BASE}/stock/profile2",
            params={"symbol": symbol.upper()},
            headers=_finnhub_headers(),
            timeout=8,
        )
        data = resp.json()
        return {
            "symbol": symbol.upper(),
            "name": data.get("name", symbol),
            "industry": data.get("finnhubIndustry", "N/A"),
            "market_cap": data.get("marketCapitalization", "N/A"),
            "exchange": data.get("exchange", "N/A"),
            "ipo": data.get("ipo", "N/A"),
            "logo": data.get("logo", ""),
            "weburl": data.get("weburl", ""),
            "source": "Finnhub",
        }
    except Exception as e:
        print(f"[Tools] Finnhub profile error: {e}")
        return {"symbol": symbol, "source": "error"}


def compare_companies(symbols: list) -> list:
    """Compare multiple companies using Finnhub data."""
    results = []
    for sym in symbols[:3]:  # cap at 3
        price = get_stock_price(sym)
        profile = get_company_profile(sym)
        results.append({**price, **{k: v for k, v in profile.items() if k not in price}})
    return results


def research_company(query: str) -> dict:
    """Use Tavily to research a company via live web search."""
    api_key = os.getenv("TAVILY_API_KEY", "")
    if not api_key or api_key == "YOUR_TAVILY_KEY":
        return {
            "query": query,
            "results": [{"title": "Mock Result", "content": f"This is a mock research result for: {query}. Add your Tavily API key to get live results."}],
            "images": ["https://via.placeholder.com/800x400?text=Mock+Company+Image+1", "https://via.placeholder.com/800x400?text=Mock+Company+Image+2"],
            "source": "mock",
        }
    try:
        resp = requests.post(
            f"{TAVILY_BASE}/search",
            headers={"Content-Type": "application/json"},
            json={
                "api_key": api_key,
                "query": f"{query} company business products recent developments",
                "search_depth": "basic",
                "max_results": 5
            },
            timeout=15,
        )
        data = resp.json()
        
        if resp.status_code != 200 or "error" in data or "detail" in data:
            err_msg = data.get("error", data.get("detail", f"HTTP {resp.status_code}"))
            print(f"[Tools] Tavily API Error: {err_msg}")
            return {"query": query, "error": err_msg}
            
        return {
            "query": query,
            "results": [
                {"title": r.get("title", ""), "content": r.get("content", ""), "url": r.get("url", "")}
                for r in data.get("results", [])[:4]
            ],
            "images": data.get("images", []),
            "source": "Tavily",
        }
    except Exception as e:
        print(f"[Tools] Tavily error: {e}")
        return {"query": query, "error": str(e)}


# ─── Mock fallbacks ───────────────────────────────────────────────────────────

MOCK_PRICES = {
    "TSLA": {"current_price": 177.58, "open": 175.00, "high": 180.12, "low": 174.50, "previous_close": 176.40, "change": 1.18, "change_pct": 0.67},
    "AAPL": {"current_price": 189.30, "open": 187.50, "high": 191.00, "low": 186.80, "previous_close": 188.00, "change": 1.30, "change_pct": 0.69},
    "NVDA": {"current_price": 875.40, "open": 860.00, "high": 880.00, "low": 855.00, "previous_close": 865.00, "change": 10.40, "change_pct": 1.20},
    "MSFT": {"current_price": 415.20, "open": 412.00, "high": 418.00, "low": 410.50, "previous_close": 413.00, "change": 2.20, "change_pct": 0.53},
    "GOOGL": {"current_price": 165.80, "open": 163.00, "high": 167.00, "low": 162.50, "previous_close": 164.00, "change": 1.80, "change_pct": 1.10},
    "AMZN": {"current_price": 182.50, "open": 180.00, "high": 184.00, "low": 179.50, "previous_close": 181.00, "change": 1.50, "change_pct": 0.83},
    "META": {"current_price": 512.30, "open": 508.00, "high": 515.00, "low": 507.00, "previous_close": 510.00, "change": 2.30, "change_pct": 0.45},
}


def _mock_stock_price(symbol: str) -> dict:
    sym = symbol.upper()
    base = MOCK_PRICES.get(sym, {"current_price": 100.00, "open": 99.00, "high": 102.00, "low": 98.00, "previous_close": 99.50, "change": 0.50, "change_pct": 0.50})
    return {"symbol": sym, **base, "source": "mock"}
