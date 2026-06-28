from typing import Optional
from pydantic import BaseModel


class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None


class ChatResponse(BaseModel):
    reply: str
    source: str
    blocked: bool = False


class ComplaintStatusUpdateRequest(BaseModel):
    status: str