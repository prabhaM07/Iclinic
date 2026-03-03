from datetime import datetime, timezone
from sqlalchemy import select, and_
from src.data.clients.postgres_client import AsyncSessionLocal
from src.data.models.postgres.appointment import Appointment
from src.data.models.postgres.appointment_type import AppointmentType
from src.data.models.postgres.ENUM import AppointmentStatus
from src.control.voice_assistance.models import get_llama1
from src.data.repositories.generic_crud import update_instance


SELECT_PROMPT = """
You are a medical voice assistant.

The user has the following scheduled appointments:
{appointments_list}

The user said: "{user_text}"

Match what the user said to one of the appointment type names above.
Reply ONLY with the exact appointment type name from the list, nothing else.
If you cannot match, reply: UNKNOWN
"""

CONFIRM_PROMPT = """
You are a medical voice assistant.

The user wants to cancel this appointment:
Date: {date}
Time: {start_time} to {end_time}
Type: {appointment_type}

Ask: "Are you sure you want to cancel this appointment?"

If the user clearly agrees, reply: YES
If the user declines, reply: NO
Reply ONLY YES or NO.
"""


async def cancel_appointment_node(state: dict) -> dict:

    print("[cancel_appointment_node] -----------------------------")

    user_id = state.get("patient_id")
    user_text = state.get("user_text")
    stage = state.get("cancellation_stage")

    print(f"[cancel_appointment_node] user_id={user_id}, stage={stage}, user_text={user_text}")

    # -------------------------------------------
    # STAGE 1 → Fetch All Appointments & Ask Which
    # -------------------------------------------
    if stage is None:

        print("[cancel_appointment_node] STAGE 1 - fetching all scheduled appointments")

        try:
            async with AsyncSessionLocal() as session:

                stmt = (
                    select(Appointment, AppointmentType.name.label("type_name"))
                    .join(AppointmentType, Appointment.appointment_type_id == AppointmentType.id)
                    .where(
                        and_(
                            Appointment.patient_id == user_id,
                            Appointment.status == AppointmentStatus.SCHEDULED,
                            Appointment.is_active == True,
                        )
                    )
                    .order_by(Appointment.scheduled_date.asc())
                )

                result = await session.execute(stmt)
                rows = result.all()

                print(f"[cancel_appointment_node] Appointments found: {len(rows)}")

        except Exception as e:
            print(f"[cancel_appointment_node] DB ERROR: {type(e).__name__}: {e}")
            return {
                **state,
                "ai_text": "Something went wrong while fetching your appointments. Please try again.",
                "cancellation_complete": True,
            }

        if not rows:
            return {
                **state,
                "ai_text": "You do not have any scheduled appointments to cancel.",
                "cancellation_complete": True,
            }

        # Build appointments list for state
        appointments_list = []
        for appointment, type_name in rows:
            appointments_list.append({
                "id": appointment.id,
                "date": str(appointment.scheduled_date),
                "start_time": str(appointment.scheduled_start_time),
                "end_time": str(appointment.scheduled_end_time),
                "reason": appointment.reason_for_visit or "Not specified",
                "type_name": type_name,
            })

        # Build spoken list for user
        spoken_list = ", ".join(
            [f"{i+1}. {a['type_name']} on {a['date']}" for i, a in enumerate(appointments_list)]
        )

        return {
            **state,
            "appointments_list": appointments_list,
            "cancellation_stage": "ask_which",
            "ai_text": (
                f"You have {len(appointments_list)} scheduled appointment"
                f"{'s' if len(appointments_list) > 1 else ''}. "
                f"{spoken_list}. "
                f"Which appointment type would you like to cancel?"
            ),
        }

    # -------------------------------------------
    # STAGE 2 → Match User Choice to Appointment
    # -------------------------------------------
    if stage == "ask_which":

        print("[cancel_appointment_node] STAGE 2 - matching user choice")

        appointments_list = state.get("appointments_list", [])

        if not user_text:
            return {
                **state,
                "ai_text": "Please say the name of the appointment type you want to cancel.",
            }

        # If only one appointment, skip selection
        if len(appointments_list) == 1:
            chosen = appointments_list[0]
            print(f"[cancel_appointment_node] Only one appointment, auto-selecting: {chosen}")
        else:
            try:
                model = get_llama1()

                spoken_types = "\n".join(
                    [f"- {a['type_name']}" for a in appointments_list]
                )

                response = await model.ainvoke([
                    ("system", SELECT_PROMPT.format(
                        appointments_list=spoken_types,
                        user_text=user_text,
                    )),
                    ("human", user_text),
                ])

                matched_type = response.content.strip()
                print(f"[cancel_appointment_node] LLM matched type: '{matched_type}'")

            except Exception as e:
                print(f"[cancel_appointment_node] LLM ERROR: {type(e).__name__}: {e}")
                return {
                    **state,
                    "ai_text": "Something went wrong. Please try again.",
                    "cancellation_complete": True,
                }

            if matched_type == "UNKNOWN":
                type_names = ", ".join([a["type_name"] for a in appointments_list])
                return {
                    **state,
                    "ai_text": (
                        f"I could not understand which appointment you meant. "
                        f"Please say one of these: {type_names}."
                    ),
                }

            # Find matching appointment from list
            chosen = next(
                (a for a in appointments_list if a["type_name"].lower() == matched_type.lower()),
                None
            )

            if not chosen:
                type_names = ", ".join([a["type_name"] for a in appointments_list])
                return {
                    **state,
                    "ai_text": (
                        f"I could not find that appointment type. "
                        f"Please choose from: {type_names}."
                    ),
                }

        return {
            **state,
            "appointment_to_cancel": chosen,
            "cancellation_stage": "ask_confirm",
            "ai_text": (
                f"You selected {chosen['type_name']} on {chosen['date']} "
                f"from {chosen['start_time']} to {chosen['end_time']}. "
                f"Are you sure you want to cancel this appointment?"
            ),
        }

    # -------------------------------------------
    # STAGE 3 → Confirm & Cancel
    # -------------------------------------------
    if stage == "ask_confirm":

        print("[cancel_appointment_node] STAGE 3 - confirming cancellation")

        appointment_data = state.get("appointment_to_cancel")

        if not user_text:
            return {
                **state,
                "ai_text": "Please confirm. Do you want to cancel this appointment?",
            }

        try:
            model = get_llama1()
            response = await model.ainvoke([
                ("system", CONFIRM_PROMPT.format(
                    date=appointment_data["date"],
                    start_time=appointment_data["start_time"],
                    end_time=appointment_data["end_time"],
                    appointment_type=appointment_data["type_name"],
                )),
                ("human", user_text),
            ])

            decision = response.content.strip().upper()
            print(f"[cancel_appointment_node] Decision: '{decision}'")

        except Exception as e:
            print(f"[cancel_appointment_node] LLM ERROR: {type(e).__name__}: {e}")
            return {
                **state,
                "ai_text": "Something went wrong. Please try again.",
                "cancellation_complete": True,
            }

        if decision == "YES":

            try:
                async with AsyncSessionLocal() as session:
                    await update_instance(
                        id=appointment_data["id"],
                        model=Appointment,
                        db=session,
                        status=AppointmentStatus.CANCELLED,
                        cancelled_at=datetime.now(timezone.utc),
                        cancellation_reason="Cancelled via voice assistant",
                        is_active=False,
                    )
                print("[cancel_appointment_node] Appointment cancelled in DB")

            except Exception as e:
                print(f"[cancel_appointment_node] DB ERROR: {type(e).__name__}: {e}")
                return {
                    **state,
                    "ai_text": "Something went wrong while cancelling. Please try again.",
                    "cancellation_complete": True,
                }

            return {
                **state,
                "ai_text": f"Your {appointment_data['type_name']} appointment on {appointment_data['date']} has been successfully cancelled.",
                "cancellation_stage": "done",
                "cancellation_complete": True,
            }

        else:
            return {
                **state,
                "ai_text": "Okay, your appointment remains scheduled.",
                "cancellation_stage": "done",
                "cancellation_complete": True,
            }

    print(f"[cancel_appointment_node] WARNING: Unhandled stage='{stage}'")



    