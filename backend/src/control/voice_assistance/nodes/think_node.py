from src.control.voice_assistance.models import get_llama1

llm = get_llama1()

async def think_node(state: dict) -> dict:
    
    try:
        user_text = state.get("user_text")
        if not user_text:
            return {**state, "ai_text": "I didn't catch that. Could you please repeat?"}

        response = await llm.ainvoke([
            ("system", "You are a helpful voice assistant. Reply in 1-2 sentences. Be concise since your response will be spoken aloud."),
            ("human", user_text)
        ])

        print(f"[think_node] Groq: {response.content}")
        return {**state, "ai_text": response.content}

    except Exception as e:
        print(f"[think_node] Error: {e}")
        return {**state, "error": str(e)}
    

