from intent_model import extract_intent
from policy_engine import check_policy
from decision_engine import execute_decision
from response_generator import generate_response
from audit_logger import log_decision


class OpenClawAgent:
    """
    OpenClaw AI Agent Runtime — IntentShield Financial Copilot.

    This layer acts as the autonomous agent execution framework (OpenClaw-compatible).
    All reasoning, policy enforcement, and tool execution is delegated strictly through
    IntentShield's safety pipeline. No action executes without passing policy validation.

    Execution flow:
        User Request → OpenClaw Agent → Intent Extraction → Policy Check
        → Decision Engine → ALLOW / BLOCK / REQUIRES_CONFIRMATION → Tool Execution → Audit Log
    """

    AGENT_RUNTIME = "OPENCLAW_v1.0"
    MULTI_STEP_INTENTS = {"MULTI_STEP_ANALYSIS", "COMPARE_COMPANIES", "RESEARCH_COMPANY"}

    def __init__(self, agent_name="IntentShield_Financial_Copilot"):
        self.agent_name = agent_name

    def execute(self, user_message: str, context: list = None) -> dict:
        """
        Main agent entry point.
        Runs the full IntentShield safety pipeline for a given user message.
        Multi-step intents are handled via an extended reasoning trace.
        """
        if context is None:
            context = []

        print(f"[{self.AGENT_RUNTIME}] Agent '{self.agent_name}' processing: {user_message[:60]}...")

        # Step 1: Intent Extraction
        intent_data = extract_intent(user_message)
        intent = intent_data.get("intent", "UNKNOWN")

        # Step 2: Policy Enforcement (deterministic — no LLM involvement)
        policy_result = check_policy(intent_data)

        # Step 3: Decision Engine — route to tool or block
        # Multi-step intents get enriched context injected
        if intent in self.MULTI_STEP_INTENTS:
            print(f"[{self.AGENT_RUNTIME}] Multi-step reasoning activated for intent: {intent}")
            decision_result = execute_decision(intent_data, policy_result, context, user_message)
            decision_result["reasoning_trace"] = self._build_reasoning_trace(intent_data, decision_result)
        else:
            decision_result = execute_decision(intent_data, policy_result, context, user_message)

        # Step 4: Generate natural language response
        assistant_reply = generate_response(user_message, intent_data, policy_result, decision_result)

        # Step 5: Audit Log
        audit_entry = log_decision(user_message, intent_data, policy_result, decision_result)

        print(f"[{self.AGENT_RUNTIME}] Decision: {policy_result.get('decision')} | Tool: {decision_result.get('tool_used')}")

        return {
            "assistant_reply": assistant_reply,
            "intent_data": intent_data,
            "policy_result": policy_result,
            "decision_result": decision_result,
            "audit_log_entry": audit_entry,
            "agent_runtime": self.AGENT_RUNTIME,
        }

    def _build_reasoning_trace(self, intent_data: dict, decision_result: dict) -> list:
        """
        Build a human-readable trace of the agent's reasoning steps.
        Used for multi-step intents and debugging.
        """
        steps = []
        intent = intent_data.get("intent")
        companies = intent_data.get("companies", [])
        symbol = intent_data.get("symbol")

        steps.append(f"Intent classified: {intent}")
        if companies:
            steps.append(f"Targets identified: {', '.join(companies)}")
        elif symbol:
            steps.append(f"Symbol identified: {symbol}")

        tool = decision_result.get("tool_used")
        if tool:
            steps.append(f"Tool invoked: {tool}")

        raw_steps = decision_result.get("result", {})
        if isinstance(raw_steps, dict) and "steps" in raw_steps:
            for s in raw_steps["steps"]:
                sym = s.get("symbol", "")
                price = s.get("data", {}).get("current_price", "?")
                chg = s.get("data", {}).get("change_pct", 0)
                steps.append(f"Price checked — {sym}: ${price} ({chg:+.2f}% today)")

        steps.append("Policy validated. Response generated.")
        return steps
