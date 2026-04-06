import os
import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def _generate_core_response(
    user_message: str,
    intent_data: dict,
    policy_result: dict,
    decision_result: dict,
) -> str:
    """Generate a natural language assistant response using OpenAI or fallback."""
    api_key = os.getenv("OPENAI_API_KEY", "")
    if not api_key or api_key == "YOUR_OPENAI_KEY":
        return _fallback_response(intent_data, policy_result, decision_result)

    if decision_result.get("is_direct_response"):
        return decision_result.get("result", "")

    decision = policy_result["decision"]
    intent = policy_result["intent"]

    if decision == "CLARIFY" or decision_result.get("status") == "clarify":
        clarify_prompt = f"""
You are IntentShield, a helpful financial AI assistant.
The user asked an ambiguous question: "{user_message}"
Reason: {policy_result.get('reason', 'Need more context')}

Politely ask the user to clarify their request. For example, "Which companies would you like me to look up?"
Keep your response concise (1-2 sentences).
"""
        try:
            resp = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": clarify_prompt}],
                temperature=0.7,
                max_tokens=150,
            )
            return resp.choices[0].message.content
        except Exception:
            return _fallback_response(intent_data, policy_result, decision_result)

    if decision_result.get("status") == "requires_confirmation":
        return _fallback_response(intent_data, policy_result, decision_result)

    elif decision != "ALLOW":
        block_prompt = f"""
You are IntentShield, a safe financial AI assistant.
The user asked: "{user_message}"
This action was BLOCKED by the policy engine.
Intent detected: {intent}
Reason: {policy_result['reason']}
Risk level: {policy_result['risk_level']}

Explain politely why this was blocked and suggest what they CAN do instead.
Keep your response concise and helpful (2-3 sentences).
"""
        try:
            resp = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": block_prompt}],
                temperature=0.7,
                max_tokens=200,
            )
            return resp.choices[0].message.content
        except Exception:
            return _fallback_response(intent_data, policy_result, decision_result)

    tool_result = decision_result.get("result", {})
    tool_used = decision_result.get("tool_used", "")
    tool_json = json.dumps(tool_result, indent=2) if tool_result else "{}"

    summary_prompt = f"""You're IntentShield, a secure financial AI. Respond concisely. Use markdown.
User: "{user_message}"
Data: {tool_json[:1000]}
"""
    try:
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": summary_prompt}],
            temperature=0.3,
            max_tokens=200,
        )
        return resp.choices[0].message.content
    except Exception as e:
        print(f"[ResponseGen] OpenAI error: {e}")
        return _fallback_response(intent_data, policy_result, decision_result)


