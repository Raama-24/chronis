import re
import json
import logging
import traceback
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from models import ChatRequest, ChatResponse, AnalyticsResponse
from data import check_slot_availability, mark_slot_as_booked, get_available_slots
from prompt import get_system_prompt
from analytics_prompt import ANALYTICS_PROMPT
from llm_client import call_llm
from leads_storage import save_lead_analytics, save_session_to_disk, load_session_from_disk, search_lead_by_name

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("main_api")

app = FastAPI(title="Northstar One Conversational Sales Bot")

# In-memory session history storage
sessions: dict[str, dict] = {}


def detect_and_check_slot(user_message: str) -> tuple[str | None, dict | None]:
    """
    Enhanced regex & NLP pattern matcher for site visit slot bookings.
    Checks date and time requests against unbooked available slots.
    """
    user_lower = user_message.lower()
    
    # 1. Date extraction
    date_match = re.search(r'(\d{4}-\d{2}-\d{2})', user_message)
    req_date = None
    if date_match:
        req_date = date_match.group(1)
    else:
        for day, date_str in [("6", "2026-09-06"), ("06", "2026-09-06"), 
                              ("7", "2026-09-07"), ("07", "2026-09-07"),
                              ("8", "2026-09-08"), ("08", "2026-09-08"),
                              ("10", "2026-09-10"), ("9", "2026-09-09")]:
            if (f"{day} sep" in user_lower or f"{day}th sep" in user_lower or 
                f"sep {day}" in user_lower or f"september {day}" in user_lower or
                f"{day}th september" in user_lower or f"date {day}" in user_lower or
                f"{day} date" in user_lower):
                req_date = date_str
                break

    # 2. Time extraction (handles 10:00, 10am, 10 am, 16:00, 4pm, 4 pm, 11am, 3pm)
    req_time = None
    time_match = re.search(r'(\d{1,2}:\d{2})', user_message)
    if time_match:
        req_time = time_match.group(1)
    elif "10" in user_lower and ("am" in user_lower or "baje" in user_lower or "morning" in user_lower or "10:00" in user_lower or "10" in user_lower):
        req_time = "10:00"
    elif ("16" in user_lower or "4 pm" in user_lower or "4pm" in user_lower or "4 baje" in user_lower or "evening" in user_lower):
        req_time = "16:00"
    elif ("11" in user_lower) and ("am" in user_lower or "baje" in user_lower or "11" in user_lower):
        req_time = "11:00"
    elif ("15" in user_lower or "3 pm" in user_lower or "3pm" in user_lower or "3 baje" in user_lower):
        req_time = "15:00"

    booking_intent_words = ["book", "reserve", "schedule", "site visit", "visit", "slot", "bhk"]
    has_site_visit_query = any(kw in user_lower for kw in booking_intent_words)

    if req_date:
        res = check_slot_availability(req_date, req_time)
        
        # If available exact slot, mark as permanently booked
        if req_time and res["available"]:
            exact_target = f"{req_date} {req_time}".strip()
            mark_slot_as_booked(exact_target)

        system_note = (
            f"[SYSTEM SLOT CHECK RESULT for date '{req_date}' "
            f"{'time ' + req_time if req_time else ''}]:\n"
            f"Available: {res['available']}\n"
            f"Message: {res['message']}\n"
            f"Remaining Available Fixed Slots: {', '.join(res['alternatives']) if res['alternatives'] else 'None'}"
        )
        return system_note, res
    elif has_site_visit_query:
        available = get_available_slots()
        system_note = (
            f"[SYSTEM SLOT CHECK RESULT]: Customer asked about site visits / apartment options.\n"
            f"Currently Remaining Available Fixed Slots: {', '.join(available) if available else 'None'}"
        )
        return system_note, {"available": True, "alternatives": available}

    return None, None


def detect_name_intro(user_message: str) -> str | None:
    msg = user_message.strip()
    patterns = [
        r'(?:i am|i\'m|my name is|this is|myself)\s+([A-Za-z]+)',
        r'^([A-Za-z]+)\s+here$'
    ]
    for pat in patterns:
        m = re.search(pat, msg, re.IGNORECASE)
        if m:
            name = m.group(1)
            if name.lower() not in ["a", "the", "hello", "hi", "hey", "looking", "interested"]:
                return name
    return None


@app.get("/history/{session_id}")
def get_session_history(session_id: str):
    if session_id in sessions:
        return {"history": sessions[session_id]["history"]}
    
    disk_session = load_session_from_disk(session_id)
    if disk_session:
        sessions[session_id] = disk_session
        return {"history": disk_session["history"]}
    
    return {"history": []}


