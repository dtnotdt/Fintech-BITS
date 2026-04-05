import json
import os
import re

from tools import get_stock_price, get_company_profile, compare_companies, research_company
import paper_trading

PORTFOLIO_PATH = os.path.join(os.path.dirname(__file__), "portfolio.json")
WATCHLIST_PATH = os.path.join(os.path.dirname(__file__), "watchlist.json")


from intent_model import _extract_companies

TICKER_TO_NAME = {
    'TSLA': 'Tesla',
    'AAPL': 'Apple',
    'NVDA': 'Nvidia',
    'MSFT': 'Microsoft',
    'GOOGL': 'Google',
    'AMZN': 'Amazon',
    'META': 'Meta',
    'NFLX': 'Netflix'
}

def execute_decision(intent_data: dict, policy_result: dict, context: list = None, user_message: str = "") -> dict:
    """
    Route approved actions to the correct tool.
    Returns a decision result with tool output or block explanation.
    """
    decision = policy_result.get("decision")
    intent = policy_result.get("intent")

    needs_clarification = False
    if intent == "UNKNOWN":
        needs_clarification = True
    elif intent == "COMPARE_COMPANIES":
        companies = intent_data.get("companies", [])
        if not companies or len(companies) < 2:
            needs_clarification = True
    elif intent == "RESEARCH_COMPANY":
        companies = intent_data.get("companies", [])
        if not companies and not intent_data.get("symbol"):
            needs_clarification = True

    if decision == "CLARIFY" or needs_clarification:
        ctx_str = " ".join([str(m.get("content", "")) for m in (context or [])]).lower()
        companies_ctx = _extract_companies(ctx_str)
        # Use companies from current intent or from context
        companies = intent_data.get("companies") or companies_ctx
        
        if companies and len(companies) == 1:
            comp = companies[0]
            display_name = TICKER_TO_NAME.get(comp, comp.title())
            # When exactly one company is mentioned but intent is ambiguous, return a disambiguation menu
            return {
                "executed": True,
                "tool_used": "Static Knowledge",
                "result": f"This request is ambiguous.\nDid you mean:\n- Research {display_name}\n- Compare {display_name}\n- Add {display_name} to watchlist\n- Simulate buying {display_name}",
                "is_direct_response": True
            }
        elif companies and len(companies) > 1:
            intent_data["intent"] = "COMPARE_COMPANIES"
            intent_data["companies"] = companies
            policy_result["intent"] = "COMPARE_COMPANIES"
            policy_result["decision"] = "ALLOW"
            intent = policy_result["intent"]
            decision = policy_result["decision"]
        else:
            return {
                "executed": False,
                "tool_used": None,
                "result": None,
                "status": "clarify",
                "block_reason": "Could you clarify which companies or items you are referring to?",
            }


    if decision == "REQUIRES_CONFIRMATION":
        symbol = intent_data.get("symbol", "")
        qty = intent_data.get("quantity") or 1
        side = "buy" if intent == "BUY_STOCK" else "sell"
        return {
            "executed": False,
            "tool_used": None,
            "result": None,
            "status": "requires_confirmation",
            "pending_trade": {"symbol": symbol, "qty": qty, "side": side},
            "block_reason": f"Trade requires confirmation: {side.upper()} {qty} x {symbol}. Reply 'yes confirm' to execute.",
        }

    if decision != "ALLOW":
        return {
            "executed": False,
            "tool_used": None,
            "result": None,
            "block_reason": policy_result["reason"],
        }

    # ── Route to correct tool ──────────────────────────────────────────────────

    if intent == "READ_STOCK_INFO":
        symbol = intent_data.get("symbol") or "TSLA"
        result = get_stock_price(symbol)
        return {"executed": True, "tool_used": "Finnhub", "result": result}

    elif intent == "RESEARCH_COMPANY":
        companies = intent_data.get("companies", [])
        symbol = intent_data.get("symbol")
        
        target_companies = companies if companies else ([symbol] if symbol else [])
        target_companies = [c for c in target_companies if c]
        if not target_companies:
            target_companies = ["the company"]

        results = []
        all_images = []
        for company in target_companies:
            query = f"{company} company overview what they do products industry and recent developments"
            res = research_company(query)
            results.append(res)
            all_images.extend(res.get("images", []))
            
        primary_company = target_companies[0] if target_companies else "Unknown Company"
        
        return {
            "executed": True, 
            "tool_used": "Tavily", 
            "result": results, 
            "images": all_images[:6],
            "company_name": primary_company
        }

    elif intent == "VIEW_PORTFOLIO":
        context_text = " ".join([m.get("content", "").lower() for m in (context or [])][-3:]) + " " + user_message.lower()
        # Simple extraction: if the user provided any 4 digit number in the recent context or current message
        has_pin = re.search(r"\b\d{4}\b", context_text)
        
        if not has_pin:
            return {
                "executed": False, 
                "tool_used": None, 
                "result": None,
                "status": "clarify",
                "block_reason": "For your security, please provide your 4-digit PIN to view your portfolio."
            }

        with open(PORTFOLIO_PATH, "r") as f:
            portfolio = json.load(f)
        return {"executed": True, "tool_used": "Local Portfolio", "result": portfolio}

    elif intent == "COMPARE_COMPANIES":
        companies = intent_data.get("companies")
        result = compare_companies(companies)
        return {"executed": True, "tool_used": "Finnhub", "result": result}

    elif intent == "LIST_COMPANIES":
        companies_str = "Apple, Microsoft, Nvidia, Amazon, Alphabet, Meta, Tesla, JPMorgan Chase, Goldman Sachs, Visa, Mastercard, Berkshire Hathaway, AMD, Netflix, Salesforce"
        return {
            "executed": True,
            "tool_used": "Static Knowledge",
            "result": f"Here are 15 major companies you may want to explore:\n{companies_str}",
            "is_direct_response": True
        }

    elif intent == "ADD_TO_WATCHLIST":
        symbol = intent_data.get("symbol")
        companies = intent_data.get("companies", [])
        target = symbol or (companies[0] if companies else None)
        
        if not target:
            return {
                "executed": False,
                "tool_used": None,
                "result": None,
                "status": "clarify",
                "block_reason": "Could you clarify which company you want to add to your watchlist?",
            }
            
        with open(WATCHLIST_PATH, "r") as f:
            try:
                watchlist = json.load(f)
            except json.JSONDecodeError:
                watchlist = []
            
        if target not in watchlist:
            watchlist.append(target)
            with open(WATCHLIST_PATH, "w") as f:
                json.dump(watchlist, f)
                
        return {"executed": True, "tool_used": "Local Watchlist", "result": {"added": target, "watchlist": watchlist}}

    elif intent == "VIEW_WATCHLIST":
        with open(WATCHLIST_PATH, "r") as f:
            try:
                watchlist = json.load(f)
            except json.JSONDecodeError:
                watchlist = []
        return {"executed": True, "tool_used": "Local Watchlist", "result": {"watchlist": watchlist}}

    elif intent == "CONFIRM_TRADE":
        # Extract pending trade from conversation context
        pending = None
        for msg in reversed(context or []):
            content = msg.get("content", "")
            # Parse out symbol/qty/side from assistant's confirmation prompt
            action_match = re.search(r"Action:\s*\*\*(BUY|SELL)\*\*", content, re.IGNORECASE)
            sym_match = re.search(r"Symbol:\s*\*\*([A-Z]+)\*\*", content, re.IGNORECASE)
            qty_match = re.search(r"Quantity:\s*\*\*(\d+)\s*shares\*\*", content, re.IGNORECASE)
            
            if action_match and sym_match and qty_match:
                pending = {
                    "side": action_match.group(1).lower(),
                    "symbol": sym_match.group(1).upper(),
                    "qty": int(qty_match.group(1))
                }
                break
            
            # Legacy/fallback regex
            match = re.search(r"(BUY|SELL)\s+(\d+)\s+x\s+([A-Z]+)", content, re.IGNORECASE)
            if match:
                pending = {"side": match.group(1).lower(), "qty": int(match.group(2)), "symbol": match.group(3).upper()}
                break
        if not pending:
            # Fallback: try to extract from context text
            for msg in reversed(context or []):
                content = msg.get("content", "").lower()
                # filter out UI text elements if possible
                sym_match = re.search(r"\b([A-Z]{2,5})\b", msg.get("content", "").replace("BUY", "").replace("SELL", ""))
                side = "buy" if "buy" in content else ("sell" if "sell" in content else None)
                if sym_match and side:
                    pending = {"side": side, "qty": 1, "symbol": sym_match.group(1).upper()}
                    break
        if not pending:
            return {
                "executed": False, "tool_used": None, "result": None,
                "block_reason": "No pending trade found. Please specify what you'd like to buy or sell first."
            }

        # PIN enforcement for dangerous action
        context_text = " ".join([m.get("content", "").lower() for m in (context or [])][-3:]) + " " + user_message.lower()
        has_pin = re.search(r"\b\d{4}\b", context_text)
        if not has_pin:
             return {
                "executed": False, 
                "tool_used": None, 
                "result": None,
                "status": "clarify",
                "block_reason": "For your security, please provide your 4-digit PIN alongside your confirmation (e.g. 'yes confirm 1234')."
            }

        result = paper_trading.place_order(pending["symbol"], pending["qty"], pending["side"])
        return {"executed": True, "tool_used": "Paper Trading Engine", "result": result}

    elif intent == "GET_PAPER_POSITIONS":
        result = paper_trading.get_positions()
        return {"executed": True, "tool_used": "Paper Trading Engine", "result": result}

    elif intent == "GET_PAPER_ORDERS":
        result = paper_trading.get_orders()
        return {"executed": True, "tool_used": "Paper Trading Engine", "result": result}

    elif intent == "MULTI_STEP_ANALYSIS":
        companies = intent_data.get("companies", [])
        symbol = intent_data.get("symbol")
        targets = companies if companies else ([symbol] if symbol else [])
        if not targets:
            return {"executed": False, "tool_used": None, "result": None,
                    "block_reason": "Please specify which stocks to analyze."}
        steps = []
        for sym in targets[:2]:
            price_data = get_stock_price(sym)
            steps.append({"step": "price_check", "symbol": sym, "data": price_data})
        return {"executed": True, "tool_used": "Multi-Step Reasoning", "result": {"steps": steps, "targets": targets}}

    return {
        "executed": False,
        "tool_used": None,
        "result": None,
        "block_reason": "Unhandled intent.",
    }
