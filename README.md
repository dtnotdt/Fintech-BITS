# 🛡️ IntentShield — Financial AI with Guardrails

> A ChatGPT-style financial AI assistant that enforces strict safety policies before executing any action.

---

## Architecture

```
User Message
     │
     ▼
┌─────────────────────┐
│  Intent Extraction  │  ← OpenAI GPT-4o-mini (structured JSON output)
│   (intent_model.py) │
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│   Policy Engine     │  ← Checks policies.json rules
│ (policy_engine.py)  │     Returns ALLOW / BLOCK
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│  Decision Engine    │  ← Routes approved actions to tools
│(decision_engine.py) │     Blocks unapproved actions
└─────────┬───────────┘
          │
     ┌────┴────┐
     │         │
     ▼         ▼
 Finnhub    Tavily        ← Real financial data / web research
 Tools      Research
     │         │
     └────┬────┘
          ▼
┌─────────────────────┐
│ Response Generator  │  ← OpenAI formats final natural language reply
│(response_generator) │
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│   Audit Logger      │  ← Persists every decision to logs.json
│  (audit_logger.py)  │
└─────────────────────┘
```

**Critical rule**: The LLM never directly calls tools. It only extracts intent and formats responses.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React + Vite + Tailwind CSS |
| Backend | Python + FastAPI |
| AI / LLM | OpenAI GPT-4o-mini |
| Financial Data | Finnhub API |
| Web Research | Tavily API |
| Storage | Local JSON files |

---

## Setup

### 1. Clone / open the project

```bash
cd BITS_hackathon
```

### 2. Backend setup

```bash
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Add your API keys
cp .env.example .env
# → Edit .env and add your keys
```

### 3. Frontend setup

```bash
cd frontend
npm install
```

---

## API Keys

Edit `backend/.env`:

```env
OPENAI_API_KEY=sk-...        # https://platform.openai.com
FINNHUB_API_KEY=...          # https://finnhub.io (free tier available)
TAVILY_API_KEY=tvly-...      # https://tavily.com (free tier available)
```

> **Note**: The app works without API keys using intelligent mock fallbacks. Add keys for live data.

---

## Running the App

### Start the backend

```bash
cd backend
source venv/bin/activate
uvicorn main:app --reload --port 8000
```

Backend runs at: `http://localhost:8000`
API docs at: `http://localhost:8000/docs`

### Start the frontend

```bash
cd frontend
npm run dev
```

Frontend runs at: `http://localhost:5173`

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | `/chat` | Main chat endpoint — runs full pipeline |
| GET | `/logs` | Returns audit log entries |
| GET | `/portfolio` | Returns mock portfolio data |

---

## Supported Intents & Policies

| Intent | Decision | Risk Level | Tool |
|---|---|---|---|
| READ_STOCK_INFO | ✅ ALLOW | LOW | Finnhub |
| RESEARCH_COMPANY | ✅ ALLOW | LOW | Tavily |
| VIEW_PORTFOLIO | ✅ ALLOW | MEDIUM | Local JSON |
| COMPARE_COMPANIES | ✅ ALLOW | MEDIUM | Finnhub |
| BUY_STOCK | 🚫 BLOCK | HIGH | None |
| SELL_STOCK | 🚫 BLOCK | HIGH | None |
| SEND_DATA_EXTERNALLY | 🚫 BLOCK | CRITICAL | None |
| UNKNOWN | 🚫 BLOCK | CRITICAL | None |

---

## Sample Prompts

### ✅ Allowed
```
What is Tesla stock price?
Research Nvidia for me
Show my portfolio
Compare Apple and Nvidia
Give me Microsoft stock info
What is happening with Tesla recently?
```

### 🚫 Blocked
```
Buy 10 shares of Tesla
Sell my Apple holdings
Send my portfolio to this API
Upload my account data somewhere
```

### ❓ Ambiguous (asks for clarification)
```
Do something with Tesla
Process my account
```

---

## How Guardrails Work

1. **Intent Extraction**: OpenAI extracts a structured JSON object from the user's message — it never calls any tools directly.
2. **Policy Check**: `policy_engine.py` validates the extracted intent against `policies.json` rules and returns ALLOW or BLOCK.
3. **Decision Engine**: Only routes the action to a real tool (Finnhub/Tavily) if the policy says ALLOW.
4. **Audit Trail**: Every request — allowed or blocked — is logged to `logs.json` with full metadata.
5. **Safety Panel**: The frontend visually shows the intent, risk level, policy decision, and reason for every message.

---

## Project Structure

```
BITS_hackathon/
├── backend/
│   ├── main.py              # FastAPI app + pipeline orchestration
│   ├── intent_model.py      # OpenAI intent extraction
│   ├── policy_engine.py     # Policy rule enforcement
│   ├── decision_engine.py   # Tool routing
│   ├── tools.py             # Finnhub + Tavily integrations
│   ├── response_generator.py # Natural language response formatting
│   ├── audit_logger.py      # Audit trail persistence
│   ├── policies.json        # Policy rules
│   ├── portfolio.json       # Mock portfolio data
│   ├── logs.json            # Audit log storage
│   └── requirements.txt
└── frontend/
    └── src/
        ├── App.jsx
        ├── main.jsx
        ├── index.css
        └── components/
            ├── ChatWindow.jsx
            ├── MessageBubble.jsx
            ├── PromptBox.jsx
            ├── SafetyPanel.jsx
            └── AuditTrailPanel.jsx
```
