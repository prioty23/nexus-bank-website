from pydantic import BaseModel, Field #create data models and add rules min max length.
from typing import Optional #value can be there or missing


class ChatRequest(BaseModel):  #what frontend sends
    message: str = Field(..., min_length=1, max_length=1000) #message is required must be a string can't be empty max 1000 char.
    session_id: Optional[str] = None


class ChatResponse(BaseModel): #what backend returns.
    reply: str   #must a text from chatbot
    source: str = "fastapi"          #where the reply came from.
    blocked: bool = False   #user text blocked by saftey filter.