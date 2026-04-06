import os
import json
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

from intent_model import extract_intent
from policy_engine import check_policy
from decision_engine import execute_decision
from response_generator import generate_response
from audit_logger import log_decision, get_all_logs
from armorclaw_namespace import ArmorClawPlugin

load_dotenv()

app = FastAPI(title="IntentShield API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    message: str
    context: list = []


@app.get("/")
def root():
    return {"status": "ok", "service": "IntentShield API"}


@app.post("/chat")
async def chat(req: ChatRequest):
    user_message = req.message.strip()
    if not user_message:
        return {"error": "Empty message"}

    # ── ArmorClaw Plugin Runtime ──────────────────────────────────────────────
    agent = ArmorClawPlugin()
    agent_output = agent.execute(user_message, req.context)
    
    intent_data = agent_output["intent_data"]
    policy_result = agent_output["policy_result"]
    decision_result = agent_output["decision_result"]
    assistant_reply = agent_output["assistant_reply"]
    audit_entry = agent_output["audit_log_entry"]

    response = {
        "assistant_reply": assistant_reply,
        "intent_data": intent_data,
        "policy_result": policy_result,
        "decision_result": {
            "executed": decision_result.get("executed", False),
            "tool_used": decision_result.get("tool_used"),
            "block_reason": decision_result.get("block_reason"),
            "result": decision_result.get("result"),
        },
        "audit_log_entry": audit_entry,
    }
    
    if intent_data.get("intent") == "RESEARCH_COMPANY" and policy_result.get("decision") == "ALLOW":
        response["company_name"] = decision_result.get("company_name", "Unknown Company")
        response["research_summary"] = assistant_reply
        response["image_urls"] = decision_result.get("images", [])

    return response


@app.get("/logs")
def get_logs():
    return get_all_logs()


@app.get("/portfolio")
def get_portfolio():
    portfolio_path = os.path.join(os.path.dirname(__file__), "portfolio.json")
    with open(portfolio_path, "r") as f:
        return json.load(f)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
