"""Backend entrypoint."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from groq_client import generate_groq_customer_service_reply
from schemas import ChatRequest, ChatResponse
from safety import contains_sensitive_data, get_safety_response

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
    # Step 1: Get the user's message from the request.
    user_message = request.message.strip()

    # Step 2: Stop the chat if the user shares sensitive banking information.
    if contains_sensitive_data(user_message):
        return ChatResponse(
            reply=get_safety_response(),
            source="safety-filter",
            blocked=True
        )

    # Step 3: If the message is safe, ask Groq to create the chatbot reply.
    try:
        reply = generate_groq_customer_service_reply(user_message)

        return ChatResponse(
            reply=reply,
            source="groq-llm",
            blocked=False
        )

    except Exception as error:
        print("Groq error:", error)

        return ChatResponse(
            reply=ERROR_REPLY,
            source="groq-error",
            blocked=False
        )
