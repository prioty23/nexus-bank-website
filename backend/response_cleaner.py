def clean_bank_contact_information(reply):
    if not reply:
        return reply

    wrong_patterns = [
        "[email protected]",
        "email protected",
        "+88 09677716230",
        "09677716230",
    ]

    for pattern in wrong_patterns:
        if pattern.lower() in reply.lower():
            return (
                "Please contact Eastern Bank PLC customer service immediately:\n\n"
                "Hotline: 16230\n"
                "From overseas: +8809677716230\n"
                "General contact number: +8809666777325\n"
                "Email: info@ebl-bd.com"
            )

    return reply
