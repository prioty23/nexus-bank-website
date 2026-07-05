"""Backend entrypoint."""

from urllib.parse import urlparse

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
    search_website_information,
    save_pending_complaint,
    get_pending_complaint,
    delete_pending_complaint,
)

from website_scraper import get_internal_links_from_website, get_text_from_website

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
    is_complaint_confirmation_yes,
    is_complaint_confirmation_no,
    build_complaint_confirmation_reply,
    build_complaint_cancelled_reply,
)

from knowledge_router import select_knowledge_pages

from memory_recall import (
    is_complaint_memory_question,
    build_recent_memory_reply,
    build_latest_complaint_memory_reply,
)

from response_cleaner import clean_bank_contact_information


ERROR_REPLY = "Sorry, I could not process that request right now. Please try again later."
EBL_CONTEXT_LIMIT = 10000
SESSION_SUMMARY_LIMIT = 800


def limit_text(text, max_characters):
    if not text:
        return ""

    if len(text) <= max_characters:
        return text

    return text[:max_characters]


def is_document_question(message):
    message = message.lower()

    document_words = [
        "document",
        "documents",
        "required",
        "requirement",
        "requirements",
        "need",
        "needed",
    ]

    account_words = [
        "account",
        "savings",
        "saving",
        "current",
        "open",
        "opening",
    ]

    return contains_any_word(message, document_words) and contains_any_word(message, account_words)


def contains_any_word(message, words):
    for word in words:
        if word in message:
            return True

    return False


def is_broad_account_opening_question(message):
    message = message.lower()

    broad_phrases = [
        "how can i open an account",
        "how to open an account",
        "open an account",
        "open account",
        "account opening",
        "create account",
        "new account",
    ]

    return any(phrase in message for phrase in broad_phrases)


def clean_document_line(line):
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

    cleaned_line = line.strip()

    for old_value, new_value in replacements.items():
        cleaned_line = cleaned_line.replace(old_value, new_value)

    return cleaned_line


def extract_required_document_lines(website_info):
    if not website_info:
        return []

    lines = [
        clean_document_line(line)
        for line in website_info.splitlines()
    ]

    start_index = -1

    for index, line in enumerate(lines):
        lower_line = line.lower()

        if (
            lower_line == "required documents for account opening"
            or lower_line == "documents required to open account"
        ):
            start_index = index
            break

    if start_index < 0:
        return []

    stop_lines = [
        "quick apply",
        "ebl  self  service portal",
        "ebl self service portal",
        "existing customer",
        "new customer",
        "apply for",
        "preferred branch",
    ]

    document_lines = []

    for line in lines[start_index + 1:]:
        if not line:
            continue

        lower_line = line.lower()

        if lower_line.startswith("page:") or lower_line.startswith("url:"):
            break

        if lower_line in stop_lines:
            break

        if line in ["':", "' :"] and document_lines:
            document_lines[-1] = f"{document_lines[-1]}'" + ":"
            continue

        document_lines.append(line)

    return document_lines


def build_required_documents_reply(user_message, website_info):
    if not is_document_question(user_message):
        return ""

    document_lines = extract_required_document_lines(website_info)

    if not document_lines:
        return ""

    reply = "To open a savings account, the EBL website lists these required documents:\n\n"
    inside_group = False

    for line in document_lines:
        lower_line = line.lower()

        if (
            lower_line.startswith("applicants")
            or lower_line.startswith("nominees")
        ):
            reply += f"- {line}\n"
            inside_group = True
            continue

        if (
            lower_line.startswith("completed")
            or lower_line.startswith("during account opening")
        ):
            reply += f"- {line}\n"
            inside_group = False
            continue

        if inside_group:
            reply += f"  - {line}\n"
        else:
            reply += f"- {line}\n"

    return reply.strip()


