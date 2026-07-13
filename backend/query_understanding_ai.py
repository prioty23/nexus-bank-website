import json
import os

from dotenv import load_dotenv
from groq import Groq

from intent_router import detect_intent


load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")

ALLOWED_INTENTS = [
    "greeting",
    "account_information",
    "card_information",
    "loan_information",
    "deposit_information",
    "digital_banking",
    "branch_locator",
    "charge_information",
    "contact_information",
    "online_apply",
    "complaint_create",
    "complaint_status",
    "off_topic",
    "general_information",
]

SYSTEM_PROMPT = """
You are only a query understanding engine for Eastern Bank PLC chatbot.
Your job is to classify the user message and rewrite it into a clean English search query for searching EBL website database.
Do not answer the customer.
Do not use general banking knowledge.
Return only valid JSON.
No markdown.
No explanation.

Allowed intent values:
- greeting
- account_information
- card_information
- loan_information
- deposit_information
- digital_banking
- branch_locator
- charge_information
- contact_information
- online_apply
- complaint_create
- complaint_status
- off_topic
- general_information

The JSON must contain exactly these keys:
intent
search_query
language

Language should be a short label such as english, banglish, bangla, broken_english, or unknown.
The search_query should be clean English terms useful for searching Eastern Bank PLC website content.

Intent guidance:
- Use account_information for broad account opening questions, including messages like "Open an Account", "account khulte ki lagbe", "ami ebl account korte chai", and "how can I open an account".
- Do not classify broad account opening questions as online_apply.
- Use online_apply only when the customer explicitly asks for an online application link, application form, apply link, or apply online page.
"""


def build_fallback_understanding(message):
    fallback_intent = detect_intent(message)

    return {
        "intent": fallback_intent,
        "search_query": message,
        "language": "unknown",
    }


def parse_groq_json(content):
    if not content:
        raise ValueError("Groq returned an empty response")

    parsed = json.loads(content.strip())

    if not isinstance(parsed, dict):
        raise ValueError("Groq response JSON is not an object")

    intent = str(parsed.get("intent", "")).strip()
    search_query = str(parsed.get("search_query", "")).strip()
    language = str(parsed.get("language", "")).strip() or "unknown"

    if intent not in ALLOWED_INTENTS:
        raise ValueError("Groq returned an unsupported intent")

    if not search_query:
        raise ValueError("Groq returned an empty search query")

    return {
        "intent": intent,
        "search_query": search_query,
        "language": language,
    }


def should_force_account_information(message, understood_query):
    if understood_query.get("intent") != "online_apply":
        return False

    normalized_message = " ".join(message.lower().split())

    explicit_online_apply_phrases = [
        "apply online",
        "online apply",
        "online application",
        "application link",
        "apply link",
        "online form",
        "apply now",
    ]

    if any(phrase in normalized_message for phrase in explicit_online_apply_phrases):
        return False

    broad_account_phrases = [
        "open an account",
        "open account",
        "account opening",
        "create account",
        "new account",
        "account khulte",
        "account khola",
        "account korte",
    ]

    return any(phrase in normalized_message for phrase in broad_account_phrases)


def normalize_understood_query(message, understood_query):
    if should_force_account_information(message, understood_query):
        understood_query = dict(understood_query)
        understood_query["intent"] = "account_information"
        understood_query["search_query"] = (
            "EBL account opening requirements account types savings current deposit online application"
        )

    return understood_query


def understand_user_query_with_groq(message):
    if not GROQ_API_KEY:
        return build_fallback_understanding(message)

    try:
        client = Groq(api_key=GROQ_API_KEY)

        chat_completion = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": SYSTEM_PROMPT,
                },
                {
                    "role": "user",
                    "content": message,
                },
            ],
            temperature=0,
            max_completion_tokens=250,
        )

        content = chat_completion.choices[0].message.content
        understood_query = parse_groq_json(content)
        return normalize_understood_query(message, understood_query)

    except Exception as error:
        print("QUERY UNDERSTANDING ERROR:", repr(error))
        return build_fallback_understanding(message)
