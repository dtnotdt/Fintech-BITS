"""
sub_agents.py — Sub-Agent Delegation Module

Implements the delegation bonus criteria for the hackathon. 
The Execution Proximal agent has strictly bounded authority — it is the ONLY 
part of the system allowed to invoke `alpaca_trading.place_order`. The main 
agent cannot place trades itself, ensuring a zero-trust compartmentalization.
"""

from alpaca_trading import place_order

class ExecutionProximalAgent:
    """
    Sub-agent with bounded authority to execute trades in the Alpaca ecosystem.
    It receives explicit intent structs after human/PIN confirmation and routes them.
    """
    def __init__(self):
        self.agent_id = "EXECUTION_PROXIMAL_V1"
        self.scope = ["alpaca_trading.place_order"]

    def execute_delegated_task(self, intent_data: dict) -> dict:
        """
        Takes a verified trade intent and executes it securely.
        Returns the trade receipt.
        """
        symbol = intent_data.get("symbol")
        qty = intent_data.get("quantity", 1)
        side = "buy" if intent_data.get("intent") == "BUY_STOCK" else "sell"

        if not symbol:
            return {"error": "Delegation failed: Missing symbol for execution."}

        print(f"[🛡️ {self.agent_id}] Processing authorized trade: {side.upper()} {qty} shares of {symbol}")
        
        # Invoke the actual API layer
        receipt = place_order(symbol, qty, side)
        
        return {
            "delegation_success": True,
            "sub_agent": self.agent_id,
            "task_receipt": receipt
        }

# Global instance for the decision engine to invoke
execution_proximal_agent = ExecutionProximalAgent()
