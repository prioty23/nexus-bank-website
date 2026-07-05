def clean_bank_contact_information(reply):
    if not reply:
        return reply

    reply = clean_reply_text(reply)
    reply = clean_missing_info_phrases(reply)

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


def clean_missing_info_phrases(reply):
    replacement = (
        "Please specify the exact EBL product or service so I can provide "
        "the most relevant available information."
    )

    wrong_missing_info_phrases = [
        "Detailed information is not available in the current EBL website data.",
        "Detailed information is not available in the current EBL website data",
    ]

    cleaned_reply = reply

    for phrase in wrong_missing_info_phrases:
        cleaned_reply = cleaned_reply.replace(phrase, replacement)

    return cleaned_reply


def clean_reply_text(reply):
    replacements = {
        "\u2018": "'",
        "\u2019": "'",
        "\u201c": '"',
        "\u201d": '"',
        "\u2013": "-",
        "\u2014": "-",
        "\u2022": "-",
        "\ufffd": "'",
    }

    cleaned_reply = reply

    for old_value, new_value in replacements.items():
        cleaned_reply = cleaned_reply.replace(old_value, new_value)

    return cleaned_reply
