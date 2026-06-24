"""Backend entrypoint."""  #starting file for the backend 
from fastapi import FastAPI #import FastAPI framework to create the backend API
from fastapi.middleware.cors import CORSMiddleware #import middleware to handle CORS  which allows the frontend to communicate with the backend without issues

from schemas import ChatRequest, ChatResponse #imports the request and response models (what data should be sent to the backend and what data the backend should return)
from safety import contains_sensitive_data, get_safety_response #imports sensitive data checker and warning response
from groq_client import generate_groq_customer_service_reply #import the function that sens the user's safe message to Groq and gets an AI reply
from database import save_chat, get_chat_history, get_website_information, save_website_text
from website_scraper import get_text_from_website


ERROR_REPLY = "Sorry, I could not process that request right now. Please try again later." #error message return to the user if Groq LLM fails 


app = FastAPI( #creates the FastAPI app with title, description, and version
    title="Eastern Bank AI Chatbot API", 
    description="FastAPI backend for Eastern Bank AI chatbot", 
    version="1.0.0", 
)

origins = [
    "http://localhost:3000", #list of frontend URLs allowed to access the backend 
    "http://127.0.0.1:3000",
]

app.add_middleware( #activate CORS settings so browser requests from frontend allowed to access the backend without CORS errors
    CORSMiddleware, 
    allow_origins=origins, 
    allow_credentials=True, 
    allow_methods=["*"],  
    allow_headers=["*"], #allows all HTTP methods and headers in requests from the allowed origins
)


@app.get("/") #creates GET / endpoint to check if the backend is running
def root(): 
    return {
        "message": "Eastern AI Chatbot API is running"
    }


@app.get("/health") #creates GET/health endpoint for backend status checking
def health_check():
    return {
        "status": "ok",
        "service": "eastern-bank-plc-chatbot-backend"
    }


@app.post("/chat", response_model=ChatResponse) #accepts post request and return data
def chat(request: ChatRequest): #func runs when frontend sends a text 
    user_message = request.message.strip() #remove extra spaces from start to end of a text 
    session_id = request.session_id or "default-session" 

    if contains_sensitive_data(user_message): #unsafe data otp, pass, pin
        safety_reply = get_safety_response() #gets warning text

        save_chat( #saves blocked text & warning into database
            session_id=session_id,
            user_message=user_message,
            bot_reply=safety_reply,
            source="safety-filter",
            blocked=True, #marked the text was blocked
            status="blocked" #stores the result as blocked in database
        )

        return ChatResponse( 
            reply=safety_reply,
            source="safety-filter",
            blocked=True
        )

    try:
        history = get_chat_history(session_id)  #loads old text history for the same session
        website_info = get_website_information()

        reply = generate_groq_customer_service_reply( #sends current user text and previous history to groq
            user_message,
            history,
            website_info
        )

        save_chat( #saves successful user text & bot reply into database
            session_id=session_id,
            user_message=user_message,
            bot_reply=reply,
            source="groq-llm",
            blocked=False, #text wasn't block
            status="answered"
        )

        return ChatResponse(
            reply=reply,
            source="groq-llm",
            blocked=False
        )

    except Exception as e: #if any error happens
        print("Groq error:", e) #real error in the backend terminal for debugging

        error_reply = "Sorry, I could not process your request right now. Please try again later."

        save_chat( #saves failed request & error text  in database
            session_id=session_id,
            user_message=user_message,
            bot_reply=error_reply,
            source="groq-error",
            blocked=False,
            status="error"
        )

        return ChatResponse( #sends error text to the frontend 
            reply=error_reply,
            source="groq-error",
            blocked=False
        )

@app.post("/refresh-website-info")
def refresh_website_info():
    page_url = "http://www.ebl.com.bd/"
    page_name = "Eastern Bank PLC Website"

    page_text = get_text_from_website(page_url)

    save_website_text(
        page_name=page_name,
        page_url=page_url,
        page_text=page_text
    )

    return {
        "message": "Website information refreshed successfully",
        "characters_saved": len(page_text)
    }