DISCOVERY_SOURCES = [
    {
        "page_url": "https://www.ebl.com.bd/retail/EBL-Cards",
        "allowed_paths": [
            "/retail/eblcard/",
            "/islamic/eblcard/",
            "/ebl-virtual-prepaid-card",
        ],
    },
    {
        "page_url": "https://www.ebl.com.bd/retail/retail-loan",
        "allowed_paths": [
            "/retail-loan/",
        ],
    },
    {
        "page_url": "https://www.ebl.com.bd/sme/sme-loans",
        "allowed_paths": [
            "/sme-loan/",
            "/sme/sme-loan/",
        ],
    },
    {
        "page_url": "https://www.ebl.com.bd/retail/retail-deposit",
        "allowed_paths": [
            "/retail-deposit/",
        ],
    },
]

MAX_DISCOVERED_PAGES = 120


def is_allowed_discovered_url(url, allowed_paths):
    parsed_url = urlparse(url)
    path = parsed_url.path.lower()

    if not parsed_url.netloc.endswith("ebl.com.bd"):
        return False

    for allowed_path in allowed_paths:
        if path.startswith(allowed_path.lower()):
            return True

    return False


def build_discovered_page_name(link):
    link_text = link.get("text", "").strip()

    if link_text and link_text.lower() not in ["readmore", "read more", "apply now"]:
        return f"EBL Detail Page - {link_text}"

    path = urlparse(link["url"]).path.strip("/")
    slug = path.split("/")[-1]
    title = slug.replace("-", " ").replace("_", " ").strip()

    if not title:
        title = "Product Detail"

    return f"EBL Detail Page - {title.title()}"


