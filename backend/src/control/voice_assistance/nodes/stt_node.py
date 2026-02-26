
async def stt_node(state: dict) -> dict:
    
    user_text = state.get("user_text", "").strip()

    if not user_text:
        print("[stt_node] No speech detected")
        return {**state, "user_text": None}

    print(f"[stt_node] Transcript: {user_text}")
    return {**state, "user_text": user_text}

