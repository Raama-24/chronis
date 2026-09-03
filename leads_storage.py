import os
import json
import logging
from datetime import datetime

# Directory for storing archived session analytics JSON files
LEADS_DIR = os.path.join(os.path.dirname(__file__), "archived_leads")
SESSIONS_DIR = os.path.join(os.path.dirname(__file__), "persisted_sessions")
os.makedirs(LEADS_DIR, exist_ok=True)
os.makedirs(SESSIONS_DIR, exist_ok=True)

logger = logging.getLogger("leads_archiver")


def save_lead_analytics(session_id: str, analytics_dict: dict) -> str:
    """
    Saves the extracted analytics JSON object to disk inside the archived_leads/ folder.
    Returns the file path where the lead was saved.
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"lead_{session_id}_{timestamp}.json"
    filepath = os.path.join(LEADS_DIR, filename)
    
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(analytics_dict, f, indent=2, ensure_ascii=False)
        
    logger.info(f"[Lead Storage] Saved session analytics to: {filepath}")
    return filepath


def save_session_to_disk(session_id: str, session_data: dict):
    """
    Saves full session history and state to disk in persisted_sessions/<session_id>.json.
    """
    filepath = os.path.join(SESSIONS_DIR, f"{session_id}.json")
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(session_data, f, indent=2, ensure_ascii=False)
    logger.info(f"[Session Persistence] Saved session '{session_id}' to disk.")


def load_session_from_disk(session_id: str) -> dict | None:
    """
    Loads persisted session history and state from disk if it exists.
    """
    filepath = os.path.join(SESSIONS_DIR, f"{session_id}.json")
    if os.path.exists(filepath):
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
            logger.info(f"[Session Persistence] Loaded session '{session_id}' from disk.")
            return data
        except Exception as e:
            logger.error(f"[Session Persistence Error] Failed reading '{session_id}.json': {e}")
    return None


def search_lead_by_name(customer_name: str) -> dict | None:
    """
    Searches archived_leads/ files for a customer by name (case-insensitive).
    Returns the lead dict summary if found, else None.
    """
    if not customer_name or len(customer_name.strip()) < 2:
        return None

    target_name = customer_name.strip().lower()

    if not os.path.exists(LEADS_DIR):
        return None

    # Search leads in reverse chronological order (newest first)
    files = sorted(os.listdir(LEADS_DIR), reverse=True)
    for fname in files:
        if fname.endswith(".json"):
            fpath = os.path.join(LEADS_DIR, fname)
            try:
                with open(fpath, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    cname = data.get("customer_name")
                    if cname and target_name in cname.lower():
                        logger.info(f"[Name Lookup] Found matching lead record for '{customer_name}' in {fname}")
                        return data
            except Exception as e:
                logger.error(f"[Name Lookup Error] Reading {fname}: {e}")

    return None