def _fallback_response(intent_data: dict, policy_result: dict, decision_result: dict) -> str:
    if decision_result.get("is_direct_response"):
        return decision_result.get("result", "")

    intent = policy_result["intent"]
    decision = policy_result["decision"]

    if decision == "CLARIFY" or decision_result.get("status") == "clarify":
        return f"🤔 **Clarification Needed**: {decision_result.get('block_reason', 'Could you clarify which companies you are referring to?')}"

    elif decision_result.get("status") == "requires_confirmation":
        pending = decision_result.get("pending_trade", {})
        sym = pending.get("symbol", "?")
        qty = pending.get("qty", 1)
        side = pending.get("side", "buy").upper()
        return (
            f"⚠️ **Trade Confirmation Required**\n\n"
            f"You are about to place a **paper trade** order:\n"
            f"- Action: **{side}**\n"
            f"- Symbol: **{sym}**\n"
            f"- Quantity: **{qty} shares**\n\n"
            f"🔒 This will execute in the **simulated paper trading environment** only.\n"
            f"Reply **'yes confirm'** along with your **4-digit PIN** to execute, or ignore to cancel."
        )

    elif decision != "ALLOW":
        reason = policy_result.get("reason", "This action is not permitted.")
        return f"⚠️ **Action Blocked**: {reason} (Intent: {intent}, Risk: {policy_result.get('risk_level', 'UNKNOWN')})"

    result = decision_result.get("result", {})
    tool = decision_result.get("tool_used", "")

    if intent == "READ_STOCK_INFO":
        sym = result.get("symbol", "")
        price = result.get("current_price", "N/A")
        chg = result.get("change", 0)
        chg_pct = result.get("change_pct", 0)
        arrow = "▲" if chg >= 0 else "▼"
        return f"📈 **{sym}** is trading at **${price}** {arrow} {abs(chg_pct):.2f}% today. (Source: {tool})"

    elif intent == "VIEW_PORTFOLIO":
        owner = result.get("owner", "Dhitee")
        holdings = result.get("holdings", [])
        total = result.get("estimated_total_value", 0)
        lines = [f"💼 **{owner}'s Portfolio** — Estimated Total: **${total:,}**\n"]
        for h in holdings:
            lines.append(f"- **{h['stock']}** ({h['symbol']}): {h['shares']} shares")
        lines.append(f"\nCash Balance: **${result.get('cash_balance', 0):,}**")
        return "\n".join(lines)

    elif intent == "COMPARE_COMPANIES":
        if isinstance(result, list):
            lines = ["📊 **Company Comparison**\n"]
            for r in result:
                lines.append(f"**{r.get('symbol', '')}**: ${r.get('current_price', 'N/A')} | Change: {r.get('change_pct', 0):.2f}%")
            return "\n".join(lines)

    elif intent == "RESEARCH_COMPANY":
        if not isinstance(result, list):
            result = [result]
            
        output = []
        for res in result:
            company = res.get("query", "").split()[0].title()
            output.append(f"🔍 **Research Report: {company}**")
            
            if "error" in res or not res.get("results"):
                output.append(f"*(Live research could not be fetched: {res.get('error', 'No results')})*")
                output.append("\n**Overview:**\nThis is a generic overview. Because live fetching failed, no real-time data is available.")
                output.append("\n**Core Business:**\nThe primary revenue drivers are typically flagship product lines, enterprise services, and expanding market footprints.")
                output.append("\n**Products / Services:**\nIndustry-standard hardware, software, and consumer-facing solutions.")
                output.append("\n**Recent Context:**\nCheck recent news for up-to-date industry shifts and strategic initiatives.")
                output.append("\n**Investor Summary:**\nMonitor earnings reports and macroeconomic indicators for forward guidance.")
                output.append("---")
                continue
                
            snippets = res.get("results", [])
            output.append(f"**Overview:**\n{snippets[0]['content'] if len(snippets) > 0 else 'N/A'}")
            output.append(f"\n**Core Business:**\n{snippets[1]['content'] if len(snippets) > 1 else 'N/A'}")
            output.append(f"\n**Products / Services:**\n{snippets[2]['content'] if len(snippets) > 2 else 'N/A'}")
            output.append(f"\n**Recent Context:**\n{snippets[3]['content'] if len(snippets) > 3 else 'N/A'}")
            if len(snippets) > 0:
                output.append(f"\n**Investor Summary:**\nSource: {snippets[0]['title']} ({snippets[0]['url']})")
            
            output.append("---")
            
        return "\n\n".join(output) if output else "No research results found."

    elif intent == "ADD_TO_WATCHLIST":
        added = result.get("added", "")
        return f"✅ **{added}** has been successfully added to your watchlist."

    elif intent == "VIEW_WATCHLIST":
        watchlist = result.get("watchlist", [])
        if not watchlist:
            return "Your watchlist is currently empty. Try adding a company!"
        lines = ["📋 **Your Watchlist**\n"]
        for sym in watchlist:
            lines.append(f"- [{sym}](https://www.google.com/search?q={sym}+stock)")
        return "\n".join(lines)

    elif decision_result.get("status") == "requires_confirmation":
        pending = decision_result.get("pending_trade", {})
        sym = pending.get("symbol", "?")
        qty = pending.get("qty", 1)
        side = pending.get("side", "buy").upper()
        return (
            f"⚠️ **Trade Confirmation Required**\n\n"
            f"You are about to place a **paper trade** order:\n"
            f"- Action: **{side}**\n"
            f"- Symbol: **{sym}**\n"
            f"- Quantity: **{qty} shares**\n\n"
            f"🔒 This will execute in the **simulated paper trading environment** only.\n"
            f"Reply **'yes confirm'** to execute, or ignore to cancel."
        )

    elif intent == "CONFIRM_TRADE":
        order_result = result.get("task_receipt", {})
        oid = order_result.get("order_id", "?")
        sym = order_result.get("symbol", "?")
        qty = order_result.get("qty", "?")
        side = order_result.get("side", "?").upper()
        price = order_result.get("fill_price", "?")
        value = order_result.get("order_value", "?")
        return (
            f"✅ **Paper Trade Executed** (Order `{oid}`)\n\n"
            f"- **{side}** {qty} shares of **{sym}**\n"
            f"- Fill Price: **${price}**\n"
            f"- Total Value: **${value}**\n"
            f"- Status: **Filled** (simulated)\n\n"
            f"View your positions by saying *'show my paper positions'*."
        )

    elif intent == "GET_PAPER_POSITIONS":
        positions = result.get("positions", [])
        count = result.get("count", 0)
        if count == 0:
            return "📊 Your paper trading portfolio is currently empty. Try buying some shares first!"
        lines = [f"📊 **Paper Trading Positions** ({count} open)\n"]
        for p in positions:
            pnl_arrow = "▲" if p["unrealized_pnl"] >= 0 else "▼"
            lines.append(
                f"- **{p['symbol']}**: {p['qty']} shares @ avg ${p['avg_price']} | "
                f"Now ${p['current_price']} | PnL: {pnl_arrow} ${abs(p['unrealized_pnl'])} ({p['pnl_pct']:.2f}%)"
            )
        return "\n".join(lines)

    elif intent == "GET_PAPER_ORDERS":
        orders = result.get("orders", [])
        if not orders:
            return "📋 No paper trade orders found yet."
        lines = ["📋 **Recent Paper Orders**\n"]
        for o in orders[:5]:
            lines.append(f"- `{o['order_id']}` | {o['side'].upper()} {o['qty']}x **{o['symbol']}** @ ${o['fill_price']} | {o['status'].upper()}")
        return "\n".join(lines)

    elif intent == "MULTI_STEP_ANALYSIS":
        steps = result.get("steps", [])
        targets = result.get("targets", [])
        if not steps:
            return "Could not complete multi-step analysis."
        lines = [f"🧠 **Multi-Step Analysis: {', '.join(targets)}**\n"]
        for step in steps:
            sym = step["symbol"]
            data = step["data"]
            price = data.get("current_price", "N/A")
            chg_pct = data.get("change_pct", 0)
            chg = data.get("change", 0)
            arrow = "▲" if chg >= 0 else "▼"
            sentiment = "showing strength" if chg_pct > 0.5 else ("under pressure" if chg_pct < -0.5 else "relatively flat")
            lines.append(f"**Step 1 — Price Check {sym}:** ${price} {arrow} {abs(chg_pct):.2f}% today — *{sentiment}*")
        if len(steps) > 1:
            best = max(steps, key=lambda s: s["data"].get("change_pct", 0))
            lines.append(f"\n**Step 2 — Reasoning:** Based on today's performance, **{best['symbol']}** appears stronger with {best['data'].get('change_pct', 0):.2f}% change.")
            lines.append("\n**Step 3 — Recommendation:** Monitor both, but favour the stronger performer for near-term sentiment.")
        else:
            d = steps[0]["data"]
            chg = d.get("change_pct", 0)
            if chg > 0:
                lines.append(f"\n**Reasoning:** {targets[0]} is up today — momentum looks positive. Consider watching closely.")
            else:
                lines.append(f"\n**Reasoning:** {targets[0]} is down today — caution advised. Avoid impulsive action.")
        return "\n".join(lines)

    return f"✅ Action completed via {tool}."

