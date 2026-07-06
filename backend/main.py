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
    get_branch_locator_reply,
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
LOAN_CATEGORY_QUESTION = "Do you want to know about SME or Retail loans?"


RETAIL_LOAN_PRODUCTS = [
    "Personal Loan",
    "Home Loan",
    "Auto Loan",
    "Two Wheeler Loan",
    "Secured loan (Cash Covered)",
    "EBL Edu Loan",
    "EBL Assure",
    "EBL Executive Loan",
    "EBL Women's Loan",
    "EBL Islamic Home Finance",
    "EBL Islamic Auto Finance",
]


SME_LOAN_PRODUCTS = [
    "EBL Utkorsho",
    "EBL Startup",
    "EBL Mukti",
    "EBL Uddipon",
    "EBL Fleet Financing",
    "EBL Krishi Loan",
    "EBL Asha",
    "EBL Cash Credit",
    "EBL Business Solution",
    "EBL E-Loan /E-Cash",
]


LOAN_PRODUCT_RULES = [
    {
        "name": "EBL Assure",
        "category": "retail",
        "page_name": "EBL Detail Page - Ebl Assure",
        "url": "https://www.ebl.com.bd/retail-loan/EBL-Assure",
        "aliases": ["ebl assure", "assure loan", "assure"],
    },
    {
        "name": "EBL Executive Loan",
        "category": "retail",
        "page_name": "EBL Detail Page - Ebl Executive Loan",
        "url": "https://www.ebl.com.bd/retail-loan/EBL-Executive-Loan",
        "aliases": ["ebl executive loan", "executive loan"],
    },
    {
        "name": "EBL Women's Loan",
        "category": "retail",
        "page_name": "EBL Detail Page - Ebl Womens Loan",
        "url": "https://www.ebl.com.bd/retail-loan/EBL-Womens-Loan",
        "aliases": [
            "ebl womens loan",
            "ebl women's loan",
            "women loan",
            "women's loan",
            "womens loan",
        ],
    },
    {
        "name": "EBL Home Loan",
        "category": "retail",
        "page_name": "EBL Detail Page - Ebl Home Loan",
        "url": "https://www.ebl.com.bd/retail-loan/EBL-Home-Loan",
        "aliases": ["ebl home loan", "home loan", "mortgage loan"],
    },
    {
        "name": "EBL Auto Loan",
        "category": "retail",
        "page_name": "EBL Detail Page - Ebl Auto Loan",
        "url": "https://www.ebl.com.bd/retail-loan/EBL-Auto-Loan",
        "aliases": ["ebl auto loan", "auto loan", "car loan"],
    },
    {
        "name": "EBL Two Wheeler Loan",
        "category": "retail",
        "page_name": "EBL Detail Page - Ebl Two Wheeler Loan",
        "url": "https://www.ebl.com.bd/retail-loan/ebl-two-wheeler-loan",
        "aliases": ["ebl two wheeler loan", "two wheeler loan", "bike loan", "motorcycle loan"],
    },
    {
        "name": "EBL Edu Loan",
        "category": "retail",
        "page_name": "EBL Detail Page - Ebl Edu Loan",
        "url": "https://www.ebl.com.bd/retail-loan/ebl-edu-loan",
        "aliases": ["ebl edu loan", "edu loan", "education loan", "student loan"],
    },
    {
        "name": "EBL Fast Cash",
        "category": "retail",
        "page_name": "EBL Detail Page - Ebl Fast Cash",
        "url": "https://www.ebl.com.bd/retail-loan/ebl-fast-cash",
        "aliases": ["ebl fast cash", "fast cash"],
    },
    {
        "name": "EBL Fast Loan",
        "category": "retail",
        "page_name": "EBL Detail Page - Ebl Fast Loan",
        "url": "https://www.ebl.com.bd/retail-loan/ebl-fast-loan",
        "aliases": ["ebl fast loan", "fast loan"],
    },
    {
        "name": "EBL Women Home Credit",
        "category": "retail",
        "page_name": "EBL Detail Page - Ebl Women Home Credit",
        "url": "https://www.ebl.com.bd/retail-loan/ebl-women-home-credit",
        "aliases": ["ebl women home credit", "women home credit"],
    },
    {
        "name": "EBL Islamic Home Finance",
        "category": "retail",
        "page_name": "EBL Islamic Home Finance Page",
        "url": "https://www.ebl.com.bd/islamic-retail-finance/home-finance/",
        "aliases": [
            "ebl islamic home finance",
            "islamic home finance",
            "islamic home loan",
            "shariah home finance",
        ],
    },
    {
        "name": "EBL Islamic Auto Finance",
        "category": "retail",
        "page_name": "EBL Islamic Auto Finance Page",
        "url": "https://www.ebl.com.bd/islamic-retail-finance/auto-finance/",
        "aliases": [
            "ebl islamic auto finance",
            "islamic auto finance",
            "islamic car finance",
            "islamic auto loan",
            "shariah auto finance",
        ],
    },
    {
        "name": "EBL Utkorsho",
        "category": "sme",
        "page_name": "EBL SME Loan Page",
        "url": "https://www.ebl.com.bd/sme/sme-loans",
        "aliases": ["ebl utkorsho", "utkorsho"],
    },
    {
        "name": "EBL Startup",
        "category": "sme",
        "page_name": "EBL SME Loan Page",
        "url": "https://www.ebl.com.bd/sme/sme-loans",
        "aliases": ["ebl startup", "startup loan", "startup"],
    },
    {
        "name": "EBL Mukti",
        "category": "sme",
        "page_name": "EBL SME Loan Page",
        "url": "https://www.ebl.com.bd/sme/sme-loans",
        "aliases": ["ebl mukti", "mukti"],
    },
    {
        "name": "EBL Uddipon",
        "category": "sme",
        "page_name": "EBL SME Loan Page",
        "url": "https://www.ebl.com.bd/sme/sme-loans",
        "aliases": ["ebl uddipon", "uddipon"],
    },
    {
        "name": "EBL Fleet Financing",
        "category": "sme",
        "page_name": "EBL SME Loan Page",
        "url": "https://www.ebl.com.bd/sme/sme-loans",
        "aliases": ["ebl fleet financing", "fleet financing", "fleet loan"],
    },
    {
        "name": "EBL Krishi Loan",
        "category": "sme",
        "page_name": "EBL SME Loan Page",
        "url": "https://www.ebl.com.bd/sme/sme-loans",
        "aliases": ["ebl krishi loan", "krishi loan", "krishi", "agri loan", "agriculture loan"],
    },
    {
        "name": "EBL Asha",
        "category": "sme",
        "page_name": "EBL SME Loan Page",
        "url": "https://www.ebl.com.bd/sme/sme-loans",
        "aliases": ["ebl asha", "asha loan", "asha"],
    },
    {
        "name": "EBL Cash Credit",
        "category": "sme",
        "page_name": "EBL SME Loan Page",
        "url": "https://www.ebl.com.bd/sme/sme-loans",
        "aliases": ["ebl cash credit", "cash credit", "cc loan"],
    },
    {
        "name": "EBL Business Solution",
        "category": "sme",
        "page_name": "EBL SME Loan Page",
        "url": "https://www.ebl.com.bd/sme/sme-loans",
        "aliases": ["ebl business solution", "business solution", "business solution loan"],
    },
    {
        "name": "EBL E-Loan /E-Cash",
        "category": "sme",
        "page_name": "EBL SME Loan Page",
        "url": "https://www.ebl.com.bd/sme/sme-loans",
        "aliases": [
            "ebl e loan e cash",
            "ebl e-loan e-cash",
            "e loan e cash",
            "e-loan e-cash",
            "e loan",
            "e-loan",
            "e cash",
            "e-cash",
            "ecash",
            "eloan",
        ],
    },
]


