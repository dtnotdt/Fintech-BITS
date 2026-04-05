"""
paper_trading.py — Simulated Paper Trading Module (Alpaca-compatible interface)

Acts as a sandboxed execution layer for paper trades routed through the
IntentShield policy engine. All orders are stored locally and never touch
real markets.
"""

import json
import os
import uuid
from datetime import datetime, timezone

ORDERS_PATH = os.path.join(os.path.dirname(__file__), "paper_orders.json")
POSITIONS_PATH = os.path.join(os.path.dirname(__file__), "paper_positions.json")

# Simulated fill prices (mirrors tools.py mock prices)
MOCK_PRICES = {
    "TSLA": 177.58, "AAPL": 189.30, "NVDA": 875.40, "MSFT": 415.20,
    "GOOGL": 165.80, "AMZN": 182.50, "META": 512.30, "NFLX": 628.00,
    "CRM": 273.50, "V": 275.80, "MA": 462.10, "PYPL": 65.40,
    "SHOP": 74.20, "UBER": 71.50, "DIS": 99.80, "BA": 168.90,
}


def _load_json(path: str, default) -> any:
    try:
        with open(path, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return default


def _save_json(path: str, data) -> None:
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def _get_fill_price(symbol: str) -> float:
    return MOCK_PRICES.get(symbol.upper(), 100.00)


def place_order(symbol: str, qty: int, side: str) -> dict:
    """
    Place a simulated paper trade order.
    side: 'buy' or 'sell'
    """
    symbol = symbol.upper()
    qty = int(qty) if qty else 1
    fill_price = _get_fill_price(symbol)
    order_value = round(fill_price * qty, 2)

    order = {
        "order_id": str(uuid.uuid4())[:8].upper(),
        "symbol": symbol,
        "qty": qty,
        "side": side,
        "fill_price": fill_price,
        "order_value": order_value,
        "status": "filled",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "source": "IntentShield Paper Trading",
    }

    # Persist order
    orders = _load_json(ORDERS_PATH, [])
    orders.insert(0, order)
    _save_json(ORDERS_PATH, orders)

    # Update positions
    positions = _load_json(POSITIONS_PATH, {})
    if side == "buy":
        if symbol in positions:
            old = positions[symbol]
            total_qty = old["qty"] + qty
            avg_price = round((old["avg_price"] * old["qty"] + fill_price * qty) / total_qty, 2)
            positions[symbol] = {"symbol": symbol, "qty": total_qty, "avg_price": avg_price, "current_price": fill_price}
        else:
            positions[symbol] = {"symbol": symbol, "qty": qty, "avg_price": fill_price, "current_price": fill_price}
    elif side == "sell":
        if symbol in positions:
            remaining = positions[symbol]["qty"] - qty
            if remaining <= 0:
                del positions[symbol]
            else:
                positions[symbol]["qty"] = remaining
                positions[symbol]["current_price"] = fill_price

    _save_json(POSITIONS_PATH, positions)

    return {
        "executed": True,
        "order": order,
        "message": f"Paper order {order['order_id']} filled: {side.upper()} {qty} x {symbol} @ ${fill_price}",
    }


def get_positions() -> dict:
    """Return all current open simulated positions."""
    positions = _load_json(POSITIONS_PATH, {})
    result = []
    for sym, pos in positions.items():
        current = _get_fill_price(sym)
        qty = pos["qty"]
        avg = pos["avg_price"]
        pnl = round((current - avg) * qty, 2)
        pnl_pct = round((current - avg) / avg * 100, 2) if avg else 0
        result.append({
            "symbol": sym,
            "qty": qty,
            "avg_price": avg,
            "current_price": current,
            "market_value": round(current * qty, 2),
            "unrealized_pnl": pnl,
            "pnl_pct": pnl_pct,
        })
    return {"positions": result, "count": len(result)}


def get_orders(limit: int = 10) -> dict:
    """Return recent paper trade order history."""
    orders = _load_json(ORDERS_PATH, [])
    return {"orders": orders[:limit], "count": len(orders)}


def cancel_order(order_id: str) -> dict:
    """Cancel a pending order by ID (simulation — marks as cancelled)."""
    orders = _load_json(ORDERS_PATH, [])
    for o in orders:
        if o["order_id"] == order_id.upper():
            o["status"] = "cancelled"
            _save_json(ORDERS_PATH, orders)
            return {"cancelled": True, "order_id": order_id}
    return {"cancelled": False, "error": f"Order {order_id} not found."}
