import os
import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

INTENT_PROMPT = """You are an intent extractor for a financial assistant. Reply ONLY with valid JSON:
{
  "intent": "<READ_STOCK_INFO, RESEARCH_COMPANY, VIEW_PORTFOLIO, COMPARE_COMPANIES, BUY_STOCK, SELL_STOCK, SEND_DATA_EXTERNALLY, LIST_COMPANIES, ADD_TO_WATCHLIST, VIEW_WATCHLIST, UNKNOWN>",
  "symbol": "<ticker|null>",
  "quantity": <int|null>,
  "companies": ["<name>"] or [],
  "target_url": "<url|null>",
  "action_type": "<READ, RESEARCH, TRANSACTION, DATA_TRANSFER, UNKNOWN>",
  "risk_level": "<LOW, MEDIUM, HIGH, CRITICAL>",
  "confidence": <0.0-1.0>
}
Rules:
- buy/purchase/order = BUY_STOCK, HIGH
- sell/dump/offload = SELL_STOCK, HIGH
- price/stock price/quote/how much = READ_STOCK_INFO, LOW
- list companies/top stocks = LIST_COMPANIES, LOW
- compare/vs/versus = COMPARE_COMPANIES, MEDIUM
- portfolio/holdings/my stocks = VIEW_PORTFOLIO, MEDIUM
- send/export/upload data = SEND_DATA_EXTERNALLY, CRITICAL
- "add [ANY COMPANY] to watchlist" or "track [COMPANY]" or "watch [COMPANY]" = ADD_TO_WATCHLIST, LOW. Extract company into `companies`.
- show/view watchlist = VIEW_WATCHLIST, LOW
- ambiguous/other = UNKNOWN, CRITICAL
Always extract company or stock names into `companies` array."""


