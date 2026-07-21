def is_complaint_memory_question(message):
    message = message.lower()

    complaint_words = [
        "complaint",
        "complain",
        "complaint id",
        "issue i created",
        "case i created",
    ]

    memory_words = [
        "before",
        "earlier",
        "previous",
        "last",
        "created",
        "made",
        "submitted",
    ]

    has_complaint_word = any(word in message for word in complaint_words)
    has_memory_word = any(word in message for word in memory_words)

    return has_complaint_word and has_memory_word


def is_first_memory_question(message):
    message = message.lower()

    first_memory_phrases = [
        "first text",
        "first message",
        "first question",
        "oldest message",
        "oldest question",
        "what did i ask first",
        "what did i first ask",
    ]

    return any(phrase in message for phrase in first_memory_phrases)


def build_first_memory_reply(message):
    if not message:
        return (
            "I do not have any earlier saved messages in this session yet."
        )

    return f"Your first message in this session was: {message['message']}"


def build_recent_memory_reply(messages):
    if not messages:
        return (
            "I do not have any earlier saved messages in this session yet."
        )

    reply = "Here are your recent questions from this session:\n\n"

    for index, item in enumerate(messages, start=1):
        reply += f"{index}. {item['message']}\n"

    return reply.strip()


def build_latest_complaint_memory_reply(complaint):
    if not complaint:
        return (
            "I could not find any complaint created in this session yet."
        )

    return (
        "Here is the latest complaint I found in this session:\n\n"
        f"Complaint ID: {complaint['complaint_id']}\n"
        f"Issue Type: {complaint['issue_type']}\n"
        f"Status: {complaint['status']}\n"
        f"Description: {complaint['description']}\n"
        f"Created At: {complaint['created_at']}\n"
        f"Last Updated: {complaint['updated_at']}"
    )
