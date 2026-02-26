from langgraph.graph import StateGraph, END
from .state import VoiceState
from .nodes.call_init_node import call_init_node
from .nodes.stt_node import stt_node
from .nodes.think_node import think_node
from .nodes.tts_node import tts_node


def build_call_graph():
    
    workflow = StateGraph(VoiceState)
    workflow.add_node("call_init", call_init_node)
    workflow.set_entry_point("call_init")
    workflow.add_edge("call_init", END)
    return workflow.compile()


def build_response_graph():
    
    workflow = StateGraph(VoiceState)

    workflow.add_node("stt",   stt_node)
    workflow.add_node("think", think_node)
    workflow.add_node("tts",   tts_node)

    workflow.set_entry_point("stt")
    workflow.add_edge("stt",   "think")
    workflow.add_edge("think", "tts")
    workflow.add_edge("tts",   END)

    return workflow.compile()


