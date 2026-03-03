from fastapi_mail import FastMail, MessageSchema, ConnectionConfig


conf = ConnectionConfig(
    MAIL_USERNAME="prabhamuruganantham06@gmail.com",
    MAIL_PASSWORD="ptyt oscx cego mthh",
    MAIL_FROM="prabhamuruganantham06@gmail.com",
    MAIL_PORT=587,
    MAIL_SERVER="smtp.gmail.com",
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True,
)


async def _send_confirmation_email(to_email: str, body: str) -> None:
    message = MessageSchema(
        subject="Your Appointment is Confirmed",
        recipients=[to_email],
        body=body,
        subtype="plain",
    )
    fm = FastMail(conf)
    await fm.send_message(message)


def _build_email_body(state: dict) -> str:
    doctor_name  = state.get("confirmed_doctor_name", "your doctor")
    slot_display = state.get("booked_slot_display", "the scheduled time")

    reason       = state.get("reason_for_visit")
    notes        = state.get("notes")
    instructions = state.get("instructions")

    lines = [
        "Dear Patient,",
        "",
        f"Your appointment has been successfully booked.",
        "",
        f"  Doctor  : {doctor_name}",
        f"  Slot    : {slot_display}",
    ]

    if reason:
        lines.append(f"  Reason  : {reason}")
    if notes:
        lines.append(f"  Notes   : {notes}")
    if instructions:
        lines.append(f"  Instructions : {instructions}")

    lines += [
        "",
        "Please arrive 10 minutes before your scheduled time.",
        "If you need to reschedule or cancel, contact us as soon as possible.",
        "",
        "Best regards,",
        "The Appointments Team",
    ]

    return "\n".join(lines)


async def booking_confirmation_node(state: dict) -> dict:

    print("i came here [booking_confirmation_node] -----------------------------")

    # Only run after a successful booking
    if not state.get("booked_slot_id"):
        return state


    patient_id = state.get("patient_id")

    try:
        to_email = state.get("user_email")

        if not to_email:
            print(f"[booking_confirmation_node] No email found for patient_id={patient_id}")
            return state

        body = _build_email_body(state)
        await _send_confirmation_email(to_email, body)
        print(f"[booking_confirmation_node] Confirmation email sent to {to_email}")

    except Exception as e:
        # Don't fail the whole flow if email sending fails
        print(f"[booking_confirmation_node] Failed to send confirmation email: {e}")

    return state