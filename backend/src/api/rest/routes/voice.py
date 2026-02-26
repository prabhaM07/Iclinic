from fastapi import APIRouter, Query, Request
from fastapi.responses import Response
from twilio.twiml.voice_response import VoiceResponse, Gather
from src.control.voice_assistance.graph import build_call_graph, build_response_graph

router = APIRouter()
call_graph     = build_call_graph()
response_graph = build_response_graph()


@router.post("/make-call")
async def make_call(request: Request,response:Response,to_number: str = Query(...)):

    print("Received number:", to_number)

    try:
        result = await call_graph.ainvoke({
            "to_number": to_number,
            "call_sid":  None,
            "user_text": None,
            "ai_text":   None,
            "error":     None,
        })

        print("Graph result:", result)

        if result.get("error"):
            print("Graph error:", result["error"])
            return {"status": "error", "detail": result["error"]}

        return {"status": "call placed", "call_sid": result["call_sid"]}

    except Exception as e:
        print("Exception:", str(e))
        raise

@router.post("/twilio-webhook")
async def twilio_webhook(request: Request,response:Response):
    
    print("[twilio-webhook] Call answered")

    # Build TwiML response: greet then listen
    response = VoiceResponse()
    gather = Gather(
        input="speech",
        action="/voice-response",
        speech_timeout="auto",
        speech_model="phone_call",
        language="en-IN"
    )
    gather.say("Hello! How can I assist you today?", voice="alice")
    response.append(gather)

    # If user says nothing, redirect back and start again
    response.redirect("/twilio-webhook")

    return Response(content=str(response), media_type="application/xml")


@router.post("/voice-response")
async def voice_response(request: Request,response:Response):
    
    form = await request.form()
    speech_result = form.get("SpeechResult", "").strip()
    print(f"[voice-response] SpeechResult: {speech_result}")

    # Run the full pipeline
    result = await response_graph.ainvoke({
        "to_number": None,
        "call_sid":  None,
        "user_text": speech_result,
        "ai_text":   None,
        "error":     None,
    })

    ai_text = result.get("ai_text", "I'm sorry, I didn't understand that.")

    # Build TwiML response: speak ai_text then listen again
    response = VoiceResponse()
    gather = Gather(
        input="speech",
        action="/voice-response",
        speech_timeout="auto",
        speech_model="phone_call",
        language="en-IN"
    )
    gather.say(ai_text, voice="alice")
    response.append(gather)

    # If no response, redirect back
    response.redirect("/twilio-webhook")

    return Response(content=str(response), media_type="application/xml")