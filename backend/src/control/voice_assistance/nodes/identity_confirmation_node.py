import json
from typing import Dict, Any
from src.control.voice_assistance.prompts.confirmation_node_prompt import CONVERSATION_PROMPT, VERIFIER_PROMPT
from src.control.voice_assistance.models import ainvoke_llm
from src.control.voice_assistance.utils import clear_markdown


async def identity_confirmation_node(state: Dict[str, Any]) -> Dict[str, Any]:

    print("[identity_confirmation_node] -----------------------------")

    patient_name: str = (state.get("user_name") or "").strip()
    phone_number: str = (state.get("user_phone") or "").strip()
    user_text: str = (state.get("user_text") or "").strip()

    if not patient_name:
        return state

    conversation: list = list(state.get("conversation") or [])

    if user_text:

        print("[user_response] :", user_text)
        
        conversation.append({"role": "user", "content": user_text})

    conv_messages = [
        {
            "role": "system",
            "content": CONVERSATION_PROMPT.format(name=patient_name, phone=phone_number)
        },
        *conversation
    ]

    if not any(m["role"] == "user" for m in conv_messages):
        conv_messages.append({"role": "user", "content": "start"})

    try:
        conv_response = await ainvoke_llm(conv_messages)
        sentence: str = conv_response.content.strip()

    except Exception:
        return state

    confirmed = False
    end_call = False
    corrected_name = None
    corrected_phone = None

    if user_text:

        verify_messages = [
            {"role": "system", "content": VERIFIER_PROMPT},
            {"role": "user", "content": f"Conversation so far:\n{conv_messages}\n\nLatest user reply: {user_text}"}
        ]

        try:
            verify_response = await ainvoke_llm(verify_messages)
            verify_response = verify_response.content.strip()
            raw = clear_markdown(verify_response)
            data = json.loads(raw)

            confirmed = bool(data.get("confirmed", False))
            end_call = bool(data.get("end_call", False))
            corrected_name = data.get("corrected_name")
            corrected_phone = data.get("corrected_phone")

        except Exception as e:
            print("[VERIFIER ERROR]", e)

    if corrected_name:
        state["user_name"] = corrected_name
    if corrected_phone:
        state["user_phone"] = corrected_phone

    conversation.append({"role": "assistant", "content": sentence})

    return {
        **state,
        "conversation": conversation,
        "confirmed_user": confirmed,
        "confirmation_done": confirmed or end_call,
        "ai_text": sentence,
    }

