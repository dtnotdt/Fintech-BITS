"""
alpaca_trading.py — Live Simulated Paper Trading via Alpaca API

Provides live market execution capability for the IntentShield pipeline.
Uses alpaca-py to interact with the Alpaca Paper Trading environment.
Includes a graceful fallback (mock data) if API keys are missing to ensure
demonstrations for Hackathon judges don't crash.
"""

import os
import json
import uuid
from datetime import datetime, timezone

try:
    from alpaca.trading.client import TradingClient
    from alpaca.trading.requests import MarketOrderRequest
    from alpaca.trading.enums import OrderSide, TimeInForce
    HAS_ALPACA = True
except ImportError:
    HAS_ALPACA = False


ALPACA_API_KEY = os.getenv("ALPACA_API_KEY")
ALPACA_SECRET_KEY = os.getenv("ALPACA_SECRET_KEY")

# Determine if we should run in live paper mode or mock mode
USE_LIVE_ALPACA = HAS_ALPACA and ALPACA_API_KEY and ALPACA_SECRET_KEY and ALPACA_API_KEY != "your_alpaca_api_key_here"

if USE_LIVE_ALPACA:
    trading_client = TradingClient(ALPACA_API_KEY, ALPACA_SECRET_KEY, paper=True)
else:
    trading_client = None
    print("[🛡️ ARMORCLAW WARNING] Live Alpaca credentials missing or invalid. Falling back to internal mock simulator.")


# ==========================================
# MOCK FALLBACK STATE (replaces local JSONs)
# ==========================================
MOCK_PRICES = {
    "TSLA": 177.58, "AAPL": 189.30, "NVDA": 875.40, "MSFT": 415.20,
    "GOOGL": 165.80, "AMZN": 182.50, "META": 512.30, "NFLX": 628.00,
    "CRM": 273.50, "V": 275.80, "MA": 462.10, "PYPL": 65.40,
    "SHOP": 74.20, "UBER": 71.50, "DIS": 99.80, "BA": 168.90,
}

# In-memory store for fallback mode (to avoid file IO races during dev)
fallback_orders = []
fallback_positions = {}


def place_order(symbol: str, qty: int, side: str) -> dict:
    """
    Execute a trade. Uses Alpaca if configured, otherwise falls back to simulator.
    """
    symbol = symbol.upper()
    qty = float(qty) if qty else 1.0

    if USE_LIVE_ALPACA:
        try:
            alpaca_side = OrderSide.BUY if side.lower() == "buy" else OrderSide.SELL
            market_order_data = MarketOrderRequest(
                symbol=symbol,
                qty=qty,
                side=alpaca_side,
                time_in_force=TimeInForce.DAY
            )
            order = trading_client.submit_order(order_data=market_order_data)
            return {
                "executed": True,
                "order_id": str(order.id),
                "symbol": symbol,
                "qty": qty,
                "side": side,
                "status": order.status.value,
                "message": f"Alpaca Order Submitted: {side.upper()} {qty} x {symbol}",
            }
        except Exception as e:
            return {"executed": False, "error": str(e), "message": f"Alpaca API Error: {str(e)}"}
    else:
        # MOCK IMPLEMENTATION
        fill_price = MOCK_PRICES.get(symbol, 100.0)
        order_value = round(fill_price * qty, 2)
        order_id = str(uuid.uuid4())[:8].upper()

        order = {
            "order_id": order_id,
            "symbol": symbol,
            "qty": qty,
            "side": side,
            "fill_price": fill_price,
            "order_value": order_value,
            "status": "filled",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "source": "IntentShield Fallback Simulator",
        }
        fallback_orders.insert(0, order)

        if side.lower() == "buy":
            if symbol in fallback_positions:
                old = fallback_positions[symbol]
                total_qty = old["qty"] + qty
                avg_price = round((old["avg_price"] * old["qty"] + fill_price * qty) / total_qty, 2)
                fallback_positions[symbol] = {"symbol": symbol, "qty": total_qty, "avg_price": avg_price, "current_price": fill_price}
            else:
                fallback_positions[symbol] = {"symbol": symbol, "qty": qty, "avg_price": fill_price, "current_price": fill_price}
        elif side.lower() == "sell":
            if symbol in fallback_positions:
                remaining = fallback_positions[symbol]["qty"] - qty
                if remaining <= 0:
                    del fallback_positions[symbol]
                else:
                    fallback_positions[symbol]["qty"] = remaining
                    fallback_positions[symbol]["current_price"] = fill_price

        return {
            "executed": True,
            "order_id": order_id,
            "symbol": symbol,
            "qty": qty,
            "side": side,
            "fill_price": fill_price,
            "message": f"Mock Order Filled: {side.upper()} {qty} x {symbol} @ ${fill_price}",
        }


def get_positions() -> dict:
    if USE_LIVE_ALPACA:
        try:
            positions = trading_client.get_all_positions()
            result = []
            for pos in positions:
                result.append({
                    "symbol": pos.symbol,
                    "qty": float(pos.qty),
                    "avg_price": float(pos.avg_entry_price),
                    "current_price": float(pos.current_price),
                    "market_value": float(pos.market_value),
                    "unrealized_pnl": float(pos.unrealized_pl),
                    "pnl_pct": float(pos.unrealized_plpc) * 100,
                })
            return {"positions": result, "count": len(result)}
        except Exception as e:
            return {"positions": [], "count": 0, "error": str(e)}
    else:
        result = []
        for sym, pos in fallback_positions.items():
            current = MOCK_PRICES.get(sym, 100.0)
            qty = pos["qty"]
            avg = pos["avg_price"]
            pnl = round((current - avg) * qty, 2)
            pnl_pct = round((current - avg) / avg * 100, 2) if avg else 0
            result.append({
                "symbol": sym, "qty": qty, "avg_price": avg, "current_price": current,
                "market_value": round(current * qty, 2), "unrealized_pnl": pnl, "pnl_pct": pnl_pct,
            })
        return {"positions": result, "count": len(result)}


def get_orders(limit: int = 10) -> dict:
    if USE_LIVE_ALPACA:
        try:
            # We don't implement strict pagination here for brevity
            orders = trading_client.get_orders(status="all", limit=limit)
            result = [{"order_id": str(o.id), "symbol": o.symbol, "qty": float(o.qty) if o.qty else 0, "side": o.side.value, "status": o.status.value} for o in orders]
            return {"orders": result, "count": len(result)}
        except Exception as e:
            return {"orders": [], "count": 0, "error": str(e)}
    else:
        return {"orders": fallback_orders[:limit], "count": len(fallback_orders)}


def cancel_order(order_id: str) -> dict:
    if USE_LIVE_ALPACA:
        try:
            trading_client.cancel_order_by_id(order_id)
            return {"cancelled": True, "order_id": order_id}
        except Exception as e:
            return {"cancelled": False, "error": str(e)}
    else:
        for o in fallback_orders:
            if o["order_id"] == order_id:
                o["status"] = "cancelled"
                return {"cancelled": True, "order_id": order_id}
        return {"cancelled": False, "error": f"Order {order_id} not found."}