LOAN_SECTION_STOP_PREFIXES = [
    "eligibility",
    "mandatory documents",
    "common documents",
    "who are eligible",
    "apply now",
    "quick apply",
    "calulator",
    "calculator",
    "ebl  self  service portal",
    "ebl self service portal",
    "existing customer",
    "new customer",
]


LOAN_SECTION_SKIP_LINES = [
    "back",
    "features",
    "features:",
    "primary features",
    "primary features:",
    "special feature",
    "special feature:",
    "loan purpose",
    "loan purpose:",
]


ACCOUNT_CATEGORY_QUESTION = (
    "Do you want to open a Retail account, an SME account or an Islamic account?"
)


ACCOUNT_CATEGORY_PRODUCTS = {
    "current": [
        "EBL Current Account",
        "EBL Current Plus",
        "EBL Expat LCY Account",
        "EBL Freelancer Suite",
        "EBL Mariner Account (USD)",
        "EBL Expat FCY Account",
        "EBL Citizen Account",
    ],
    "savings": [
        "EBL Power Savings",
        "EBL Classic Savings",
        "EBL Green Account",
        "EBL Max Saver",
        "EBL Premium Savings",
        "EBL 50+ Savings",
        "EBL Smart Women's Savings Account",
    ],
    "dps": [
        "EBL Women Confidence",
        "EBL Kotipoti Scheme",
        "EBL Multiplier",
        "EBL Millionaire Scheme",
        "EBL Confidence",
    ],
    "fixed": [
        "EBL Repeat",
        "EBL FD",
        "EBL Earn First FD",
    ],
    "nrb_foreign": [
        "EBL Shonchoy",
        "EBL Paribar",
        "EBL NFCD",
        "EBL Global",
        "EBL RFCD Account",
        "EBL Expat LCY Account",
        "EBL Expat FCY Account",
        "EBL Mariner Account (USD)",
        "EBL Citizen Account",
        "EBL Freelancer Suite",
    ],
    "personal_retail": [
        "EBL High Earning Account",
        "EBL Personal Retail Account",
    ],
    "student_banking": [
        "EBL Junior Savings Account",
        "EBL Campus Account",
        "EBL Student File Services",
        "EBL Child Future Plan",
        "EBL Aspire Scheme",
        "EBL Little Star",
        "EBL Junior Saver's Islamic Account",
        "EBL Campus Islamic Account",
    ],
    "islamic_deposit": [
        "EBL Islamic Current Account",
        "EBL Islamic SND Account",
        "EBL Speed Islamic SND",
        "EBL High Performance Islamic Account",
        "EBL Power Islamic Savings Account",
        "EBL Executive Islamic Savings Account (Payroll Account)",
        "EBL Women's Islamic Savings Account",
        "EBL Campus Islamic Account",
        "EBL Junior Saver's Islamic Account",
        "EBL Islamic Term Deposit Account",
        "EBL Islamic Monthly Profit Scheme",
        "EBL Islamic DPS Account(s)",
    ],
    "sme_deposit": [
        "EBL Current Account",
        "EBL Foreign Currency Account",
        "EBL ERQ Account",
        "EBL Fixed Deposits",
        "EBL Fixed Deposit - Repeat",
        "EBL Equity Builder Account",
        "EBL Short Notice Deposit",
        "EBL Subidha",
    ],
}


ACCOUNT_CATEGORY_LABELS = {
    "current": "Current Deposit",
    "savings": "Savings Deposit",
    "dps": "DPS",
    "fixed": "Fixed Deposit",
    "nrb_foreign": "NRB/Foreign Currency",
    "personal_retail": "Personal Retail",
    "student_banking": "Student Banking",
    "islamic_deposit": "Islamic Deposit",
    "sme_deposit": "SME Deposit",
}


RETAIL_ACCOUNT_PRODUCTS = list(dict.fromkeys(
    ACCOUNT_CATEGORY_PRODUCTS["current"]
    + ACCOUNT_CATEGORY_PRODUCTS["savings"]
    + ACCOUNT_CATEGORY_PRODUCTS["dps"]
    + ACCOUNT_CATEGORY_PRODUCTS["fixed"]
    + ACCOUNT_CATEGORY_PRODUCTS["nrb_foreign"]
    + ACCOUNT_CATEGORY_PRODUCTS["personal_retail"]
    + ACCOUNT_CATEGORY_PRODUCTS["student_banking"]
    + ACCOUNT_CATEGORY_PRODUCTS["islamic_deposit"]
))


ACCOUNT_SEGMENT_PRODUCTS = {
    "retail": RETAIL_ACCOUNT_PRODUCTS,
    "sme": ACCOUNT_CATEGORY_PRODUCTS["sme_deposit"],
}


ACCOUNT_SEGMENT_LABELS = {
    "retail": "Retail Account",
    "sme": "SME Account",
}


RETAIL_BANKING_LINKS = [
    ("Retail Loan", "https://www.ebl.com.bd/retail/retail-loan"),
    ("Retail Deposit", "https://www.ebl.com.bd/retail/retail-deposit"),
    ("EBL Cards", "https://www.ebl.com.bd/retail/EBL-Cards"),
    ("EBL Skybanking", "https://www.ebl.com.bd/retail-digital/ebl-skybanking"),
    (
        "EBL Missed Call Alert Service",
        "https://www.ebl.com.bd/retail-digital/ebl-missed-call-alert-service",
    ),
    ("EBL 365 PLUS", "https://www.ebl.com.bd/retail-digital/ebl-365-plus"),
    ("EBL SKYPAY", "https://www.ebl.com.bd/retail-ecommerce/ebl-skypay"),
    ("EBL Insta Account-Branch", "https://www.ebl.com.bd/retail/ebl-insta-account"),
    ("EBL Insta Banking-Online", "https://www.ebl.com.bd/retail/ebl-insta-banking"),
    ("EBL Priority Banking", "https://www.ebl.com.bd/priority/"),
    ("EBL Power Banking", "https://www.ebl.com.bd/powerbanking"),
    ("EBL Super Saver", "https://www.ebl.com.bd/ebl-super-saver"),
    ("EBL Women Banking", "https://www.ebl.com.bd/retail/Women-Banking"),
    ("EBL Agent Banking", "https://www.ebl.com.bd/agentbanking"),
    ("EBL Payroll Banking", "https://www.ebl.com.bd/retail/EBL-Payroll-Banking"),
    ("EBL Student Banking", "https://www.ebl.com.bd/retail/EBL-Student-Banking"),
    ("EBL Bancassurance", "https://www.ebl.com.bd/retail/ebl-bancassurance"),
    ("EBL Retail Alliance", "https://www.ebl.com.bd/retail/ebl-retail-propositions"),
]


ISLAMIC_BANKING_LINKS = [
    ("EBL Islamic Banking", "https://www.ebl.com.bd/islamicbanking"),
    ("Shariah Committee", "https://www.ebl.com.bd/islamic/member_ssc"),
    ("Islamic Retail", "https://www.ebl.com.bd/islamic/islamic-retail-finance"),
    ("Islamic SME", "https://www.ebl.com.bd/islamic/islamic-sme-finance"),
    ("Islamic Corporate", "https://www.ebl.com.bd/islamic/islamic-corporate-finance"),
    ("Islamic Cards", "https://www.ebl.com.bd/islamic/islamic-cards"),
    ("Profit Distribution", "https://www.ebl.com.bd/islamic/profit-distribution"),
    ("Islamic Notice", "https://www.ebl.com.bd/islamic/notice"),
    (
        "EBL Islamic Visa Platinum Debit Card",
        "https://www.ebl.com.bd/islamic/eblcard/ebl-islamic-visa-platinum-debit-card",
    ),
    (
        "EBL Islamic Visa Prepaid Card",
        "https://www.ebl.com.bd/islamic/eblcard/ebl-islamic-visa-prepaid-card",
    ),
    (
        "EBL Islamic Priority Visa Signature Debit Card",
        "https://www.ebl.com.bd/islamic/eblcard/ebl-islamic-priority-visa-signature-debit-card",
    ),
    (
        "EBL Islamic Women's Platinum Debit Card",
        "https://www.ebl.com.bd/islamic/eblcard/islamic-women-platinum-debit-card",
    ),
]


