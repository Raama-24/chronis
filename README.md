# Northstar One - Conversational Real Estate Sales Bot (Aanya)

A lightweight, high-performance, full-stack conversational sales bot built for "Northstar One" real estate project in Sector 79, Gurugram by Northstar Homes.

---

## Technical Architecture Overview

```
+------------------------+             +--------------------------+
|  Frontend (index.html) |  fetch()    |   FastAPI Server (main)  |
|  - Vanilla JS          | ----------> | - In-Memory Session Dict |
|  - Mode Selector       | <---------- | - Static File Mounting   |
|    (Chat / Voice)      |             | - Prompt Mode Formatter  |
+------------------------+             +------------+-------------+
                                                    |
                                       +------------+-------------+
                                       | Deterministic Slot Check |
                                       |      (data.py)           |
                                       +------------+-------------+
                                                    |
                                       +------------+-------------+
                                       |     LLM Client & Models  |
                                       | (llm_client.py / Groq)   |
                                       +--------------------------+
```

### Key Design Decisions

1. **Dual Interaction Modes (`chat` vs `voice`)**:
   - Single unified System Prompt handles both text chat and voice interface styles dynamically based on `interaction_mode` passed in `ChatRequest`.
   - **CHAT mode**: Normal response length, bullet lists allowed, standard formatting.
   - **VOICE mode**: Short conversational responses (1–3 sentences), spoken-style numbers ("one crore thirty five lakh" instead of "₹1.35 Cr"), zero markdown/bullets/emojis.

2. **Why No RAG, Vector DB, or LangChain/Agent Frameworks?**
   - Real estate property specs and fixed visit calendars for a single project are bounded and deterministic facts. 
   - Injecting complete ground-truth data directly into the System Prompt eliminates vector retrieval latency, chunking inaccuracies, context fragmentation, and agent framework overhead.

3. **Why Deterministic Python Slot-Checking?**
   - Calendar availability must never be left to LLM probabilistic hallucination.
   - The backend checks requested dates/times against `PROJECT_DATA['fixed_slots']` using deterministic python logic in `data.py` and injects a `[SYSTEM SLOT CHECK RESULT]` directive before LLM generation.

4. **Why In-Memory Session Storage?**
   - Plain Python dictionary keyed by `session_id` provides zero-latency context retrieval without database setup overhead.

5. **Structured Post-Conversation Analytics & Guardrails:**
   - Upon clicking "End Conversation", `/end_session` sends the full transcript history to Groq LLM with `analytics_prompt.py` to extract structured JSON insights validated via Pydantic `AnalyticsResponse`.
   - Includes specific compliance fields: `do_not_contact`, `escalated_to_human`, and `follow_up_preferred_time`.

---

## File Structure & Descriptions

- `data.py`: Fixed ground-truth facts for Northstar One (Developer, Sector 79, 2BHK starting ₹1.35 Cr, 3BHK starting ₹1.75 Cr), fixed slots, and `check_slot_availability()`.
- `prompt.py`: `get_system_prompt(interaction_mode)` returning Aanya's persona system prompt with facts, mode guidelines, qualification goals, opt-out rules, human escalation, and slot check instructions.
- `analytics_prompt.py`: Strict JSON extraction prompt for transcript intelligence post-session (includes `do_not_contact`, `escalated_to_human`, `follow_up_preferred_time`).
- `models.py`: Pydantic models `ChatRequest` (with `interaction_mode`), `ChatResponse`, and `AnalyticsResponse`.
- `llm_client.py`: Groq SDK client wrapper reading environment variables via `python-dotenv`.
- `main.py`: FastAPI server containing in-memory session management, deterministic slot middleware, `/chat`, `/end_session`, and static file hosting.
- `static/index.html`: Clean, responsive web UI with real-time chat window, Chat/Voice mode toggle dropdown, session generator, and interactive analytics modal.
- `test_cases.md`: 9 scripted test conversations covering normal booking, objections, slot failures, Hinglish support, unknown info refusals, discount refusals, opt-outs, busy customer follow-ups, and human escalation.
- `requirements.txt`: Project dependencies (`fastapi`, `uvicorn`, `pydantic`, `python-dotenv`, `groq`).

---

## How to Run Locally

### 1. Prerequisites & Environment Setup
Ensure Python 3.10+ is installed. Clone/navigate to the directory:

```bash
# Install dependencies
pip install -r requirements.txt
```

Create a `.env` file in the project root:
```env
GROQ_API_KEY=your_actual_groq_api_key_here
GROQ_MODEL=llama-3.3-70b-versatile
```

### 2. Launch FastAPI Server
Run the application using Uvicorn:

```bash
uvicorn main:app --reload
```

### 3. Open Web Interface
Navigate to `http://127.0.0.1:8000` in your browser. Select "Mode: Chat" or "Mode: Voice" to test different response styles.

---

## Verification & Testing

Inspect [test_cases.md](file:///c:/Users/Raama/OneDrive/Desktop/chronis/test_cases.md) to verify expected behaviors for all 9 required conversation scenarios.
