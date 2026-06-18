MIN_CARD_DIGITS = 13
MAX_CARD_DIGITS = 19
PUNCTUATION = [":", "=", ".", ",", "?", "!", "-", "_", "/", "\\"]

SAFETY_RESPONSE = (
    "For your security, please do not share OTP, PIN, password, CVV, "
    "full card number or other sensitive banking details. "
    "For account-specific help, please contact official Eastern Bank PLC support "
    "or visit your nearest branch."
)


def contains_sensitive_data(message: str) -> bool:
    """Return True if the user's message contains sensitive banking data."""

    if not message:
        return False

    text = clean_text(message)

    if has_number_after(text, "otp", 4, 8):
        return True
    if has_number_after(text, "pin", 4, 8):
        return True
    if has_number_after(text, "cvv", 3, 4):
        return True
    if has_text_after(text, "password"):
        return True
    if has_text_after(text, "passcode"):
        return True

    if has_card_number(text):
        return True

    return False


def has_number_after(text: str, word: str, min_digits: int, max_digits: int) -> bool:
    digits = only_digits(text_after(text, word))

    return min_digits <= len(digits) <= max_digits


def has_text_after(text: str, word: str) -> bool:
    return text_after(text, word).strip() != ""


def has_card_number(text: str) -> bool:
    digits = only_digits(text)

    return MIN_CARD_DIGITS <= len(digits) <= MAX_CARD_DIGITS


def text_after(text: str, word: str) -> str:
    search_word = f" {word} "

    if search_word not in text:
        return ""

    return text.split(search_word, 1)[1]


def clean_text(text: str) -> str:
    text = text.lower()

    for symbol in PUNCTUATION:
        text = text.replace(symbol, " ")

    return f" {text} "


def only_digits(text: str) -> str:
    return "".join(character for character in text if character.isdigit())


def get_safety_response() -> str:
    return SAFETY_RESPONSE
