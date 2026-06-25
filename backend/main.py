"""Backend entrypoint."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from schemas import ChatRequest, ChatResponse
from safety import contains_sensitive_data, get_safety_response

from groq_client import (
    generate_groq_customer_service_reply,
    update_conversation_summary,
)

from database import (
    save_chat,
    get_chat_history,
    get_website_information,
    save_website_text,
    clear_website_information,
    get_session_summary,
    save_session_summary,
)

from website_scraper import get_text_from_website

from topic_guard import (
    is_allowed_question,
    get_off_topic_reply,
    is_greeting_only,
    get_greeting_reply,
)


ERROR_REPLY = "Sorry, I could not process that request right now. Please try again later."
CONTACT_EMAIL = "info@ebl-bd.com"
CONTACT_HOTLINE = "16230"
CONTACT_OVERSEAS = "+8809677716230"
CONTACT_NUMBER = "+8809666777325"
CONTACT_WORDS = [
    "email",
    "mail",
    "hotline",
    "phone",
    "number",
    "contact",
    "customer support",
    "customer service",
    "call center",
    "helpline",
]
WEBSITE_PAGES = [
    {
        "page_name": "EBL Home Page",
        "page_url": "https://www.ebl.com.bd/",
    },
    {
        "page_name": "EBL Cards Page",
        "page_url": "https://www.ebl.com.bd/retail/EBL-Cards",
    },
    {
        "page_name": "EBL Retail Loan Page",
        "page_url": "https://www.ebl.com.bd/retail/retail-loan",
    },
    {
        "page_name": "EBL SME Loan Page",
        "page_url": "https://www.ebl.com.bd/sme/sme-loans",
    },
    {
        "page_name": "EBL Retail Deposits Page",
        "page_url": "https://www.ebl.com.bd/retail/retail-deposit",
    },
    {
        "page_name": "EBL SME Deposits Page",
        "page_url": "https://www.ebl.com.bd/sme/sme-deposits",
    },
    {
        "page_name": "EBL Digital Banking Page",
        "page_url": "https://www.ebl.com.bd/retail-digital/ebl-skybanking",
    },
    {
        "page_name": "EBL Contact Page",
        "page_url": "https://www.ebl.com.bd/contact",
    },
    {
        "page_name": "EBL Locator Page",
        "page_url": "https://www.ebl.com.bd/locator/",
    },
]


def is_direct_contact_question(message):
    message = message.lower()

    for word in CONTACT_WORDS:
        if word in message:
            return True

    return False


def get_direct_contact_reply(message):
    message = message.lower()

    if "email" in message or "mail" in message:
        return CONTACT_EMAIL

    if "hotline" in message:
        return CONTACT_HOTLINE

    if "phone" in message or "number" in message or "call center" in message or "helpline" in message:
        return (
            f"Hotline: {CONTACT_HOTLINE}\n"
            f"From overseas: {CONTACT_OVERSEAS}\n"
            f"General contact number: {CONTACT_NUMBER}"
        )

    if "contact" in message or "customer support" in message or "customer service" in message:
        return (
            f"Email: {CONTACT_EMAIL}\n"
            f"Hotline: {CONTACT_HOTLINE}\n"
            f"From overseas: {CONTACT_OVERSEAS}\n"
            f"General contact number: {CONTACT_NUMBER}"
        )

    return (
        f"Email: {CONTACT_EMAIL}\n"
        f"Hotline: {CONTACT_HOTLINE}"
    )


def build_response(reply, source, blocked=False):
    return ChatResponse(reply=reply, source=source, blocked=blocked)


def save_and_build_response(
    session_id,
    user_message,
    reply,
    source,
    status,
    blocked=False,
):
    save_chat(
        session_id=session_id,
        user_message=user_message,
        bot_reply=reply,
        source=source,
        blocked=blocked,
        status=status,
    )

    return build_response(reply, source, blocked)


def update_summary_safely(session_id, session_summary, user_message, reply):
    try:
        new_summary = update_conversation_summary(
            session_summary,
            user_message,
            reply,
        )
        save_session_summary(session_id, new_summary)
    except Exception:
        pass


app = FastAPI(
    title="Eastern Bank AI Chatbot API",
    description="FastAPI backend for Eastern Bank AI chatbot",
    version="1.0.0",
)


origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {
        "message": "Eastern AI Chatbot API is running"
    }


@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "service": "eastern-bank-plc-chatbot-backend"
    }


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    user_message = request.message.strip()
    session_id = request.session_id or "default-session"

    if contains_sensitive_data(user_message):
        return save_and_build_response(
            session_id=session_id,
            user_message=user_message,
            reply=get_safety_response(),
            source="safety-filter",
            status="blocked",
            blocked=True,
        )

    if is_greeting_only(user_message):
        return save_and_build_response(
            session_id=session_id,
            user_message=user_message,
            reply=get_greeting_reply(),
            source="greeting-handler",
            status="greeting",
        )

    if is_direct_contact_question(user_message):
        return save_and_build_response(
            session_id=session_id,
            user_message=user_message,
            reply=get_direct_contact_reply(user_message),
            source="verified-contact",
            status="answered",
        )

    history = get_chat_history(session_id, limit=10)
    if not is_allowed_question(user_message, len(history) > 0):
        return save_and_build_response(
            session_id=session_id,
            user_message=user_message,
            reply=get_off_topic_reply(),
            source="topic-guard",
            status="off_topic",
        )

    website_info = get_website_information()
    session_summary = get_session_summary(session_id)

    try:
        reply = generate_groq_customer_service_reply(
            user_message,
            history,
            website_info,
            session_summary
        )
    except Exception:
        return save_and_build_response(
            session_id=session_id,
            user_message=user_message,
            reply=ERROR_REPLY,
            source="system-error",
            status="error",
        )

    response = save_and_build_response(
        session_id=session_id,
        user_message=user_message,
        reply=reply,
        source="groq-llm",
        status="answered",
    )
    update_summary_safely(session_id, session_summary, user_message, reply)
    return response


@app.post("/refresh-website-info")
def refresh_website_info():
    clear_website_information()

    saved_pages = []
    failed_pages = []

    for page in WEBSITE_PAGES:
        try:
            page_text = get_text_from_website(page["page_url"])

            save_website_text(
                page_name=page["page_name"],
                page_url=page["page_url"],
                page_text=page_text
            )

            saved_pages.append({
                "page_name": page["page_name"],
                "page_url": page["page_url"],
                "characters_saved": len(page_text)
            })

        except Exception as error:
            failed_pages.append({
                "page_name": page["page_name"],
                "page_url": page["page_url"],
                "error": str(error)
            })

    verified_contact_text = """
Eastern Bank PLC official contact information:

General email: info@ebl-bd.com
Hotline: 16230
From overseas: +8809677716230
General contact number: +8809666777325

Source: Eastern Bank PLC official contact page.
"""

    save_website_text(
        page_name="EBL Verified Contact Information",
        page_url="https://www.ebl.com.bd/contact",
        page_text=verified_contact_text
    )

    saved_pages.append({
        "page_name": "EBL Verified Contact Information",
        "page_url": "https://www.ebl.com.bd/contact",
        "characters_saved": len(verified_contact_text)
    })

    return {
        "message": "Website information refresh completed",
        "saved_pages": saved_pages,
        "failed_pages": failed_pages
    }