def discover_website_pages():
    discovered_pages = []
    seen_urls = set(page["page_url"] for page in WEBSITE_PAGES)

    for source in DISCOVERY_SOURCES:
        links = get_internal_links_from_website(source["page_url"])

        for link in links:
            page_url = link["url"]

            if page_url in seen_urls:
                continue

            if not is_allowed_discovered_url(page_url, source["allowed_paths"]):
                continue

            seen_urls.add(page_url)
            discovered_pages.append({
                "page_name": build_discovered_page_name(link),
                "page_url": page_url,
            })

            if len(discovered_pages) >= MAX_DISCOVERED_PAGES:
                return discovered_pages

    return discovered_pages


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
        "page_name": "EBL Power Savings Page",
        "page_url": "https://www.ebl.com.bd/retail-deposit/EBL-Power-Savings",
    },
    {
        "page_name": "EBL Premium Savings Page",
        "page_url": "https://www.ebl.com.bd/retail-deposit/EBL-Premium-Savings",
    },
    {
        "page_name": "EBL 50+ Savings Page",
        "page_url": "https://www.ebl.com.bd/retail-deposit/EBL-50Plus-Savings",
    },
    {
        "page_name": "EBL Max Saver Page",
        "page_url": "https://www.ebl.com.bd/retail-deposit/EBL-Max-Saver",
    },
    {
        "page_name": "EBL Current Account Page",
        "page_url": "https://www.ebl.com.bd/retail-deposit/EBL-Current-Account",
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
    {
        "page_name": "EBL Online Apply Page",
        "page_url": "https://www.ebl.com.bd/onlineapply",
    },
    {
        "page_name": "EBL Forms and Downloads Page",
        "page_url": "https://www.ebl.com.bd/forms-downloads",
    },
    {
        "page_name": "EBL Interest Rates Page",
        "page_url": "https://www.ebl.com.bd/interest-rates",
    },
    {
        "page_name": "EBL Schedule of Charges Page",
        "page_url": "https://www.ebl.com.bd/schedule-of-charges",
    },
    {
        "page_name": "EBL Foreign Exchange Rate Page",
        "page_url": "https://www.ebl.com.bd/foreign-exchange-rate",
    },
    {
        "page_name": "EBL Complaint Cell Page",
        "page_url": "https://www.ebl.com.bd/complaint-cell",
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


    pending_complaint = get_pending_complaint(session_id)

    if pending_complaint:
        if is_complaint_confirmation_no(user_message):
            delete_pending_complaint(session_id)

            return save_and_build_response(
                session_id=session_id,
                user_message=user_message,
                reply=build_complaint_cancelled_reply(),
                source="complaint-agent",
                status="complaint_cancelled",
            )

        if is_complaint_confirmation_yes(user_message):
            complaint = save_complaint(
                session_id=session_id,
                issue_type=pending_complaint["issue_type"],
                description=pending_complaint["description"],
            )

            delete_pending_complaint(session_id)

            complaint_reply = build_complaint_created_reply(complaint)

            return save_and_build_response(
                session_id=session_id,
                user_message=user_message,
                reply=complaint_reply,
                source="complaint-agent",
                status="complaint_created",
            )

        return save_and_build_response(
            session_id=session_id,
            user_message=user_message,
            reply=(
                "Please confirm whether you want me to create the complaint record.\n\n"
                "Reply with Yes to create it or No to cancel."
            ),
            source="complaint-agent",
            status="waiting_complaint_confirmation",
        )

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

        save_pending_complaint(
            session_id=session_id,
            issue_type=issue_type,
            description=user_message,
        )

        confirmation_reply = build_complaint_confirmation_reply(issue_type)

        return save_and_build_response(
            session_id=session_id,
            user_message=user_message,
            reply=confirmation_reply,
            source="complaint-agent",
            status="waiting_complaint_confirmation",
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

    history = get_chat_history(session_id, limit=4)
    has_previous_history = len(history) > 0

    if intent == "off_topic" and not is_allowed_question(user_message, has_previous_history):
        return save_and_build_response(
            session_id=session_id,
            user_message=user_message,
            reply=get_off_topic_reply(),
            source="topic-guard",
            status="off_topic",
        )

    if intent == "account_information" and is_broad_account_opening_question(user_message):
        selected_pages = [
            "EBL Online Apply Page",
            "EBL Retail Deposits Page",
            "EBL SME Deposits Page",
            "EBL Verified Contact Information",
        ]

        website_info = limit_text(
            get_website_information_by_page_names(selected_pages),
            EBL_CONTEXT_LIMIT,
        )

    else:
        website_info = limit_text(
            search_website_information(user_message, limit=5),
            EBL_CONTEXT_LIMIT,
        )

    if not website_info:
        selected_pages = select_knowledge_pages(intent)

        website_info = limit_text(
            get_website_information_by_page_names(selected_pages),
            EBL_CONTEXT_LIMIT,
        )

    if not website_info:
        website_info = limit_text(
            get_website_information(),
            EBL_CONTEXT_LIMIT,
        )

    session_summary = limit_text(
        get_session_summary(session_id),
        SESSION_SUMMARY_LIMIT,
    )

    required_documents_reply = ""

    if not (
        intent == "account_information"
        and is_broad_account_opening_question(user_message)
    ):
        required_documents_reply = build_required_documents_reply(
            user_message,
            website_info,
        )

    if required_documents_reply:
        return save_and_build_response(
            session_id=session_id,
            user_message=user_message,
            reply=required_documents_reply,
            source="website-retrieval",
            status="answered",
        )

    try:
        reply = generate_groq_customer_service_reply(
            user_message,
            history,
            website_info,
            session_summary,
        )

    except Exception as error:
        print("GROQ ERROR:", repr(error))

        return save_and_build_response(
            session_id=session_id,
            user_message=user_message,
            reply=f"System error: {type(error).__name__}: {error}",
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

    try:
        discovered_pages = discover_website_pages()
    except Exception as error:
        discovered_pages = []
        failed_pages.append({
            "page_name": "EBL Detail Page Discovery",
            "page_url": "multiple EBL source pages",
            "error": str(error),
        })

    for page in discovered_pages:
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
                "discovered": True,
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
Official online application link: https://www.ebl.com.bd/onlineapply

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