ACCOUNT_PRODUCT_RULES = [
    {
        "name": "EBL Current Account",
        "category": "sme_deposit",
        "page_name": "EBL SME Deposits Page",
        "url": "https://www.ebl.com.bd/sme/sme-deposits",
        "aliases": ["sme current account", "sme current deposit", "business current account"],
    },
    {
        "name": "EBL Current Account",
        "category": "current",
        "page_name": "EBL Current Account Page",
        "url": "https://www.ebl.com.bd/retail-deposit/EBL-Current-Account",
        "aliases": ["ebl current account", "current account"],
    },
    {
        "name": "EBL Current Plus",
        "category": "current",
        "page_name": "EBL Detail Page - Ebl Current Plus",
        "url": "https://www.ebl.com.bd/retail-deposit/EBL-Current-Plus",
        "aliases": ["ebl current plus", "current plus"],
    },
    {
        "name": "EBL Power Savings",
        "category": "savings",
        "page_name": "EBL Power Savings Page",
        "url": "https://www.ebl.com.bd/retail-deposit/EBL-Power-Savings",
        "aliases": ["ebl power savings", "power savings"],
    },
    {
        "name": "EBL Classic Savings",
        "category": "savings",
        "page_name": "EBL Detail Page - Ebl Classic Savings",
        "url": "https://www.ebl.com.bd/retail-deposit/EBL-Classic-Savings",
        "aliases": ["ebl classic savings", "classic savings"],
    },
    {
        "name": "EBL Green Account",
        "category": "savings",
        "page_name": "EBL Detail Page - Ebl Green Account",
        "url": "https://www.ebl.com.bd/retail-deposit/ebl-green-account",
        "aliases": ["ebl green account", "green account"],
    },
    {
        "name": "EBL Max Saver",
        "category": "savings",
        "page_name": "EBL Max Saver Page",
        "url": "https://www.ebl.com.bd/retail-deposit/EBL-Max-Saver",
        "aliases": ["ebl max saver", "max saver"],
    },
    {
        "name": "EBL Premium Savings",
        "category": "savings",
        "page_name": "EBL Premium Savings Page",
        "url": "https://www.ebl.com.bd/retail-deposit/EBL-Premium-Savings",
        "aliases": ["ebl premium savings", "premium savings"],
    },
    {
        "name": "EBL 50+ Savings",
        "category": "savings",
        "page_name": "EBL 50+ Savings Page",
        "url": "https://www.ebl.com.bd/retail-deposit/EBL-50Plus-Savings",
        "aliases": ["ebl 50+ savings", "50+ savings", "50 plus savings", "senior savings"],
    },
    {
        "name": "EBL Smart Women's Savings Account",
        "category": "savings",
        "page_name": "EBL Detail Page - Ebl Smart Womens Savings Account",
        "url": "https://www.ebl.com.bd/retail-deposit/EBL-Smart-Womens-Savings-Account",
        "aliases": [
            "ebl smart womens savings account",
            "smart womens savings",
            "women savings account",
            "women's savings account",
            "womens savings account",
        ],
    },
    {
        "name": "EBL Women Confidence",
        "category": "dps",
        "page_name": "EBL Detail Page - Ebl Women Confidence",
        "url": "https://www.ebl.com.bd/retail-deposit/ebl-women-confidence",
        "aliases": ["ebl women confidence", "women confidence"],
    },
    {
        "name": "EBL Kotipoti Scheme",
        "category": "dps",
        "page_name": "EBL Detail Page - Ebl Kotipoti Scheme",
        "url": "https://www.ebl.com.bd/retail-deposit/EBL-Kotipoti-Scheme",
        "aliases": ["ebl kotipoti scheme", "kotipoti scheme", "kotipoti"],
    },
    {
        "name": "EBL Multiplier",
        "category": "dps",
        "page_name": "EBL Detail Page - Ebl Multiplier",
        "url": "https://www.ebl.com.bd/retail-deposit/EBL-Multiplier",
        "aliases": ["ebl multiplier", "multiplier scheme"],
    },
    {
        "name": "EBL Millionaire Scheme",
        "category": "dps",
        "page_name": "EBL Detail Page - Ebl Millionaire Scheme",
        "url": "https://www.ebl.com.bd/retail-deposit/EBL-Millionaire-Scheme",
        "aliases": ["ebl millionaire scheme", "millionaire scheme"],
    },
    {
        "name": "EBL Confidence",
        "category": "dps",
        "page_name": "EBL Detail Page - Ebl Confidence",
        "url": "https://www.ebl.com.bd/retail-deposit/EBL-Confidence",
        "aliases": ["ebl confidence", "confidence dps"],
    },
    {
        "name": "EBL Repeat",
        "category": "fixed",
        "page_name": "EBL Detail Page - Ebl Repeat",
        "url": "https://www.ebl.com.bd/retail-deposit/EBL-Repeat",
        "aliases": ["ebl repeat", "repeat fd", "repeat fixed deposit"],
    },
    {
        "name": "EBL FD",
        "category": "fixed",
        "page_name": "EBL Detail Page - Ebl Fd",
        "url": "https://www.ebl.com.bd/retail-deposit/EBL-FD",
        "aliases": ["ebl fd", "ebl fixed deposit"],
    },
    {
        "name": "EBL Earn First FD",
        "category": "fixed",
        "page_name": "EBL Detail Page - Ebl Earn First Fd",
        "url": "https://www.ebl.com.bd/retail-deposit/EBL-Earn-First-FD",
        "aliases": ["ebl earn first fd", "earn first fd", "earn first fixed deposit"],
    },
    {
        "name": "EBL Shonchoy",
        "category": "nrb_foreign",
        "page_name": "EBL Detail Page - Ebl Shonchoy",
        "url": "https://www.ebl.com.bd/retail-deposit/EBL-Shonchoy",
        "aliases": ["ebl shonchoy", "shonchoy"],
    },
    {
        "name": "EBL Paribar",
        "category": "nrb_foreign",
        "page_name": "EBL Detail Page - Ebl Paribar",
        "url": "https://www.ebl.com.bd/retail-deposit/EBL-Paribar",
        "aliases": ["ebl paribar", "paribar"],
    },
    {
        "name": "EBL NFCD",
        "category": "nrb_foreign",
        "page_name": "EBL Detail Page - Ebl Nfcd",
        "url": "https://www.ebl.com.bd/retail-deposit/EBL-NFCD",
        "aliases": ["ebl nfcd", "nfcd"],
    },
    {
        "name": "EBL Global",
        "category": "nrb_foreign",
        "page_name": "EBL Detail Page - Ebl Global",
        "url": "https://www.ebl.com.bd/retail-deposit/ebl-global",
        "aliases": ["ebl global"],
    },
    {
        "name": "EBL RFCD Account",
        "category": "nrb_foreign",
        "page_name": "EBL Detail Page - Ebl Rfcd Account",
        "url": "https://www.ebl.com.bd/retail-deposit/EBL-RFCD-Account",
        "aliases": ["ebl rfcd account", "rfcd account", "rfcd"],
    },
    {
        "name": "EBL Expat LCY Account",
        "category": "nrb_foreign",
        "page_name": "EBL Detail Page - Ebl Expat Lcy",
        "url": "https://www.ebl.com.bd/retail-deposit/ebl-expat-lcy",
        "aliases": ["ebl expat lcy account", "expat lcy account", "expat lcy"],
    },
    {
        "name": "EBL Expat FCY Account",
        "category": "nrb_foreign",
        "page_name": "EBL Detail Page - Ebl Expat Fcy",
        "url": "https://www.ebl.com.bd/retail-deposit/ebl-expat-fcy",
        "aliases": ["ebl expat fcy account", "expat fcy account", "expat fcy"],
    },
    {
        "name": "EBL Freelancer Suite",
        "category": "nrb_foreign",
        "page_name": "EBL Detail Page - Ebl Freelancer",
        "url": "https://www.ebl.com.bd/retail-deposit/ebl-freelancer",
        "aliases": ["ebl freelancer suite", "freelancer suite", "freelancer account"],
    },
    {
        "name": "EBL Mariner Account (USD)",
        "category": "nrb_foreign",
        "page_name": "EBL Detail Page - Ebl Mariner Account Usd",
        "url": "https://www.ebl.com.bd/retail-deposit/ebl-mariner-account-usd",
        "aliases": ["ebl mariner account usd", "mariner account", "mariner usd"],
    },
    {
        "name": "EBL Citizen Account",
        "category": "nrb_foreign",
        "page_name": "EBL Detail Page - Ebl Citizen",
        "url": "https://www.ebl.com.bd/retail-deposit/ebl-citizen",
        "aliases": ["ebl citizen account", "citizen account"],
    },
    {
        "name": "EBL High Earning Account",
        "category": "personal_retail",
        "page_name": "EBL Detail Page - EBL High Earning",
        "url": "https://www.ebl.com.bd/retail-deposit/ebl-high-earning-account",
        "aliases": ["ebl high earning account", "high earning account"],
    },
    {
        "name": "EBL Personal Retail Account",
        "category": "personal_retail",
        "page_name": "EBL Detail Page - Ebl Personal Retail Account",
        "url": "https://www.ebl.com.bd/retail-deposit/ebl-personal-retail-account",
        "aliases": ["ebl personal retail account", "personal retail account"],
    },
    {
        "name": "EBL Junior Savings Account",
        "category": "student_banking",
        "page_name": "EBL Junior Savings Account Page",
        "url": "https://www.ebl.com.bd/student-banking/EBL-Junior",
        "aliases": [
            "ebl junior savings account",
            "junior savings account",
            "junior savings",
            "junior account",
        ],
    },
    {
        "name": "EBL Campus Account",
        "category": "student_banking",
        "page_name": "EBL Campus Account Page",
        "url": "https://www.ebl.com.bd/student-banking/EBL-Campus-Account",
        "aliases": [
            "ebl campus account",
            "campus account",
            "student campus account",
        ],
    },
    {
        "name": "EBL Student File Services",
        "category": "student_banking",
        "page_name": "EBL Student File Services Page",
        "url": "https://www.ebl.com.bd/student-banking/EBL-Student-File-Services",
        "aliases": [
            "ebl student file services",
            "student file services",
            "student file service",
            "student file",
        ],
    },
    {
        "name": "EBL Child Future Plan",
        "category": "student_banking",
        "page_name": "EBL Child Future Plan Page",
        "url": "https://www.ebl.com.bd/student-banking/EBL-Child-Future-Plan",
        "aliases": ["ebl child future plan", "child future plan"],
    },
    {
        "name": "EBL Aspire Scheme",
        "category": "student_banking",
        "page_name": "EBL Aspire Scheme Page",
        "url": "https://www.ebl.com.bd/student-banking/EBL-Aspire-Scheme",
        "aliases": ["ebl aspire scheme", "aspire scheme", "aspire"],
    },
    {
        "name": "EBL Little Star",
        "category": "student_banking",
        "page_name": "EBL Little Star Page",
        "url": "https://www.ebl.com.bd/student-banking/ebl-little-star",
        "aliases": ["ebl little star", "little star"],
    },
    {
        "name": "EBL Islamic Current Account",
        "category": "islamic_deposit",
        "page_name": "EBL Islamic Current Account Page",
        "url": "https://www.ebl.com.bd/islamic/deposit/ebl-islamic-current-account",
        "aliases": ["ebl islamic current account", "islamic current account"],
    },
    {
        "name": "EBL Islamic SND Account",
        "category": "islamic_deposit",
        "page_name": "EBL Islamic SND Account Page",
        "url": "https://www.ebl.com.bd/islamic/deposit/ebl-islamic-snd-account",
        "aliases": ["ebl islamic snd account", "islamic snd account", "islamic special notice deposit"],
    },
    {
        "name": "EBL Speed Islamic SND",
        "category": "islamic_deposit",
        "page_name": "EBL Speed Islamic SND Page",
        "url": "https://www.ebl.com.bd/islamic/deposit/ebl-speed-islamic-snd",
        "aliases": ["ebl speed islamic snd", "speed islamic snd"],
    },
    {
        "name": "EBL High Performance Islamic Account",
        "category": "islamic_deposit",
        "page_name": "EBL High Performance Islamic Account Page",
        "url": "https://www.ebl.com.bd/islamic/deposit/ebl-high-performance-islamic-account",
        "aliases": ["ebl high performance islamic account", "high performance islamic account"],
    },
    {
        "name": "EBL Power Islamic Savings Account",
        "category": "islamic_deposit",
        "page_name": "EBL Power Islamic Savings Account Page",
        "url": "https://www.ebl.com.bd/islamic/deposit/ebl-power-islamic-savings-account",
        "aliases": ["ebl power islamic savings account", "power islamic savings", "islamic savings account"],
    },
    {
        "name": "EBL Executive Islamic Savings Account (Payroll Account)",
        "category": "islamic_deposit",
        "page_name": "EBL Executive Islamic Savings Account Page",
        "url": "https://www.ebl.com.bd/islamic/deposit/ebl-executive-islamic-savings-account-payroll-account",
        "aliases": [
            "ebl executive islamic savings account",
            "executive islamic savings",
            "islamic payroll account",
        ],
    },
    {
        "name": "EBL Women's Islamic Savings Account",
        "category": "islamic_deposit",
        "page_name": "EBL Women's Islamic Savings Account Page",
        "url": "https://www.ebl.com.bd/islamic/deposit/ebl-womens-islamic-savings-account",
        "aliases": [
            "ebl women's islamic savings account",
            "ebl womens islamic savings account",
            "women's islamic savings",
            "womens islamic savings",
        ],
    },
    {
        "name": "EBL Campus Islamic Account",
        "category": "islamic_deposit",
        "page_name": "EBL Campus Islamic Account Page",
        "url": "https://www.ebl.com.bd/islamic/deposit/ebl-campus-islamic-account",
        "aliases": ["ebl campus islamic account", "campus islamic account", "islamic student account"],
    },
    {
        "name": "EBL Junior Saver's Islamic Account",
        "category": "islamic_deposit",
        "page_name": "EBL Junior Saver's Islamic Account Page",
        "url": "https://www.ebl.com.bd/islamic/deposit/ebl-junior-savers-islamic-account",
        "aliases": [
            "ebl junior saver's islamic account",
            "ebl junior savers islamic account",
            "junior savers islamic account",
            "junior saver islamic account",
        ],
    },
    {
        "name": "EBL Islamic Term Deposit Account",
        "category": "islamic_deposit",
        "page_name": "EBL Islamic Term Deposit Account Page",
        "url": "https://www.ebl.com.bd/islamic/deposit/ebl-islamic-term-deposit-account",
        "aliases": ["ebl islamic term deposit account", "islamic term deposit", "islamic fixed deposit"],
    },
    {
        "name": "EBL Islamic Monthly Profit Scheme",
        "category": "islamic_deposit",
        "page_name": "EBL Islamic Monthly Profit Scheme Page",
        "url": "https://www.ebl.com.bd/islamic/deposit/ebl-islamic-monthly-profit-scheme",
        "aliases": ["ebl islamic monthly profit scheme", "islamic monthly profit scheme"],
    },
    {
        "name": "EBL Islamic DPS Account(s)",
        "category": "islamic_deposit",
        "page_name": "EBL Islamic DPS Account Page",
        "url": "https://www.ebl.com.bd/islamic/deposit/ebl-islamic-dps-accounts",
        "aliases": ["ebl islamic dps account", "ebl islamic dps accounts", "islamic dps"],
    },
    {
        "name": "EBL Foreign Currency Account",
        "category": "sme_deposit",
        "page_name": "EBL SME Deposits Page",
        "url": "https://www.ebl.com.bd/sme/sme-deposits",
        "aliases": ["ebl foreign currency account", "foreign currency account"],
    },
    {
        "name": "EBL ERQ Account",
        "category": "sme_deposit",
        "page_name": "EBL SME Deposits Page",
        "url": "https://www.ebl.com.bd/sme/sme-deposits",
        "aliases": ["ebl erq account", "erq account", "erq"],
    },
    {
        "name": "EBL Fixed Deposits",
        "category": "sme_deposit",
        "page_name": "EBL SME Deposits Page",
        "url": "https://www.ebl.com.bd/sme/sme-deposits",
        "aliases": ["ebl fixed deposits", "sme fixed deposits"],
    },
    {
        "name": "EBL Fixed Deposit - Repeat",
        "category": "sme_deposit",
        "page_name": "EBL SME Deposits Page",
        "url": "https://www.ebl.com.bd/sme/sme-deposits",
        "aliases": ["ebl fixed deposit repeat", "sme repeat fixed deposit"],
    },
    {
        "name": "EBL Equity Builder Account",
        "category": "sme_deposit",
        "page_name": "EBL SME Deposits Page",
        "url": "https://www.ebl.com.bd/sme/sme-deposits",
        "aliases": ["ebl equity builder account", "equity builder account", "equity builder"],
    },
    {
        "name": "EBL Short Notice Deposit",
        "category": "sme_deposit",
        "page_name": "EBL SME Deposits Page",
        "url": "https://www.ebl.com.bd/sme/sme-deposits",
        "aliases": ["ebl short notice deposit", "short notice deposit", "snd account"],
    },
    {
        "name": "EBL Subidha",
        "category": "sme_deposit",
        "page_name": "EBL SME Deposits Page",
        "url": "https://www.ebl.com.bd/sme/sme-deposits",
        "aliases": ["ebl subidha", "subidha"],
    },
]


