from typing import Optional
from typing_extensions import TypedDict


class VoiceState(TypedDict):
    to_number:  Optional[str]
    call_sid:   Optional[str]
    user_text:  Optional[str]
    ai_text:    Optional[str]
    error:      Optional[str]


    