from pydantic import BaseModel


class ChatRequest(BaseModel):
    message: str
    stock_id: str = None