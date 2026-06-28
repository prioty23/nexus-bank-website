import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")


SYSTEM_PROMPT = """
You are a professional banking customer-service assistant.

You must answer like a real bank support officer.

Important behavior:
- Give direct answers.
- Do not sound like a website guide.
- Do not copy website menu text.
- Do not tell the user where to click unless the user asks for website navigation.
- Do not say: "I recommend visiting", "click on", "go to the website", "under Contact Us", "under Useful Links", or "browse the website".
- Do not include phone number or email unless the user directly asks for hotline, contact number, or email.
- Do not claim that you can access real customer accounts.
- Do not ask for OTP, PIN, password, CVV, full card number, or sensitive banking information.
- Do not promise refunds, approvals, account opening, or complaint resolution.
- Keep replies professional, structured, and easy to understand.

Contact information rule:
Never say [email protected].
Never say +88 09677716230.
Never say 09677716230.

For Eastern Bank PLC contact information, always use:
Hotline: 16230
From overseas: +8809677716230
General contact number: +8809666777325
Email: info@ebl-bd.com
"""


def generate_groq_customer_service_reply(
    message: str,
    history=None,
    website_info="",
    session_summary=""
) -> str:
    if not GROQ_API_KEY:
        raise ValueError("GROQ_API_KEY is missing in .env")

    if history is None:
        history = []

    client = Groq(api_key=GROQ_API_KEY)

    messages = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT
        }
    ]

    if website_info:
        messages.append({
            "role": "system",
            "content": f"""
Use the following banking website information only as background context.

Website information:
{website_info}

Answer style:

For account opening questions:
Reply in this structure:
1. Short direct answer.
2. General account opening options.
3. Required documents in bullet points.
4. Final note that requirements may vary by account type.

Example style:
"To open an account, customers need to choose the account type that matches their requirement, such as a savings, current, or deposit account.

General documents may include:
- Valid photo identification
- Recent passport-size photograph
- Address and contact details
- Nominee information
- Supporting documents depending on the account type

Final requirements may vary based on the selected account type and customer profile. Customers should contact official support or visit a branch for final verification."

For document questions:
Give only the document list in a clean bullet format.

For hotline/contact questions:
Give the contact information directly if available. Do not add website navigation instructions.

For card transaction problems:
Reply in this structure:
1. Explain that it may be a duplicate transaction, pending authorization, or settlement issue.
2. Ask the customer to check the transaction details.
3. Advise contacting official card support or visiting a branch for investigation.
4. Remind not to share OTP, PIN, CVV, or full card number.

Strictly avoid these phrases:
- I recommend visiting
- click on
- go to the website
- under Contact Us
- under Useful Links
- browse the website

If exact information is missing:
Say:
"Final requirements may vary depending on the account type and customer profile. Customers should contact official support or visit a branch for final verification."

Return only the final customer-facing answer.
"""
        })

    if session_summary:
        messages.append({
            "role": "system",
            "content": f"""
Previous conversation summary:
{session_summary}

Use this summary to remember older parts of the same conversation.
"""
        })

    messages.extend(history)

    messages.append({
        "role": "user",
        "content": message
    })

    chat_completion = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=messages,
        temperature=0,
        max_completion_tokens=350,
    )

    return chat_completion.choices[0].message.content


def update_conversation_summary(old_summary, user_message, bot_reply):
    if not GROQ_API_KEY:
        raise ValueError("GROQ_API_KEY is missing in .env")

    client = Groq(api_key=GROQ_API_KEY)

    messages = [
        {
            "role": "system",
            "content": """
You summarize banking chatbot conversations.

Keep the summary short and useful.

Remember:
- what the user asked
- important banking topics
- account, card, loan, deposit, support, or complaint details
- any important follow-up context

Do not include OTP, PIN, password, CVV, full card numbers, or sensitive banking information.
"""
        },
        {
            "role": "user",
            "content": f"""
Old summary:
{old_summary}

New user message:
{user_message}

New bot reply:
{bot_reply}

Write the updated summary.
"""
        }
    ]

    chat_completion = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=messages,
        temperature=0,
        max_completion_tokens=200,
    )

    return chat_completion.choices[0].message.content