def extract_intent(user_message: str) -> dict:
    """Extract structured intent from user message using OpenAI."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key or api_key == "YOUR_OPENAI_KEY":
        return _rule_based_extraction(user_message)

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": INTENT_PROMPT},
                {"role": "user", "content": user_message},
            ],
            temperature=0.1,
            response_format={"type": "json_object"},
        )
        raw = response.choices[0].message.content
        result = json.loads(raw)
        # Safety net: if OpenAI returns UNKNOWN, try rule-based as override
        if result.get("intent") == "UNKNOWN":
            rule_result = _rule_based_extraction(user_message)
            if rule_result.get("intent") != "UNKNOWN":
                print(f"[IntentModel] Overriding OpenAI UNKNOWN with rule-based: {rule_result['intent']}")
                return rule_result
        return result
    except Exception as e:
        print(f"[IntentModel] OpenAI error: {e}")
        return _rule_based_extraction(user_message)


import re

def _rule_based_extraction(message: str) -> dict:
    """Simple keyword-based fallback intent extractor."""
    msg = message.lower()

    if any(w in msg for w in ["list the companies", "top stocks", "best finance", "banking companies", "show banking", "major companies"]):
        return _make_intent("LIST_COMPANIES", None, "READ", "LOW", 0.90)

    if any(w in msg for w in ["show my watchlist", "view watchlist", "show watchlist", "my watchlist", "what is on my watchlist"]):
        return _make_intent("VIEW_WATCHLIST", None, "READ", "LOW", 0.95)

    # Confirmation flow
    if any(w in msg for w in ["yes confirm", "yess confirm", "confirm trade", "yes proceed", "execute it", "go ahead", "yes, execute", "yes execute", "proceed with", "yes please", "confirm it"]):
        return _make_intent("CONFIRM_TRADE", None, "TRANSACTION", "HIGH", 0.95)

    # Paper trading positions/orders
    if any(w in msg for w in ["my paper positions", "paper positions", "paper portfolio", "my simulated", "paper trades"]):
        return _make_intent("GET_PAPER_POSITIONS", None, "READ", "LOW", 0.95)

    if any(w in msg for w in ["paper orders", "my orders", "order history", "recent orders"]):
        return _make_intent("GET_PAPER_ORDERS", None, "READ", "LOW", 0.95)

    # Multi-step analysis
    multi_step_keywords = ["and then", "then tell me", "and decide", "then decide", "and suggest", "then suggest",
                           "check and", "analyze and", "and determine", "looks stronger", "should i buy",
                           "worth buying", "should i watch", "if it is down"]
    if any(w in msg for w in multi_step_keywords):
        companies = _extract_companies(msg)
        symbol = _extract_symbol(msg)
        return _make_intent("MULTI_STEP_ANALYSIS", symbol, "RESEARCH", "LOW", 0.85, companies=companies)

    # Watchlist: "add X to [my/the] watchlist" — handles any company name
    watchlist_add_match = re.search(r"add\s+(.+?)\s+to(?:\s+(?:my|the))?\s+watchlist", msg, re.IGNORECASE)
    if watchlist_add_match or any(w in msg for w in ["add to watchlist", "add to my watchlist"]):
        raw_company = watchlist_add_match.group(1).strip() if watchlist_add_match else ""
        symbol = _extract_symbol(msg)
        companies = _extract_companies(msg)
        # If we got a company name from regex but not from known list, add it as-is
        if raw_company and not companies:
            companies = [raw_company.upper()]
        if raw_company and not symbol:
            # Try to use raw name as symbol too
            symbol = raw_company.upper().split()[0]  # first word uppercased
        return _make_intent("ADD_TO_WATCHLIST", symbol, "READ", "LOW", 0.92, companies=companies)

    if any(w in msg for w in ["send", "upload", "export", "transfer", "webhook", "api"]):
        return _make_intent("SEND_DATA_EXTERNALLY", None, "DATA_TRANSFER", "CRITICAL", 0.85)

    if any(w in msg for w in ["buy", "purchase", "order", "acquire"]):
        symbol = _extract_symbol(msg)
        q_match = re.search(r"(?:buy|purchase|order)\s+(\d+)", msg, re.IGNORECASE) or re.search(r"(\d+)\s+(?:shares|units|stocks)", msg, re.IGNORECASE)
        qty = int(q_match.group(1)) if q_match else None
        return _make_intent("BUY_STOCK", symbol, "TRANSACTION", "HIGH", 0.88, quantity=qty)

    if any(w in msg for w in ["sell", "dump", "offload", "liquidate"]):
        symbol = _extract_symbol(msg)
        q_match = re.search(r"(?:sell|dump|offload)\s+(\d+)", msg, re.IGNORECASE) or re.search(r"(\d+)\s+(?:shares|units|stocks)", msg, re.IGNORECASE)
        qty = int(q_match.group(1)) if q_match else None
        return _make_intent("SELL_STOCK", symbol, "TRANSACTION", "HIGH", 0.88, quantity=qty)

    if any(w in msg for w in ["portfolio", "holdings", "my stocks", "my investments", "pin is", "here is my pin", "my pin"]) or re.search(r"\b\d{4}\b", msg):
        return _make_intent("VIEW_PORTFOLIO", None, "READ", "MEDIUM", 0.90)

    if any(w in msg for w in ["compare", "vs", "versus", "against"]):
        companies = _extract_companies(msg)
        return _make_intent("COMPARE_COMPANIES", None, "READ", "MEDIUM", 0.80, companies=companies)

    if any(w in msg for w in ["research", "news", "latest", "recent", "what is happening", "summarize", "explain", "tell me about", "what does", "company profile", "details about", "info on", "overview of", "background on"]):
        extracted = _extract_company_fallback(msg)
        symbol = _extract_symbol(msg)
        return _make_intent("RESEARCH_COMPANY", symbol, "RESEARCH", "LOW", 0.82, companies=extracted)

    if any(w in msg for w in ["price", "stock", "ticker", "quote", "value", "worth"]):
        symbol = _extract_symbol(msg)
        return _make_intent("READ_STOCK_INFO", symbol, "READ", "LOW", 0.85)

    companies = _extract_companies(msg)
    return _make_intent("UNKNOWN", None, "UNKNOWN", "LOW", 0.30, companies=companies)


def _make_intent(intent, symbol, action_type, risk_level, confidence, companies=None, quantity=None):
    return {
        "intent": intent,
        "symbol": symbol,
        "quantity": quantity,
        "companies": companies or [],
        "target_url": None,
        "action_type": action_type,
        "risk_level": risk_level,
        "confidence": confidence,
    }


KNOWN_SYMBOLS = {
    "tesla": "TSLA", "apple": "AAPL", "nvidia": "NVDA", "microsoft": "MSFT",
    "google": "GOOGL", "alphabet": "GOOGL", "amazon": "AMZN", "meta": "META",
    "netflix": "NFLX", "salesforce": "CRM", "crm": "CRM",
    "jpmorgan": "JPM", "jp morgan": "JPM", "morgan stanley": "MS",
    "goldman": "GS", "goldman sachs": "GS",
    "visa": "V", "mastercard": "MA", "paypal": "PYPL",
    "shopify": "SHOP", "uber": "UBER", "lyft": "LYFT",
    "disney": "DIS", "boeing": "BA", "airbnb": "ABNB",
    "spotify": "SPOT", "palantir": "PLTR", "amd": "AMD",
    "intel": "INTC", "oracle": "ORCL", "ibm": "IBM",
    "tsla": "TSLA", "aapl": "AAPL", "nvda": "NVDA",
    "msft": "MSFT", "googl": "GOOGL", "amzn": "AMZN",
}

COMPANY_NAMES = [
    "tesla", "apple", "nvidia", "microsoft", "google", "alphabet", "amazon",
    "meta", "netflix", "salesforce", "jpmorgan", "goldman", "visa", "mastercard",
    "paypal", "shopify", "uber", "lyft", "disney", "boeing", "airbnb",
    "spotify", "palantir", "amd", "intel", "oracle", "ibm",
]


def _extract_symbol(msg: str) -> str | None:
    for name, sym in KNOWN_SYMBOLS.items():
        if name in msg:
            return sym
    return None


RESEARCH_PHRASES = [
    r"tell me about\s+(.+)",
    r"research\s+(.+)",
    r"summarize\s+(.+)",
    r"explain\s+(.+)",
    r"what does\s+(.+?)\s+do",
    r"company profile for\s+(.+)",
    r"company profile of\s+(.+)",
    r"details about\s+(.+)",
    r"info on\s+(.+)",
]

def _extract_company_fallback(msg: str) -> list:
    for phrase in RESEARCH_PHRASES:
        match = re.search(phrase, msg, re.IGNORECASE)
        if match:
            # Clean up the extracted string
            return [match.group(1).strip(" ?.!").title()]
            
    # Try hardcoded if regex fails
    found = []
    for name in COMPANY_NAMES:
        if name in msg:
            found.append(KNOWN_SYMBOLS.get(name, name.upper()))
    return found[:2]

def _extract_companies(msg: str) -> list:
    found = []
    for name in COMPANY_NAMES:
        if name in msg:
            found.append(KNOWN_SYMBOLS.get(name, name.upper()))
    return found[:2]

