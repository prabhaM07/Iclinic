
# Speech-to-text is handled by Twilio's <Gather> element.
# This node normalises and sanitises the transcribed text before


async def stt_node(state: dict) -> dict:
    print("i came here [stt_node] -----------------------------")

    user_text: str | None = state.get("user_text")

    if not user_text:
        return {**state, "user_text": None}

    # trim leading/trailing spaces
    cleaned = " ".join(user_text.split()).strip()

    return {**state, "user_text": cleaned}