ACCOUNT_SECTION_STOP_PREFIXES = [
    "eligibility",
    "eligibility criteria",
    "identification document",
    "the below maturity value table",
    "product name",
    "maturity amount",
    "required documents",
    "documents required",
    "account opening documents",
    "mandatory documents",
    "relevant charges",
    "calculator",
    "fees",
    "apply now",
    "quick apply",
    "click here",
    "ebl  self  service portal",
    "ebl self service portal",
    "existing customer",
    "new customer",
    "read more",
]


ACCOUNT_SECTION_SKIP_LINES = [
    "back",
    "features",
    "features:",
    "key features",
    "key features:",
    "key features include",
    "key features include:",
    "best for you if you:",
    "best for you if you are looking for a",
    "best for you if you are looking for a:",
    "best for you if you have",
    "best for you if you have:",
    "here",
]

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
        "account options",
        "account types",
        "available accounts",
        "create account",
        "new account",
        "what accounts are available",
        "which accounts are available",
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


def normalize_loan_lookup_text(text):
    text = text.lower()

    replacements = {
        "\u2018": "'",
        "\u2019": "'",
        "-": " ",
        "_": " ",
        "/": " ",
        "(": " ",
        ")": " ",
        ".": " ",
        ",": " ",
        "?": " ",
        "!": " ",
        ":": " ",
        "'": "",
    }

    for old_value, new_value in replacements.items():
        text = text.replace(old_value, new_value)

    return " ".join(text.split())


