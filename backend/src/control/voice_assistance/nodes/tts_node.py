
async def tts_node(state: dict) -> dict:
    
    ai_text = state.get("ai_text", "").strip()

    if not ai_text:
        return {**state, "ai_text": "I'm sorry, I couldn't generate a response."}

    print(f"[tts_node] Ready to speak: {ai_text}")
    return {**state, "ai_text": ai_text}


