import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")

SYSTEM_PROMPT = """
You are EBL AI Assistant, a professional customer service chatbot.

You help users with general questions about:
- accounts
- cards
- loans
- deposits
- digital banking
- offers
- branch and ATM information
- customer support

Rules:
- Keep answers short, clear, polite, and professional.
- Do not claim that you can access real customer accounts.
- Do not ask for OTP, PIN, password, CVV, full card number, or sensitive information.
- If the user has an account-specific issue, advise them to contact official EBL support or visit a branch.
- If you are not sure, give general guidance and suggest contacting support.
"""


def generate_groq_customer_service_reply(message: str) -> str:
    # The API key must stay in .env, not inside the code.
    if not GROQ_API_KEY:
        raise ValueError("GROQ_API_KEY is missing in .env")

    client = Groq(api_key=GROQ_API_KEY)

    # Send the user's message to Groq and ask for one assistant reply.
    response = client.chat.completions.create(
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
        temperature=0.4,
        max_completion_tokens=300,
    )

    return response.choices[0].message.content