def contains_loan_lookup_phrase(message, phrase):
    normalized_message = normalize_loan_lookup_text(message)
    normalized_phrase = normalize_loan_lookup_text(phrase)

    return f" {normalized_phrase} " in f" {normalized_message} "


def detect_specific_loan_product(message):
    for product in LOAN_PRODUCT_RULES:
        for alias in product["aliases"]:
            if contains_loan_lookup_phrase(message, alias):
                return product

    return None


def detect_loan_category(message):
    normalized_message = normalize_loan_lookup_text(message)
    words = normalized_message.split()

    if "sme" in words:
        return "sme"

    if "retail" in words:
        return "retail"

    return ""


def last_assistant_asked_for_loan_category(history):
    for item in reversed(history):
        if item.get("role") != "assistant":
            continue

        content = item.get("content", "").lower()

        return "sme or retail loans" in content

    return False


def is_loan_category_follow_up(message, history):
    return bool(
        detect_loan_category(message)
        and last_assistant_asked_for_loan_category(history)
    )


def build_loan_category_reply(category):
    if category == "retail":
        product_lines = "\n".join(f"- {product}" for product in RETAIL_LOAN_PRODUCTS)

        return (
            "EBL Retail Loan options include:\n\n"
            f"{product_lines}\n\n"
            "Please tell me the specific Retail loan name if you want its features and link."
        )

    if category == "sme":
        product_lines = "\n".join(f"- {product}" for product in SME_LOAN_PRODUCTS)

        return (
            "EBL SME Loan options include:\n\n"
            f"{product_lines}\n\n"
            "Please tell me the specific SME loan name if you want its features and link."
        )

    return ""


def build_retail_loan_subcategory_reply(user_message):
    if contains_loan_lookup_phrase(user_message, "personal loan"):
        return (
            "EBL Personal Loan options include:\n\n"
            "- EBL Assure\n"
            "- EBL Executive Loan\n"
            "- EBL Women's Loan\n\n"
            "Please tell me the specific Personal Loan product name if you want its features and link."
        )

    if (
        contains_loan_lookup_phrase(user_message, "secured loan")
        or contains_loan_lookup_phrase(user_message, "cash covered")
    ):
        return (
            "EBL Secured loan (Cash Covered) options include:\n\n"
            "- EBL Fast Cash\n"
            "- EBL Fast Loan\n\n"
            "Please tell me the specific Secured loan product name if you want its features and link."
        )

    return ""


def get_content_from_website_information(website_information):
    marker = "Content:\n"

    if marker not in website_information:
        return website_information

    return website_information.split(marker, 1)[1].strip()


def find_case_insensitive(text, pattern, start=0):
    return text.lower().find(pattern.lower(), start)


def slice_retail_loan_section(page_text, product_name):
    marker = f"BACK\n{product_name}\n"
    start = find_case_insensitive(page_text, marker)

    if start >= 0:
        section = page_text[start + len("BACK\n"):]
    else:
        title_marker = f"\n{product_name}\n"
        start = page_text.lower().rfind(title_marker.lower())

        if start < 0:
            start = find_case_insensitive(page_text, product_name)

        if start < 0:
            return page_text

        section = page_text[start:].strip()

    end_positions = []

    for stop_text in [
        "\nQuick Apply",
        "\nCalulator",
        "\nCalculator",
        "\nEBL  Self  Service Portal",
        "\nEBL Self Service Portal",
    ]:
        position = find_case_insensitive(section, stop_text)

        if position >= 0:
            end_positions.append(position)

    if end_positions:
        section = section[:min(end_positions)]

    return section.strip()


