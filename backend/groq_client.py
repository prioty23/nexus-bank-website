import os  #read env variables from os
from dotenv import load_dotenv #imports functions
from groq import Groq 

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY") #reads secret groq api key from .env
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant") #reads model name from .env

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

def generate_groq_customer_service_reply(message: str, history=None) -> str: #This function sends the user’s message to Groq and returns the AI reply it also accepts old chat history if available.
    if not GROQ_API_KEY:  #API key exists or not
        raise ValueError("GROQ_API_KEY is missing in .env") #if missing stop function and show error

    if history is None: #checks old chat history was given or not.
        history = [] #empty list if no history is given

    client = Groq(api_key=GROQ_API_KEY)  #creates a connection to groq using secret api key

    messages = [
        {
            "role": "system", #list of text that will send to groq
            "content": SYSTEM_PROMPT
        }
    ]

    messages.extend(history)

    messages.append({
        "role": "user", #text from user
        "content": message
    })

    chat_completion = client.chat.completions.create( #sends all text to groq to generate
        model=GROQ_MODEL,
        messages=messages,
        temperature=0.4, #controls creativety. lower value means more stable and focused answers
        max_completion_tokens=300, #how long AI can reply
    )

    return chat_completion.choices[0].message.content #takes the final reply text from Groq and returns it