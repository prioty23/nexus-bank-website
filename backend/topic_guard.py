BANKING_KEYWORDS = [
    "account", "savings", "current", "deposit", "fixed deposit",
    "loan", "card", "credit card", "debit card", "prepaid card",
    "transaction", "payment", "refund", "charge", "deducted",
    "atm", "branch", "bank", "banking",
    "mobile banking", "internet banking", "digital banking",
    "support", "hotline", "customer service", "contact",
    "email", "mail", "phone", "number", "call center", "helpline",
    "complaint", "issue", "problem",
    "statement", "balance", "kyc", "documents",
    "nominee", "nid", "passport", "tin",
    "customer support",
    "islamic", "shariah", "sharia", "mudarabah", "wadiah",
    "profit distribution",
    "feature", "features", "benefit", "benefits",
    "student banking", "student account", "campus account",
    "junior savings", "student file", "child future",
    "aspire scheme", "little star",
]

CONTACT_WORDS = [
    "contact", "email", "mail", "phone", "number",
    "hotline", "call center", "helpline", "customer support",
]


FOLLOW_UP_WORDS = [
    "what documents", "documents required", "tell me more",
    "explain that", "what about", "which one",
    "how much", "how long", "why", "feature", "features",
    "benefit", "benefits",
    "that", "this", "it", "those", "them"
]


GREETING_WORDS = [
    "hi", "hello", "hey", "good morning", "good afternoon",
    "good evening", "assalamualaikum", "salam"
]


def is_greeting_only(message):
    message = message.lower().strip()

    for greeting in GREETING_WORDS:
        if message == greeting:
            return True

    return False


def get_greeting_reply():
    return (
        "Hello! Welcome to Eastern Bank AI Assistant. How may I assist you today?"
    )


def is_contact_question(message):
    message = message.lower()

    for word in CONTACT_WORDS:
        if word in message:
            return True

    return False


def is_banking_related(message):
    message = message.lower()

    for keyword in BANKING_KEYWORDS:
        if keyword in message:
            return True

    return False


def is_follow_up(message):
    message = message.lower()

    for word in FOLLOW_UP_WORDS:
        if word in message:
            return True

    return False


def is_allowed_question(message, has_previous_history):
    if is_greeting_only(message):
        return True

    if is_contact_question(message):
        return True

    if is_banking_related(message):
        return True

    if has_previous_history and is_follow_up(message):
        return True

    return False


def get_off_topic_reply():
    return (
        "This question is not related to banking or the current conversation. "
        "I can help with accounts, cards, loans, deposits, digital banking, "
        "transactions, complaints, or customer support."
    )