def slice_sme_loan_section(page_text, product_name):
    start = find_case_insensitive(page_text, product_name)

    if start < 0:
        return page_text

    boundary_products = SME_LOAN_PRODUCTS
    end_positions = []

    for boundary_product in boundary_products:
        if boundary_product == product_name:
            continue

        position = find_case_insensitive(page_text, boundary_product, start + len(product_name))

        if position >= 0:
            end_positions.append(position)

    end = min(end_positions) if end_positions else len(page_text)

    return page_text[start:end].strip()


def clean_loan_line(line):
    replacements = {
        "\u2018": "'",
        "\u2019": "'",
        "\u201c": '"',
        "\u201d": '"',
        "\u2013": "-",
        "\u2014": "-",
        "\u2022": "-",
        "\ufffd": "",
    }

    cleaned_line = line.strip()

    for old_value, new_value in replacements.items():
        cleaned_line = cleaned_line.replace(old_value, new_value)

    return " ".join(cleaned_line.split())


def should_stop_loan_feature_collection(line):
    lower_line = line.lower()

    for prefix in LOAN_SECTION_STOP_PREFIXES:
        if lower_line.startswith(prefix):
            return True

    return False


def should_skip_loan_feature_line(line, product_name):
    lower_line = line.lower()

    if not line or line in ["|", "+", "-"]:
        return True

    if lower_line == product_name.lower():
        return True

    return lower_line in LOAN_SECTION_SKIP_LINES


def build_loan_feature_bullets(section_text, product_name, max_bullets=10):
    raw_lines = section_text.splitlines()
    lines = [clean_loan_line(line) for line in raw_lines]
    lines = [line for line in lines if line]

    bullets = []
    index = 0

    while index < len(lines):
        line = lines[index]

        if should_stop_loan_feature_collection(line):
            break

        if should_skip_loan_feature_line(line, product_name):
            index += 1
            continue

        next_line = lines[index + 1] if index + 1 < len(lines) else ""

        if line.endswith(":") and next_line and not should_stop_loan_feature_collection(next_line):
            bullets.append(f"{line.rstrip(':')}: {next_line}")
            index += 2
        else:
            bullets.append(line)
            index += 1

        if len(bullets) >= max_bullets:
            break

    return bullets


def build_specific_loan_reply(product):
    website_information = get_website_information_by_page_names([product["page_name"]])
    page_text = get_content_from_website_information(website_information)

    if product["category"] == "sme":
        section_text = slice_sme_loan_section(page_text, product["name"])
    else:
        section_text = slice_retail_loan_section(page_text, product["name"])

    bullets = build_loan_feature_bullets(section_text, product["name"])

    if not bullets:
        return (
            f"{product['name']} details:\n\n"
            f"Link: {product['url']}"
        )

    bullet_text = "\n".join(f"- {bullet}" for bullet in bullets)

    return (
        f"{product['name']} features:\n\n"
        f"{bullet_text}\n\n"
        f"Link: {product['url']}"
    )


def build_loan_router_reply(user_message, intent, history):
    product = detect_specific_loan_product(user_message)

    if product:
        return build_specific_loan_reply(product)

    retail_subcategory_reply = build_retail_loan_subcategory_reply(user_message)

    if retail_subcategory_reply:
        return retail_subcategory_reply

    category = detect_loan_category(user_message)

    if intent == "loan_information":
        if category:
            return build_loan_category_reply(category)

        return LOAN_CATEGORY_QUESTION

    if is_loan_category_follow_up(user_message, history):
        return build_loan_category_reply(category)

    return ""


def detect_account_segment(message):
    normalized_message = normalize_loan_lookup_text(message)
    words = normalized_message.split()

    if "sme" in words or "business" in words or "institutional" in words:
        return "sme"

    if "retail" in words:
        return "retail"

    if "personal" in words and ("account" in words or "deposit" in words):
        return "retail"

    return ""


def detect_account_category(message):
    normalized_message = normalize_loan_lookup_text(message)
    words = normalized_message.split()

    if (
        "islamic" in words
        or "shariah" in words
        or "sharia" in words
        or "mudarabah" in words
        or "wadiah" in words
    ):
        return "islamic_deposit"

    if "sme" in words or "business" in words or "institutional" in words:
        return "sme_deposit"

    if (
        "student" in words
        or "campus" in words
        or "junior" in words
        or "child" in words
        or "aspire" in words
        or "little" in words
    ):
        return "student_banking"

    if "personal" in words and "retail" in words:
        return "personal_retail"

    if (
        "nrb" in words
        or "foreign" in words
        or "currency" in words
        or "fcy" in words
        or "usd" in words
        or "rfcd" in words
        or "nfcd" in words
        or "expat" in words
        or "mariner" in words
        or "freelancer" in words
    ):
        return "nrb_foreign"

    if "dps" in words or "scheme" in words or "recurring" in words:
        return "dps"

    if "fixed" in words or "fd" in words or "fdr" in words or "term" in words:
        return "fixed"

    if "saving" in words or "savings" in words:
        return "savings"

    if "current" in words:
        return "current"

    return ""


def detect_specific_account_product(message):
    category = detect_account_category(message)

    for product in ACCOUNT_PRODUCT_RULES:
        for alias in product["aliases"]:
            if alias.lower().startswith("ebl ") and contains_loan_lookup_phrase(message, alias):
                return product

    for product in ACCOUNT_PRODUCT_RULES:
        if category and product["category"] != category:
            continue

        for alias in product["aliases"]:
            if contains_loan_lookup_phrase(message, alias):
                return product

    return None


def last_assistant_asked_for_account_category(history):
    for item in reversed(history):
        if item.get("role") != "assistant":
            continue

        content = item.get("content", "").lower()

        return (
            "retail account or an sme account" in content
            or "retail account or sme account" in content
            or "which account type do you want to open" in content
        )

    return False


def is_account_category_follow_up(message, history):
    return bool(
        (detect_account_segment(message) or detect_account_category(message))
        and last_assistant_asked_for_account_category(history)
    )


def is_account_feature_follow_up(message):
    normalized_message = normalize_loan_lookup_text(message)

    return normalized_message in [
        "feature",
        "features",
        "benefit",
        "benefits",
        "show features",
        "show benefits",
        "tell me features",
        "tell me benefits",
        "tell me more",
        "details",
        "more details",
    ]


def detect_account_product_from_history(history):
    for item in reversed(history):
        if item.get("role") != "assistant":
            continue

        content = item.get("content", "").lower()

        for product in ACCOUNT_PRODUCT_RULES:
            if product["name"].lower() in content:
                return product

    return None


def build_link_list_reply(title, links):
    link_lines = "\n".join(
        f"- {label}: {url}"
        for label, url in links
    )

    return f"{title}\n\n{link_lines}"


def build_retail_banking_overview_reply():
    return build_link_list_reply(
        "EBL Retail Banking options include:",
        RETAIL_BANKING_LINKS,
    )


def build_islamic_banking_overview_reply():
    return build_link_list_reply(
        "EBL Islamic Banking information and product links:",
        ISLAMIC_BANKING_LINKS,
    )


def build_account_segment_reply(segment):
    products = ACCOUNT_SEGMENT_PRODUCTS.get(segment, [])

    if not products:
        return ""

    product_lines = "\n".join(f"- {product}" for product in products)
    segment_label = ACCOUNT_SEGMENT_LABELS.get(segment, "Account")

    return (
        f"EBL {segment_label} products include:\n\n"
        f"{product_lines}\n\n"
        "Please tell me the specific account product name if you want its features and link."
    )


def build_account_category_reply(category):
    products = ACCOUNT_CATEGORY_PRODUCTS.get(category, [])

    if not products:
        return ""

    product_lines = "\n".join(f"- {product}" for product in products)
    category_label = ACCOUNT_CATEGORY_LABELS.get(category, "Account")

    return (
        f"EBL {category_label} options include:\n\n"
        f"{product_lines}\n\n"
        f"Please tell me the specific {category_label} product name if you want its features and link."
    )


