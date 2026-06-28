"""Backend entrypoint."""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from schemas import (
    ChatRequest,
    ChatResponse,
    ComplaintStatusUpdateRequest,
)

from safety import contains_sensitive_data, get_safety_response

from groq_client import (
    generate_groq_customer_service_reply,
    update_conversation_summary,
)

from database import (
    save_chat,
    get_chat_history,
    get_website_information,
    get_website_information_by_page_names,
    save_website_text,
    clear_website_information,
    get_session_summary,
    save_session_summary,
    save_complaint,
    get_complaint_by_id,
    update_complaint_status,
    get_recent_user_messages,
    get_latest_complaint_by_session,
)

from website_scraper import get_text_from_website

from topic_guard import (
    is_allowed_question,
    get_off_topic_reply,
    is_greeting_only,
    get_greeting_reply,
)

from intent_router import detect_intent

from agent_actions import (
    get_contact_reply,
    get_online_apply_reply,
    get_urgent_card_reply,
    get_complaint_start_reply,
)

from complaint_manager import (
    has_enough_complaint_details,
    get_issue_type,
    build_complaint_created_reply,
    extract_complaint_id,
    build_complaint_status_reply,
    build_complaint_not_found_reply,
    build_missing_complaint_id_reply,
)

from knowledge_router import select_knowledge_pages

from memory_recall import (
    is_complaint_memory_question,
    build_recent_memory_reply,
    build_latest_complaint_memory_reply,
)

from response_cleaner import clean_bank_contact_information


ERROR_REPLY = "Sorry, I could not process that request right now. Please try again later."


def limit_text(text, max_characters):
    if not text:
        return ""

    if len(text) <= max_characters:
        return text

    return text[:max_characters]


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


def build_response(reply, source, blocked=False):
    return ChatResponse(
        reply=reply,
        source=source,
        blocked=blocked,
    )


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

    intent = detect_intent(user_message)

    if intent == "contact_information":
        return save_and_build_response(
            session_id=session_id,
            user_message=user_message,
            reply=get_contact_reply(user_message),
            source="contact-agent",
            status="answered",
        )

    if intent == "online_apply":
        return save_and_build_response(
            session_id=session_id,
            user_message=user_message,
            reply=get_online_apply_reply(user_message),
            source="online-apply-agent",
            status="answered",
        )

    if intent == "urgent_card_issue":
        return save_and_build_response(
            session_id=session_id,
            user_message=user_message,
            reply=get_urgent_card_reply(),
            source="urgent-escalation-agent",
            status="urgent",
        )

    if intent == "complaint_create":
        if not has_enough_complaint_details(user_message):
            return save_and_build_response(
                session_id=session_id,
                user_message=user_message,
                reply=get_complaint_start_reply(),
                source="complaint-agent",
                status="collecting_complaint_details",
            )

        issue_type = get_issue_type(user_message)

        complaint = save_complaint(
            session_id=session_id,
            issue_type=issue_type,
            description=user_message,
        )

        complaint_reply = build_complaint_created_reply(complaint)

        return save_and_build_response(
            session_id=session_id,
            user_message=user_message,
            reply=complaint_reply,
            source="complaint-agent",
            status="complaint_created",
        )

    if intent == "complaint_status":
        complaint_id = extract_complaint_id(user_message)

        if not complaint_id:
            return save_and_build_response(
                session_id=session_id,
                user_message=user_message,
                reply=build_missing_complaint_id_reply(),
                source="complaint-status-agent",
                status="missing_complaint_id",
            )

        complaint = get_complaint_by_id(complaint_id)

        if not complaint:
            return save_and_build_response(
                session_id=session_id,
                user_message=user_message,
                reply=build_complaint_not_found_reply(complaint_id),
                source="complaint-status-agent",
                status="complaint_not_found",
            )

        status_reply = build_complaint_status_reply(complaint)

        return save_and_build_response(
            session_id=session_id,
            user_message=user_message,
            reply=status_reply,
            source="complaint-status-agent",
            status="complaint_status_found",
        )

    if intent == "memory_question":
        if is_complaint_memory_question(user_message):
            latest_complaint = get_latest_complaint_by_session(session_id)
            memory_reply = build_latest_complaint_memory_reply(latest_complaint)
        else:
            recent_messages = get_recent_user_messages(session_id, limit=5)
            memory_reply = build_recent_memory_reply(recent_messages)

        return save_and_build_response(
            session_id=session_id,
            user_message=user_message,
            reply=memory_reply,
            source="memory-recall-agent",
            status="memory_recalled",
        )

    history = get_chat_history(session_id, limit=10)
    has_previous_history = len(history) > 0

    if intent == "off_topic" and not is_allowed_question(user_message, has_previous_history):
        return save_and_build_response(
            session_id=session_id,
            user_message=user_message,
            reply=get_off_topic_reply(),
            source="topic-guard",
            status="off_topic",
        )

    selected_pages = select_knowledge_pages(intent)

    website_info = limit_text(
        get_website_information_by_page_names(selected_pages),
        12000,
    )

    if not website_info:
        website_info = limit_text(get_website_information(), 12000)

    session_summary = limit_text(get_session_summary(session_id), 2000)

    try:
        reply = generate_groq_customer_service_reply(
            user_message,
            history,
            website_info,
            session_summary,
        )

    except Exception as error:
        print("GROQ ERROR:", error)

        return save_and_build_response(
            session_id=session_id,
            user_message=user_message,
            reply=ERROR_REPLY,
            source="system-error",
            status="error",
        )

    reply = clean_bank_contact_information(reply)

    response = save_and_build_response(
        session_id=session_id,
        user_message=user_message,
        reply=reply,
        source="groq-llm",
        status="answered",
    )

    update_summary_safely(
        session_id=session_id,
        session_summary=session_summary,
        user_message=user_message,
        reply=reply,
    )

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
                page_text=page_text,
            )

            saved_pages.append({
                "page_name": page["page_name"],
                "page_url": page["page_url"],
                "characters_saved": len(page_text),
            })

        except Exception as error:
            failed_pages.append({
                "page_name": page["page_name"],
                "page_url": page["page_url"],
                "error": str(error),
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
        page_text=verified_contact_text,
    )

    saved_pages.append({
        "page_name": "EBL Verified Contact Information",
        "page_url": "https://www.ebl.com.bd/contact",
        "characters_saved": len(verified_contact_text),
    })

    return {
        "message": "Website information refresh completed",
        "saved_pages": saved_pages,
        "failed_pages": failed_pages,
    }


@app.patch("/admin/complaints/{complaint_id}/status")
def admin_update_complaint_status(
    complaint_id: str,
    request: ComplaintStatusUpdateRequest,
):
    allowed_statuses = [
        "Pending",
        "In Progress",
        "Resolved",
        "Rejected",
    ]

    requested_status = request.status.strip()
    normalized_status = None

    for status in allowed_statuses:
        if requested_status.lower() == status.lower():
            normalized_status = status
            break

    if not normalized_status:
        raise HTTPException(
            status_code=400,
            detail="Invalid status. Allowed statuses are: Pending, In Progress, Resolved, Rejected.",
        )

    updated_complaint = update_complaint_status(
        complaint_id=complaint_id.upper(),
        new_status=normalized_status,
    )

    if not updated_complaint:
        raise HTTPException(
            status_code=404,
            detail="Complaint not found.",
        )

    return {
        "message": "Complaint status updated successfully",
        "complaint": updated_complaint,
    }