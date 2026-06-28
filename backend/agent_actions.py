def get_contact_reply(message):
    message = message.lower()

    if "email" in message or "mail" in message:
        return "info@ebl-bd.com"

    if "hotline" in message:
        return "16230"

    if (
        "phone" in message
        or "number" in message
        or "call center" in message
        or "helpline" in message
    ):
        return (
            "Hotline: 16230\n"
            "From overseas: +8809677716230\n"
            "General contact number: +8809666777325"
        )

    return (
        "Email: info@ebl-bd.com\n"
        "Hotline: 16230\n"
        "From overseas: +8809677716230\n"
        "General contact number: +8809666777325"
    )


def get_online_apply_reply(message):
    return (
        "You can apply online through Eastern Bank PLC's official Online Apply page:\n\n"
        "https://www.ebl.com.bd/onlineapply\n\n"
        "You can use this page for online applications such as:\n"
        "- Card application\n"
        "- Account opening\n"
        "- Loan application\n"
        "- Other available EBL services\n\n"
        "Please apply only through the official EBL website."
    )


def get_urgent_card_reply():
    return (
        "This may be an urgent banking security issue.\n\n"
        "Please contact Eastern Bank PLC immediately:\n"
        "- Hotline: 16230\n"
        "- From overseas: +8809677716230\n"
        "- General contact number: +8809666777325\n"
        "- Email: info@ebl-bd.com\n\n"
        "For your safety, do not share OTP, PIN, password, CVV, or full card number. "
        "If needed, I can also help you create a complaint record for this issue."
    )


def get_complaint_start_reply():
    return (
        "I can help create a complaint record for this issue.\n\n"
        "Please provide the following safe details:\n"
        "- Issue type\n"
        "- Transaction date, if applicable\n"
        "- Approximate amount, if applicable\n"
        "- Short description of the issue\n"
        "- Last 4 digits only, if card-related\n\n"
        "Do not share OTP, PIN, password, CVV, or full card number."
    )