def slice_retail_account_section(page_text, product_name):
    marker = f"BACK\n{product_name}\n"
    start = find_case_insensitive(page_text, marker)

    if start >= 0:
        section = page_text[start + len("BACK\n"):]
    else:
        title_marker = f"\n{product_name}\n"
        content_start = find_case_insensitive(page_text, "\nSearch\n")

        if content_start >= 0:
            start = find_case_insensitive(
                page_text,
                title_marker,
                content_start,
            )
        else:
            start = -1

        if start < 0:
            start = page_text.lower().rfind(title_marker.lower())

        if start < 0:
            start = find_case_insensitive(page_text, product_name)

        if start < 0:
            return page_text

        section = page_text[start:].strip()

    return trim_account_section_end(section)


def slice_sme_account_section(page_text, product_name):
    start = find_case_insensitive(page_text, product_name)

    if start < 0:
        return page_text

    boundary_products = ACCOUNT_CATEGORY_PRODUCTS["sme_deposit"]
    end_positions = []

    for boundary_product in boundary_products:
        if boundary_product == product_name:
            continue

        position = find_case_insensitive(page_text, boundary_product, start + len(product_name))

        if position >= 0:
            end_positions.append(position)

    end = min(end_positions) if end_positions else len(page_text)

    return page_text[start:end].strip()


def trim_account_section_end(section_text):
    end_positions = []

    for stop_text in [
        "\nRequired Documents",
        "\nDocuments Required",
        "\nAccount Opening Documents",
        "\nFees",
        "\nQuick Apply",
        "\nApply now",
        "\nEBL  Self  Service Portal",
        "\nEBL Self Service Portal",
    ]:
        position = find_case_insensitive(section_text, stop_text)

        if position >= 0:
            end_positions.append(position)

    if end_positions:
        return section_text[:min(end_positions)].strip()

    return section_text.strip()


def should_stop_account_feature_collection(line):
    lower_line = line.lower()

    for prefix in ACCOUNT_SECTION_STOP_PREFIXES:
        if lower_line.startswith(prefix):
            return True

    return False


def should_skip_account_feature_line(line, product_name):
    lower_line = line.lower()

    if not line or line in ["|", "+", "-"]:
        return True

    if lower_line == product_name.lower():
        return True

    return lower_line in ACCOUNT_SECTION_SKIP_LINES


def build_account_feature_bullets(section_text, product_name, max_bullets=15):
    raw_lines = section_text.splitlines()
    lines = [clean_loan_line(line) for line in raw_lines]
    lines = [line for line in lines if line]

    feature_headings = [
        "features",
        "key features",
        "key features include",
        "features and benefits",
        "benefits and features",
    ]

    for index, line in enumerate(lines):
        normalized_line = line.lower().rstrip(":")

        if normalized_line in feature_headings:
            lines = lines[index + 1:]
            break

    bullets = []
    index = 0

    while index < len(lines):
        line = lines[index]
        line = line.replace(" : Please see", "").replace(": Please see", "")

        if should_stop_account_feature_collection(line):
            break

        if should_skip_account_feature_line(line, product_name):
            index += 1
            continue

        next_line = lines[index + 1] if index + 1 < len(lines) else ""

        if line.endswith(":") and next_line and not should_stop_account_feature_collection(next_line):
            bullets.append(f"{line.rstrip(':')}: {next_line}")
            index += 2
        else:
            bullets.append(line)
            index += 1

        if len(bullets) >= max_bullets:
            break

    return bullets


def get_account_product_page_text(product):
    website_information = get_website_information_by_page_names([product["page_name"]])
    page_text = get_content_from_website_information(website_information)

    if page_text:
        return page_text

    try:
        page_text = get_text_from_website(product["url"])

        if page_text:
            save_website_text(
                page_name=product["page_name"],
                page_url=product["url"],
                page_text=page_text,
            )

    except Exception:
        return ""

    return page_text


def build_specific_account_reply(product):
    page_text = get_account_product_page_text(product)

    if product["category"] == "sme_deposit":
        section_text = slice_sme_account_section(page_text, product["name"])
    else:
        section_text = slice_retail_account_section(page_text, product["name"])

    bullets = build_account_feature_bullets(section_text, product["name"])

    if not bullets:
        return (
            f"{product['name']} details:\n\n"
            f"Link: {product['url']}"
        )

    bullet_text = "\n".join(f"- {bullet}" for bullet in bullets)

    return (
        f"{product['name']} features:\n\n"
        f"{bullet_text}\n\n"
        f"Link: {product['url']}"
    )


def build_account_router_reply(user_message, intent, history):
    product = detect_specific_account_product(user_message)

    if product:
        if is_document_question(user_message):
            return ""

        return build_specific_account_reply(product)

    if is_account_feature_follow_up(user_message):
        product = detect_account_product_from_history(history)

        if product:
            return build_specific_account_reply(product)

    segment = detect_account_segment(user_message)
    category = detect_account_category(user_message)
    is_broad_account_question = is_broad_account_opening_question(user_message)
    account_context_words = [
        "account",
        "accounts",
        "deposit",
        "deposits",
        "dps",
        "fd",
        "fdr",
        "saving",
        "savings",
    ]
    has_account_context = contains_any_word(
        normalize_loan_lookup_text(user_message),
        account_context_words,
    )

    if (
        intent in ["account_information", "deposit_information", "student_banking"]
        or is_broad_account_question
        or has_account_context
    ):
        if segment:
            return build_account_segment_reply(segment)

        if category:
            return build_account_category_reply(category)

        if is_broad_account_question:
            return ACCOUNT_CATEGORY_QUESTION

    if is_account_category_follow_up(user_message, history):
        if segment:
            return build_account_segment_reply(segment)

        return build_account_category_reply(category)

    return ""


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
    {
        "page_url": "https://www.ebl.com.bd/retail/EBL-Student-Banking",
        "allowed_paths": [
            "/student-banking/",
            "/islamic/deposit/",
        ],
    },
    {
        "page_url": "https://www.ebl.com.bd/islamicbanking",
        "allowed_paths": [
            "/islamic/",
            "/islamicbanking",
            "/islamic-retail-finance/",
        ],
    },
    {
        "page_url": "https://www.ebl.com.bd/retail/ebl-insta-banking",
        "allowed_paths": [
            "/retail/",
            "/retail-digital/",
            "/retail-ecommerce/",
            "/priority/",
            "/powerbanking",
            "/ebl-super-saver",
            "/agentbanking",
        ],
    },
]

