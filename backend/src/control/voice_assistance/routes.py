def route_after_stt(state: dict) -> str:
    """
    After stt_node:
      - confirmation already done → skip straight to clarify
      - otherwise → go through confirmation as normal
    """
    if state.get("confirmation_done"):
        return "clarify"
    return "confirmation"


def route_after_confirmation(state: dict) -> str:
    """
    After confirmation_node:
      - Not done (greeting / re-ask / pending) → tts
      - Done, denied                           → tts  (goodbye)
      - Done, confirmed, speak_final=True      → tts  (speak END_OK first)
      - Done, confirmed, speak_final done      → clarify
    """
    if not state.get("confirmation_done"):
        return "tts"
    if not state.get("confirmed_user"):
        return "tts"
    if state.get("speak_final"):
        return "tts"
    return "clarify"


def route_after_clarify(state: dict) -> str:
    """
    After clarify_node:
      - Emergency  → tts
      - Not done   → tts  (next question)
      - Done       → mapping
    """
    if state.get("emergency"):
        return "tts"
    if not state.get("clarify_done"):
        return "tts"
    return "mapping"


def route_after_doctor_selection(state: dict) -> str:
    """
    After doctor_selection_node:
      - Doctor confirmed → slot_selection  (move to booking)
      - Still pending    → tts             (speak the list first, wait for user)
    """
    if state.get("confirmed_doctor_id"):
        return "slot_selection"
    return "tts"

def route_after_slot_selection(state: dict) -> str:
    """
    After slot_selection_node:
      - User has picked a slot and it's ready to book → book_appointment
      - Still collecting date / period / slot info    → tts (speak next prompt)
    """
    if state.get("slot_stage") == "ready_to_book":
        return "book_appointment"
    return "tts"

