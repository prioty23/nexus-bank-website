import re

SENSITIVE_PATTERNS = [
    r"\botp\b.*\d{4,8}",  # OTP followed by 4-8 digits
    r"\bpin\b.*\d{4,8}",  # PIN followed by 4-8 digits
    r"\bcvv\b.*\d{4,8}",  # CVV followed by 4-8 digits
    r"\bpassword\b.*\s*(is|:|=)\s*\S+",  # Password followed by any non-whitespace characters
    r"\bpasscode\b.*\s*(is|:|=)\s*\S+",  # Passcode followed by any non-whitespace characters
    r"\bdebit card\b.*\d{12,19}",       # Debit card followed by 12-19 digits
    r"\bcredit card\b.*\d{12,19}",     # Credit card followed by 12-19 digits
    r"\baccount password\b",        # Account password (without specific value)
]


def contains_sensitive_data(message: str) -> bool:
    """
    Returns True if the user's message appears to contain sensitive banking data.
    """

    if not message:
        return False

    normalized_message = message.lower()

    for pattern in SENSITIVE_PATTERNS:
        if re.search(pattern, normalized_message):
            return True

    # Detect long card-like numbers, including spaces or dashes
    digits_only = re.sub(r"\D", "", message)

    if len(digits_only) >= 13 and len(digits_only) <= 19:
        return True

    return False


def get_safety_response() -> str:
    return (
        "For your security, please do not share OTP, PIN, password, CVV, "
        "full card number, or other sensitive banking details. "
        "For account-specific help, please contact official Nexus Bank support "
        "or visit your nearest branch."
    )