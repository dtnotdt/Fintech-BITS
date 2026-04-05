import json
import os

POLICIES_PATH = os.path.join(os.path.dirname(__file__), "policies.json")


def load_policies() -> dict:
    with open(POLICIES_PATH, "r") as f:
        return json.load(f)["policies"]


def check_policy(intent_data: dict) -> dict:
    """
    Check the extracted intent against policy rules.
    Returns a policy result dict with decision, risk_level, and reason.
    """
    policies = load_policies()
    intent = intent_data.get("intent", "UNKNOWN")
    confidence = intent_data.get("confidence", 0.0)

    # Low confidence → treat as UNKNOWN
    if confidence < 0.6:
        intent = "UNKNOWN"

    policy = policies.get(intent, policies["UNKNOWN"])

    return {
        "intent": intent,
        "decision": policy["decision"],
        "risk_level": policy["risk_level"],
        "reason": policy["reason"],
        "original_risk_level": intent_data.get("risk_level", policy["risk_level"]),
    }
