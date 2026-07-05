import re


def has_enough_complaint_details(message):
    message = message.lower().strip()

    if len(message.split()) < 5:
        return False

    complaint_keywords = [
        "failed", "deducted", "charged", "twice", "double",
        "atm", "cash", "refund", "transaction", "payment",
        "card", "account", "loan", "deposit", "unauthorized"
    ]

    for keyword in complaint_keywords:
        if keyword in message:
            return True

    return False


def get_issue_type(message):
    message = message.lower()

    if "atm" in message or "cash" in message:
        return "ATM Issue"

    if "card" in message or "charged" in message or "unauthorized" in message:
        return "Card Issue"

    if "transaction" in message or "payment" in message or "deducted" in message:
        return "Transaction Issue"

    if "loan" in message:
        return "Loan Issue"

    if "account" in message:
        return "Account Issue"

    if "deposit" in message:
        return "Deposit Issue"

    return "General Complaint"


def build_complaint_created_reply(complaint):
    return (
        "Your complaint has been created successfully.\n\n"
        f"Complaint ID: {complaint['complaint_id']}\n"
        f"Issue Type: {complaint['issue_type']}\n"
        f"Status: {complaint['status']}\n"
        f"Created At: {complaint['created_at']}\n\n"
        "Please save your complaint ID for future status checking. "
        "Do not share OTP, PIN, password, CVV, or full card number."
    )


def extract_complaint_id(message):
    match = re.search(r"CMP-\d{8}-\d{4}", message.upper())

    if match:
        return match.group(0)

    return None


def build_complaint_status_reply(complaint):
    return (
        "Complaint status found.\n\n"
        f"Complaint ID: {complaint['complaint_id']}\n"
        f"Issue Type: {complaint['issue_type']}\n"
        f"Status: {complaint['status']}\n"
        f"Created At: {complaint['created_at']}\n"
        f"Last Updated: {complaint['updated_at']}"
    )


def build_complaint_not_found_reply(complaint_id):
    return (
        f"I could not find any complaint with this ID: {complaint_id}\n\n"
        "Please check the complaint ID and try again."
    )


def build_missing_complaint_id_reply():
    return (
        "Please provide your complaint ID to check the status.\n\n"
        "Example: CMP-20260628-0001"
    )


def is_complaint_confirmation_yes(message):
    message = message.lower().strip()

    yes_exact_words = [
        "yes",
        "ok",
        "okay",
        "sure",
        "create",
        "submit",
        "do it",
    ]

    yes_phrases = [
        "yes create",
        "yes please",
        "create complaint",
        "submit complaint",
        "ok create",
        "okay create",
        "please create",
        "create it",
        "please submit",
    ]

    if message in yes_exact_words:
        return True

    for phrase in yes_phrases:
        if phrase in message:
            return True

    return False


def is_complaint_confirmation_no(message):
    message = message.lower().strip()

    no_exact_words = [
        "no",
        "cancel",
        "stop",
        "later",
    ]

    no_phrases = [
        "not now",
        "do not create",
        "don't create",
        "dont create",
        "no need",
        "cancel it",
        "stop it",
        "create later",
    ]

    if message in no_exact_words:
        return True

    for phrase in no_phrases:
        if phrase in message:
            return True

    return False


def build_complaint_confirmation_reply(issue_type):
    return (
        "I can create a complaint record for this issue.\n\n"
        "Do you want me to create the complaint record now?\n"
        "Please reply with Yes to create or No to cancel.\n\n"
        "For your safety, do not share OTP, PIN, password, CVV, or full card number."
    )


def build_complaint_cancelled_reply():
    return (
        "Okay, I will not create a complaint record now.\n\n"
        "If you want to create it later, please describe the issue again and confirm that you want to create a complaint."
    )
