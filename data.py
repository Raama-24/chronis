"""
Fixed ground-truth data for Northstar One real estate project with persistent disk booked slots registry.
"""

import os
import json

PROJECT_DATA = {
    "project_name": "Northstar One",
    "location": "Sector 79, Gurugram",
    "developer": "Northstar Homes",
    "configurations": [
        {"type": "2 BHK", "starting_price_display": "₹1.35 Crore onwards"},
        {"type": "3 BHK", "starting_price_display": "₹1.75 Crore onwards"}
    ],
    "fixed_slots": [
        "2026-09-06 10:00",
        "2026-09-06 16:00",
        "2026-09-07 11:00",
        "2026-09-08 15:00",
        "2026-09-10 10:00"
    ]
}

BOOKINGS_FILE = os.path.join(os.path.dirname(__file__), "booked_slots.json")


def load_booked_slots() -> set[str]:
    """
    Loads saved booked slots from disk (booked_slots.json).
    Ensures slot locks persist across server restarts, reloads, and sessions!
    """
    if os.path.exists(BOOKINGS_FILE):
        try:
            with open(BOOKINGS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                return set(data)
        except Exception:
            return set()
    return set()


def save_booked_slots(slots_set: set[str]):
    """
    Saves the set of booked slots to disk (booked_slots.json).
    """
    with open(BOOKINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(list(slots_set), f, indent=2)


# Initialize booked slots from disk
BOOKED_SLOTS: set[str] = load_booked_slots()


def mark_slot_as_booked(slot_str: str):
    """
    Marks a slot as permanently booked and saves to disk registry.
    """
    cleaned = slot_str.strip()
    BOOKED_SLOTS.add(cleaned)
    save_booked_slots(BOOKED_SLOTS)


def get_available_slots() -> list[str]:
    """
    Returns only the slots from fixed_slots that have NOT been booked yet.
    """
    return [s for s in PROJECT_DATA["fixed_slots"] if s not in BOOKED_SLOTS]


def check_slot_availability(date_str: str, time_str: str = None) -> dict:
    """
    Deterministic slot checker against fixed slots minus already BOOKED_SLOTS.
    Returns availability status and remaining available alternative slots if unavailable.
    """
    all_fixed = PROJECT_DATA["fixed_slots"]
    available_slots = get_available_slots()
    
    matching_date_slots = [s for s in available_slots if date_str in s]
    
    if time_str:
        exact_target = f"{date_str} {time_str}".strip()
        
        # Check if it was already booked
        if exact_target in BOOKED_SLOTS:
            return {
                "available": False,
                "requested_slot": exact_target,
                "message": f"Requested slot {exact_target} has ALREADY BEEN BOOKED by another customer.",
                "alternatives": available_slots
            }
        
        if exact_target in available_slots:
            return {
                "available": True,
                "requested_slot": exact_target,
                "message": f"Slot {exact_target} is available for booking.",
                "alternatives": []
            }
        else:
            return {
                "available": False,
                "requested_slot": exact_target,
                "message": f"Requested slot {exact_target} is NOT a valid fixed slot.",
                "alternatives": available_slots
            }
    
    if matching_date_slots:
        return {
            "available": True,
            "requested_slot": date_str,
            "message": f"Available slots on {date_str}: {', '.join(matching_date_slots)}",
            "matching_slots": matching_date_slots,
            "alternatives": available_slots
        }
    
    # If the date had slots in fixed_slots but all are booked
    date_in_fixed = any(date_str in s for s in all_fixed)
    if date_in_fixed:
        return {
            "available": False,
            "requested_slot": date_str,
            "message": f"All slots on date {date_str} are ALREADY BOOKED.",
            "alternatives": available_slots
        }

    return {
        "available": False,
        "requested_slot": date_str,
        "message": f"No available slots on date {date_str}.",
        "alternatives": available_slots
    }
