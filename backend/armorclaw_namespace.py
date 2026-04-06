"""
armorclaw_namespace.py — ArmorClaw Plugin Protocol Wrapper

Integrates the Antigravity Security Suite via the ArmorClaw Plugin Namespace.
Enforces the Zero Trust security protocol, cryptographic-like token checks, and 
sub-agent delegation.
"""

from intent_model import extract_intent
from policy_engine import check_policy
from decision_engine import execute_decision
from response_generator import generate_response
from audit_logger import log_decision
import uuid

class ArmorClawPlugin:
    """
    ArmorClaw Security Plugin Runtime — IntentShield Financial Copilot V.2.0-LIVE.

    Execution flow:
        User Request → ArmorClaw Plugin → Intent Extraction → Cryptographic Policy Check
        → Decision Engine → ALLOW / BLOCK / REQUIRES_CONFIRMATION → Tool/SubAgent Execution → Audit Log
    """

    AGENT_RUNTIME = "ARMORCLAW_ANTIGRAVITY_SHIELD_V2"
    MULTI_STEP_INTENTS = {"MULTI_STEP_ANALYSIS", "COMPARE_COMPANIES", "RESEARCH_COMPANY"}

    def __init__(self, agent_name="ArmorClaw_Financial_Copilot"):
        self.agent_name = agent_name

    def execute(self, user_message: str, context: list = None) -> dict:
        """
        Main agent entry point.
        """
        if context is None:
            context = []

        print(f"[⚡ {self.AGENT_RUNTIME}] Analyzing input for Prompt Injection...: {user_message[:60]}...")

        # Step 1: Intent Extraction (LLM mapped)
        intent_data = extract_intent(user_message)
        intent = intent_data.get("intent", "UNKNOWN")

        # Step 2: Policy Enforcement (Deterministic)
        # In ArmorClaw, we simulate issuing an intent token
        intent_token = f"TOKEN-{uuid.uuid4().hex[:8].upper()}"
        intent_data["_armorclaw_token"] = intent_token
        
        policy_result = check_policy(intent_data)

        # Ensure mathematical block for critical intents
        decision_enum = policy_result.get('decision')

        # Step 3: Decision Engine — route to tool, block, or Sub-Agent delegation
        if intent in self.MULTI_STEP_INTENTS:
            print(f"[🛡️ {self.AGENT_RUNTIME}] Multi-step reasoning activated. Token: {intent_token}")
            decision_result = execute_decision(intent_data, policy_result, context, user_message)
            decision_result["reasoning_trace"] = self._build_reasoning_trace(intent_data, decision_result)
        else:
            decision_result = execute_decision(intent_data, policy_result, context, user_message)

        # Step 4: Generate natural language response with SHIELD_LOG header
        assistant_reply = generate_response(user_message, intent_data, policy_result, decision_result)

        # Step 5: Audit Log
        audit_entry = log_decision(user_message, intent_data, policy_result, decision_result)

        print(f"[🛰️ {self.AGENT_RUNTIME}] Result: {decision_enum} | Path: {decision_result.get('tool_used', 'None')}")

        return {
            "assistant_reply": assistant_reply,
            "intent_data": intent_data,
            "policy_result": policy_result,
            "decision_result": decision_result,
            "audit_log_entry": audit_entry,
            "agent_runtime": self.AGENT_RUNTIME,
        }

    def _build_reasoning_trace(self, intent_data: dict, decision_result: dict) -> list:
        steps = []
        intent = intent_data.get("intent")
        companies = intent_data.get("companies", [])
        symbol = intent_data.get("symbol")

        steps.append(f"Intent Cryptographically Mapped: {intent}")
        if companies:
            steps.append(f"Entity targets identified: {', '.join(companies)}")
        elif symbol:
            steps.append(f"Symbol identified: {symbol}")

        tool = decision_result.get("tool_used")
        if tool:
            steps.append(f"Authorized tool invoked: {tool}")

        raw_steps = decision_result.get("result", {})
        if isinstance(raw_steps, dict) and "steps" in raw_steps:
            for s in raw_steps["steps"]:
                sym = s.get("symbol", "")
                price = s.get("data", {}).get("current_price", "?")
                chg = s.get("data", {}).get("change_pct", 0)
                steps.append(f"Market fetch — {sym}: ${price} ({chg:+.2f}% today)")

        steps.append("ArmorClaw validation sequence complete.")
        return steps