@app.post("/chat", response_model=ChatResponse)
def chat_endpoint(req: ChatRequest):
    try:
        session_id = req.session_id
        user_msg = req.message.strip()
        interaction_mode = req.interaction_mode.lower()

        logger.info(f"[/chat] Session: {session_id} | Mode: {interaction_mode} | Message: '{user_msg}'")

        if session_id not in sessions:
            disk_session = load_session_from_disk(session_id)
            if disk_session:
                sessions[session_id] = disk_session
            else:
                sessions[session_id] = {"history": [], "state": {}}

        session = sessions[session_id]
        
        # Prepare full history list for LLM context
        llm_messages = list(session["history"])
        llm_messages.append({"role": "user", "content": user_msg})

        # Name-based lead lookup feature:
        extracted_name = detect_name_intro(user_msg)
        if extracted_name and len(session["history"]) <= 1:
            past_lead = search_lead_by_name(extracted_name)
            if past_lead:
                lead_context_note = (
                    f"[SYSTEM DATABASE RECORD FOUND FOR RETURNING CUSTOMER '{past_lead.get('customer_name')}']:\n"
                    f"- Previous Summary: {past_lead.get('conversation_summary')}\n"
                    f"- Site Visit Status: {past_lead.get('site_visit_status')}\n"
                    f"- Follow-up Time: {past_lead.get('follow_up_preferred_time')}\n"
                    f"- Configuration Interest: {past_lead.get('configuration_interest')}\n"
                    f"INSTRUCTION: Greet {past_lead.get('customer_name')} back warmly as a returning customer! State that you recall their previous visit/inquiry details from our records, restate their confirmed slot or query, and ask how you can help them further."
                )
                logger.info(f"[/chat] Injected Lead Context for returning customer '{extracted_name}'")
                llm_messages.append({"role": "user", "content": f"\n\n{lead_context_note}"})

        # Run slot check whenever customer asks about site visits or 2/3 bhk options
        slot_check_result, slot_res = detect_and_check_slot(user_msg)
        if slot_check_result:
            logger.info(f"[/chat] Injected Slot Check Result: {slot_check_result}")
            llm_messages.append({"role": "user", "content": f"\n\n{slot_check_result}"})

        system_prompt = get_system_prompt(interaction_mode=interaction_mode)

        reply_text = call_llm(messages=llm_messages, system_prompt=system_prompt)
        logger.info(f"[/chat] Bot Reply generated successfully ({len(reply_text)} chars)")

        # Record exact user message and reply into persistent thread history
        session["history"].append({"role": "user", "content": user_msg})
        session["history"].append({"role": "assistant", "content": reply_text})

        # Persist session to disk
        save_session_to_disk(session_id, session)

        return ChatResponse(reply=reply_text)
    except Exception as e:
        err_stack = traceback.format_exc()
        logger.error(f"[/chat ERROR]: {e}\n{err_stack}")
        raise HTTPException(
            status_code=500, 
            detail=f"Error in /chat endpoint: {str(e)}"
        )


@app.post("/end_session", response_model=AnalyticsResponse)
def end_session_endpoint(req: dict):
    try:
        session_id = req.get("session_id")
        logger.info(f"[/end_session] Ending session: {session_id}")

        if not session_id or (session_id not in sessions and not load_session_from_disk(session_id)):
            logger.warning(f"[/end_session] Session ID '{session_id}' not found.")
            return AnalyticsResponse(
                customer_name=None,
                budget_mentioned=None,
                configuration_interest=None,
                interest_level="cold",
                site_visit_status="not_requested",
                follow_up_required=False,
                objections_raised=[],
                language_used="English",
                conversation_summary="No active session history recorded.",
                do_not_contact=False,
                escalated_to_human=False,
                follow_up_preferred_time=None
            )

        if session_id not in sessions:
            sessions[session_id] = load_session_from_disk(session_id)

        session_history = sessions[session_id]["history"]
        transcript_text = "\n".join([f"{msg['role'].upper()}: {msg['content']}" for msg in session_history])

        analytics_messages = [
            {"role": "user", "content": f"TRANSCRIPT:\n{transcript_text}"}
        ]

        raw_json_str = call_llm(messages=analytics_messages, system_prompt=ANALYTICS_PROMPT)
        
        clean_json_str = raw_json_str.strip()
        if clean_json_str.startswith("```"):
            clean_json_str = re.sub(r'^```(?:json)?\n?', '', clean_json_str)
            clean_json_str = re.sub(r'\n?```$', '', clean_json_str)

        parsed_data = json.loads(clean_json_str)
        analytics = AnalyticsResponse(**parsed_data)

        logger.info(f"Successfully extracted analytics summary for session: {session_id}")

        # Archive analytics to disk in archived_leads/
        save_lead_analytics(session_id, analytics.model_dump())

        return analytics
    except Exception as e:
        err_stack = traceback.format_exc()
        logger.error(f"[/end_session ERROR]: {e}\n{err_stack}")
        return AnalyticsResponse(
            customer_name=None,
            budget_mentioned=None,
            configuration_interest=None,
            interest_level="warm",
            site_visit_status="not_requested",
            follow_up_required=True,
            objections_raised=[],
            language_used="English",
            conversation_summary=f"Error extracting structured analytics: {str(e)}",
            do_not_contact=False,
            escalated_to_human=False,
            follow_up_preferred_time=None
        )


# Mount static assets
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
def read_root():
    return FileResponse("static/index.html")