def generate_response(
    user_message: str,
    intent_data: dict,
    policy_result: dict,
    decision_result: dict,
) -> str:
    inner_reply = _generate_core_response(user_message, intent_data, policy_result, decision_result)
    
    intent = policy_result.get("intent", "UNKNOWN")
    risk_score = policy_result.get("risk_level", "UNKNOWN")
    delegation_path = decision_result.get("tool_used", "None") or "None"
    if "EXECUTION_PROXIMAL" in delegation_path:
        delegation_path = "Internal -> ArmorClaw_SubAgent"
    decision = policy_result.get("decision", "UNKNOWN")
    passed_rejected = "PASSED" if decision in ["ALLOW", "REQUIRES_CONFIRMATION"] else "REJECTED"
        
    banner = (
        "┌──────────────────────────────────────────────────────────┐\n"
        "│ ⚡ ARMORCLAW ACTIVE | 🛰️ LIVE ALPACA FEED | 🛡️ ZERO TRUST   │\n"
        "└──────────────────────────────────────────────────────────┘\n\n"
        "**[SHIELD_LOG]**\n"
        f"- **Detected Intent:** [{intent}]\n"
        f"- **Risk Score:** [{risk_score}]\n"
        f"- **Delegation Path:** [{delegation_path}]\n"
        f"- **Policy Check:** [{passed_rejected}]\n\n"
    )
    
    return banner + inner_reply
