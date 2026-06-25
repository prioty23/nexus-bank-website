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
    session_id = request.session_id

    # Safety check
    if contains_sensitive_data(user_message):
        safety_reply = get_safety_response()

        save_chat(
            session_id=session_id,
            user_message=user_message,
            bot_reply=safety_reply,
            source="safety-filter",
            blocked=True,
            status="blocked"
        )

        return ChatResponse(
            reply=safety_reply,
            source="safety-filter",
            blocked=True
        )

    # Greeting check
    if is_greeting_only(user_message):
        greeting_reply = get_greeting_reply()

        save_chat(
            session_id=session_id,
            user_message=user_message,
            bot_reply=greeting_reply,
            source="greeting-handler",
            blocked=False,
            status="greeting"
        )

        return ChatResponse(
            reply=greeting_reply,
            source="greeting-handler",
            blocked=False
        )

    # Recent chat history
    history = get_chat_history(session_id, limit=10)
    has_previous_history = len(history) > 0

    # Off-topic check
    if not is_allowed_question(user_message, has_previous_history):
        off_topic_reply = get_off_topic_reply()

        save_chat(
            session_id=session_id,
            user_message=user_message,
            bot_reply=off_topic_reply,
            source="topic-guard",
            blocked=False,
            status="off_topic"
        )

        return ChatResponse(
            reply=off_topic_reply,
            source="topic-guard",
            blocked=False
        )

    # Website info and long memory
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
        save_chat(
            session_id=session_id,
            user_message=user_message,
            bot_reply=ERROR_REPLY,
            source="system-error",
            blocked=False,
            status="error"
        )

        return ChatResponse(
            reply=ERROR_REPLY,
            source="system-error",
            blocked=False
        )

    save_chat(
        session_id=session_id,
        user_message=user_message,
        bot_reply=reply,
        source="groq-llm",
        blocked=False,
        status="answered"
    )

    # Update long-term session summary
    try:
        new_summary = update_conversation_summary(
            session_summary,
            user_message,
            reply
        )

        save_session_summary(session_id, new_summary)

    except Exception:
        pass

    return ChatResponse(
        reply=reply,
        source="groq-llm",
        blocked=False
    )


@app.post("/refresh-website-info")
def refresh_website_info():
    pages = [
        {
            "page_name": "EBL Home Page",
            "page_url": "https://www.ebl.com.bd/"
        },
        {
            "page_name": "EBL Cards Page",
            "page_url": "https://www.ebl.com.bd/retail/EBL-Cards"
        },
        {
            "page_name": "EBL Retail Loan Page",
            "page_url": "https://www.ebl.com.bd/retail/retail-loan"
        },
        {
            "page_name": "EBL SME Loan Page",
            "page_url": "https://www.ebl.com.bd/sme/sme-loans"
        },
        {
            "page_name": "EBL Retail Deposits Page",
            "page_url": "https://www.ebl.com.bd/retail/retail-deposit"
        },
        {
            "page_name": "EBL SME Deposits Page",
            "page_url": "https://www.ebl.com.bd/sme/sme-deposits"
        },
        {
            "page_name": "EBL Digital Banking Page",
            "page_url": "https://www.ebl.com.bd/retail-digital/ebl-skybanking"
        },
        {
            "page_name": "EBL Contact Page",
            "page_url": "https://www.ebl.com.bd/contact"
        },
        {
            "page_name": "EBL Locator Page",
            "page_url": "https://www.ebl.com.bd/locator/"
        }
    ]

    clear_website_information()

    saved_pages = []
    failed_pages = []

    for page in pages:
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

    return {
        "message": "Website information refresh completed",
        "saved_pages": saved_pages,
        "failed_pages": failed_pages
    }