import json
import os
from datetime import datetime, timezone

LOGS_PATH = os.path.join(os.path.dirname(__file__), "logs.json")


def _load_logs() -> list:
    if not os.path.exists(LOGS_PATH):
        return []
    with open(LOGS_PATH, "r") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []


def _save_logs(logs: list) -> None:
    with open(LOGS_PATH, "w") as f:
        json.dump(logs, f, indent=2)


def log_decision(
    user_input: str,
    intent_data: dict,
    policy_result: dict,
    decision_result: dict,
) -> dict:
    """Create and persist an audit log entry. Returns the log entry."""
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "user_input": user_input,
        "intent": policy_result.get("intent", "UNKNOWN"),
        "risk_level": policy_result.get("risk_level", "CRITICAL"),
        "policy_status": policy_result.get("decision", "BLOCK"),
        "decision": policy_result.get("decision", "BLOCK"),
        "reason": policy_result.get("reason", ""),
        "tool_used": decision_result.get("tool_used"),
        "executed": decision_result.get("executed", False),
        "confidence": intent_data.get("confidence", 0.0),
        "symbol": intent_data.get("symbol"),
        "companies": intent_data.get("companies", []),
    }

    logs = _load_logs()
    logs.insert(0, entry)  # newest first
    logs = logs[:200]  # cap log size
    _save_logs(logs)

    return entry


def get_all_logs() -> list:
    return _load_logs()
