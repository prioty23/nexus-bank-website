import re


def clean_bank_contact_information(reply):
    if not reply:
        return reply

    reply = clean_reply_text(reply)
    reply = clean_missing_info_phrases(reply)
    reply = clean_unwanted_intro_phrases(reply)
    reply = clean_fee_or_charge_reply_format(reply)

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


def clean_unwanted_intro_phrases(reply):
    cleaned_reply = clean_schedule_of_charges_intro(reply)

    unwanted_intro_phrases = [
        "According to our website, ",
        "According to the website, ",
        "According to the EBL website, ",
        "According to Eastern Bank PLC's website, ",
    ]

    for phrase in unwanted_intro_phrases:
        if cleaned_reply.lower().startswith(phrase.lower()):
            cleaned_reply = cleaned_reply[len(phrase):]
            break

    return cleaned_reply


def clean_schedule_of_charges_intro(reply):
    match = re.match(
        r"(?is)^according to (?:the )?(?:eastern bank plc )?"
        r"(?:retail banking )?schedule of charges,?\s*"
        r"(?:the\s+)?(.+?)\s+(?:are|is):\s*",
        reply,
    )

    if match:
        title = match.group(1).strip()
        title = remove_leading_the(title)
        title = uppercase_first_character(title)
        body = reply[match.end():].lstrip()

        return f"{title}:\n\n{body}"

    cleaned_reply = re.sub(
        r"(?is)^according to (?:the )?(?:eastern bank plc )?"
        r"(?:retail banking )?schedule of charges,?\s*",
        "",
        reply,
        count=1,
    )

    return cleaned_reply


def remove_leading_the(text):
    if text.lower().startswith("the "):
        return text[4:].strip()

    return text


def uppercase_first_character(text):
    if not text:
        return text

    return text[0].upper() + text[1:]


def clean_fee_or_charge_reply_format(reply):
    if not looks_like_fee_or_charge_reply(reply):
        return reply

    formatted_lines = []

    for line in reply.splitlines():
        stripped_line = line.strip()

        if not stripped_line:
            if formatted_lines and formatted_lines[-1] != "":
                formatted_lines.append("")

            continue

        line_without_marker = stripped_line.lstrip("> ").strip()

        if should_format_as_charge_bullet(line_without_marker):
            line_without_marker = line_without_marker.replace(" - ", ": ", 1)
            formatted_lines.append(f"- {line_without_marker}")
            continue

        formatted_lines.append(stripped_line)

    return "\n".join(formatted_lines).strip()


def looks_like_fee_or_charge_reply(reply):
    lower_reply = reply.lower()

    return (
        "fee" in lower_reply
        or "fees" in lower_reply
        or "charge" in lower_reply
        or "charges" in lower_reply
        or "schedule of charges" in lower_reply
        or "clearing" in lower_reply
        or "ফি" in reply
        or "চার্জ" in reply
        or "৳" in reply
    )


def should_format_as_charge_bullet(line):
    if line.startswith("- "):
        return False

    lower_line = line.lower()
    has_row_separator = " - " in line
    has_money_or_condition = (
        "৳" in line
        or "%" in line
        or "bdt" in lower_line
        or "tk " in lower_line
        or "free" in lower_line
        or "ফ্রি" in line
        or "প্রকৃত খরচ" in line
    )
    has_fee_word = (
        "fee" in lower_line
        or "charge" in lower_line
        or "commission" in lower_line
        or "ফি" in line
        or "চার্জ" in line
    )

    return has_row_separator and (has_money_or_condition or has_fee_word)


def clean_missing_info_phrases(reply):
    replacement = (
        "Please specify the exact EBL product or service so I can provide "
        "the most relevant available information."
    )

    wrong_missing_info_phrases = [
        "Detailed information is not available in the current EBL website data.",
        "Detailed information is not available in the current EBL website data",
        "Detailed information is not available.",
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
