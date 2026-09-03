# Northstar One - Conversational Real Estate Sales Bot (Aanya)

A lightweight, high-performance, full-stack conversational sales bot built for Northstar One real estate project in Sector 79, Gurugram by Northstar Homes.

How to Run the Bot:
Step-by-step setup instructions (pip install -r requirements.txt, .env key configuration, uvicorn main:app --reload).

Key Assumptions:
Single-project domain boundaries (Northstar One, Sector 79 Gurugram, 2 BHK starting ₹1.35 Cr, 3 BHK starting ₹1.75 Cr).
Deterministic slot management and disk persistence (booked_slots.json, persisted_sessions/).
Automated lead extraction and name-based returning customer lookup (archived_leads/).

Known Limitations:
Flat JSON file storage for sessions/leads (production multi-node deployment would use Redis/PostgreSQL).
Speech Recognition and Speech Synthesis rely on browser APIs (supported best in Chromium-based browsers like Chrome and Edge).
Dependent on Google Gemini API availability and free-tier quotas (15 RPM / 1,500 RPD).

AI Tools Used:
Claude: Pair programming, architecture design, and code refactoring.
Google Gemini API (google-genai SDK): Powered by gemini-3.1-flash-lite for conversation dialog and structured JSON lead analytics.

## How to Run Locally

### 1. Prerequisites & Environment Setup
Ensure Python 3.10+ is installed. Clone/navigate to the directory:
# Install dependencies
pip install -r requirements.txt

Create a .env file in the project root:

GROQ_API_KEY=your_actual_groq_api_key_here
GROQ_MODEL=llama-3.3-70b-versatile


### 2. Launch FastAPI Server
Run the application using Uvicorn:

uvicorn main:app --reload


### 3. Open Web Interface
Navigate to `http://127.0.0.1:8000` in your browser. Select "Mode: Chat" or "Mode: Voice" to test different response styles.


## Verification & Testing

Inspect test_cases.md to verify expected behaviors for all 9 required conversation scenarios.