MAX_DISCOVERED_PAGES = 180


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
        "page_name": "EBL Missed Call Alert Service Page",
        "page_url": "https://www.ebl.com.bd/retail-digital/ebl-missed-call-alert-service",
    },
    {
        "page_name": "EBL 365 PLUS Page",
        "page_url": "https://www.ebl.com.bd/retail-digital/ebl-365-plus",
    },
    {
        "page_name": "EBL SKYPAY Page",
        "page_url": "https://www.ebl.com.bd/retail-ecommerce/ebl-skypay",
    },
    {
        "page_name": "EBL Insta Account Branch Page",
        "page_url": "https://www.ebl.com.bd/retail/ebl-insta-account",
    },
    {
        "page_name": "EBL Insta Banking Online Page",
        "page_url": "https://www.ebl.com.bd/retail/ebl-insta-banking",
    },
    {
        "page_name": "EBL Priority Banking Page",
        "page_url": "https://www.ebl.com.bd/priority/",
    },
    {
        "page_name": "EBL Power Banking Page",
        "page_url": "https://www.ebl.com.bd/powerbanking",
    },
    {
        "page_name": "EBL Super Saver Page",
        "page_url": "https://www.ebl.com.bd/ebl-super-saver",
    },
    {
        "page_name": "EBL Women Banking Page",
        "page_url": "https://www.ebl.com.bd/retail/Women-Banking",
    },
    {
        "page_name": "EBL Agent Banking Page",
        "page_url": "https://www.ebl.com.bd/agentbanking",
    },
    {
        "page_name": "EBL Payroll Banking Page",
        "page_url": "https://www.ebl.com.bd/retail/EBL-Payroll-Banking",
    },
    {
        "page_name": "EBL Student Banking Page",
        "page_url": "https://www.ebl.com.bd/retail/EBL-Student-Banking",
    },
    {
        "page_name": "EBL Junior Savings Account Page",
        "page_url": "https://www.ebl.com.bd/student-banking/EBL-Junior",
    },
    {
        "page_name": "EBL Campus Account Page",
        "page_url": "https://www.ebl.com.bd/student-banking/EBL-Campus-Account",
    },
    {
        "page_name": "EBL Student File Services Page",
        "page_url": "https://www.ebl.com.bd/student-banking/EBL-Student-File-Services",
    },
    {
        "page_name": "EBL Child Future Plan Page",
        "page_url": "https://www.ebl.com.bd/student-banking/EBL-Child-Future-Plan",
    },
    {
        "page_name": "EBL Aspire Scheme Page",
        "page_url": "https://www.ebl.com.bd/student-banking/EBL-Aspire-Scheme",
    },
    {
        "page_name": "EBL Little Star Page",
        "page_url": "https://www.ebl.com.bd/student-banking/ebl-little-star",
    },
    {
        "page_name": "EBL Bancassurance Page",
        "page_url": "https://www.ebl.com.bd/retail/ebl-bancassurance",
    },
    {
        "page_name": "EBL Retail Alliance Page",
        "page_url": "https://www.ebl.com.bd/retail/ebl-retail-propositions",
    },
    {
        "page_name": "EBL Islamic Banking Page",
        "page_url": "https://www.ebl.com.bd/islamicbanking",
    },
    {
        "page_name": "EBL Shariah Committee Page",
        "page_url": "https://www.ebl.com.bd/islamic/member_ssc",
    },
    {
        "page_name": "EBL Islamic Retail Finance Page",
        "page_url": "https://www.ebl.com.bd/islamic/islamic-retail-finance",
    },
    {
        "page_name": "EBL Islamic SME Finance Page",
        "page_url": "https://www.ebl.com.bd/islamic/islamic-sme-finance",
    },
    {
        "page_name": "EBL Islamic Corporate Finance Page",
        "page_url": "https://www.ebl.com.bd/islamic/islamic-corporate-finance",
    },
    {
        "page_name": "EBL Islamic Cards Page",
        "page_url": "https://www.ebl.com.bd/islamic/islamic-cards",
    },
    {
        "page_name": "EBL Islamic Profit Distribution Page",
        "page_url": "https://www.ebl.com.bd/islamic/profit-distribution",
    },
    {
        "page_name": "EBL Islamic Notice Page",
        "page_url": "https://www.ebl.com.bd/islamic/notice",
    },
    {
        "page_name": "EBL Islamic Home Finance Page",
        "page_url": "https://www.ebl.com.bd/islamic-retail-finance/home-finance/",
    },
    {
        "page_name": "EBL Islamic Auto Finance Page",
        "page_url": "https://www.ebl.com.bd/islamic-retail-finance/auto-finance/",
    },
    {
        "page_name": "EBL Islamic Current Account Page",
        "page_url": "https://www.ebl.com.bd/islamic/deposit/ebl-islamic-current-account",
    },
    {
        "page_name": "EBL Islamic SND Account Page",
        "page_url": "https://www.ebl.com.bd/islamic/deposit/ebl-islamic-snd-account",
    },
    {
        "page_name": "EBL Speed Islamic SND Page",
        "page_url": "https://www.ebl.com.bd/islamic/deposit/ebl-speed-islamic-snd",
    },
    {
        "page_name": "EBL High Performance Islamic Account Page",
        "page_url": "https://www.ebl.com.bd/islamic/deposit/ebl-high-performance-islamic-account",
    },
    {
        "page_name": "EBL Power Islamic Savings Account Page",
        "page_url": "https://www.ebl.com.bd/islamic/deposit/ebl-power-islamic-savings-account",
    },
    {
        "page_name": "EBL Executive Islamic Savings Account Page",
        "page_url": "https://www.ebl.com.bd/islamic/deposit/ebl-executive-islamic-savings-account-payroll-account",
    },
    {
        "page_name": "EBL Women's Islamic Savings Account Page",
        "page_url": "https://www.ebl.com.bd/islamic/deposit/ebl-womens-islamic-savings-account",
    },
    {
        "page_name": "EBL Campus Islamic Account Page",
        "page_url": "https://www.ebl.com.bd/islamic/deposit/ebl-campus-islamic-account",
    },
    {
        "page_name": "EBL Junior Saver's Islamic Account Page",
        "page_url": "https://www.ebl.com.bd/islamic/deposit/ebl-junior-savers-islamic-account",
    },
    {
        "page_name": "EBL Islamic Term Deposit Account Page",
        "page_url": "https://www.ebl.com.bd/islamic/deposit/ebl-islamic-term-deposit-account",
    },
    {
        "page_name": "EBL Islamic Monthly Profit Scheme Page",
        "page_url": "https://www.ebl.com.bd/islamic/deposit/ebl-islamic-monthly-profit-scheme",
    },
    {
        "page_name": "EBL Islamic DPS Account Page",
        "page_url": "https://www.ebl.com.bd/islamic/deposit/ebl-islamic-dps-accounts",
    },
    {
        "page_name": "EBL Islamic Visa Platinum Debit Card Page",
        "page_url": "https://www.ebl.com.bd/islamic/eblcard/ebl-islamic-visa-platinum-debit-card",
    },
    {
        "page_name": "EBL Islamic Visa Prepaid Card Page",
        "page_url": "https://www.ebl.com.bd/islamic/eblcard/ebl-islamic-visa-prepaid-card",
    },
    {
        "page_name": "EBL Islamic Priority Visa Signature Debit Card Page",
        "page_url": "https://www.ebl.com.bd/islamic/eblcard/ebl-islamic-priority-visa-signature-debit-card",
    },
    {
        "page_name": "EBL Islamic Women's Platinum Debit Card Page",
        "page_url": "https://www.ebl.com.bd/islamic/eblcard/islamic-women-platinum-debit-card",
    },
    {
        "page_name": "EBL Contact Page",
        "page_url": "https://www.ebl.com.bd/contact",
    },
    {
        "page_name": "EBL Locator Page",
        "page_url": "https://www.ebl.com.bd/branches",
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

    if intent == "branch_locator":
        return save_and_build_response(
            session_id=session_id,
            user_message=user_message,
            reply=get_branch_locator_reply(),
            source="branch-locator-agent",
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

    loan_router_reply = build_loan_router_reply(user_message, intent, history)

    if loan_router_reply:
        return save_and_build_response(
            session_id=session_id,
            user_message=user_message,
            reply=loan_router_reply,
            source="loan-router",
            status="answered",
        )

    account_router_reply = build_account_router_reply(user_message, intent, history)

    if account_router_reply:
        return save_and_build_response(
            session_id=session_id,
            user_message=user_message,
            reply=account_router_reply,
            source="account-router",
            status="answered",
        )

    if intent == "retail_banking":
        return save_and_build_response(
            session_id=session_id,
            user_message=user_message,
            reply=build_retail_banking_overview_reply(),
            source="retail-banking-router",
            status="answered",
        )

    if intent == "islamic_banking":
        return save_and_build_response(
            session_id=session_id,
            user_message=user_message,
            reply=build_islamic_banking_overview_reply(),
            source="islamic-banking-router",
            status="answered",
        )

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
