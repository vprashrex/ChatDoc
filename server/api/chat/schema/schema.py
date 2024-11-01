from pydantic import BaseModel

class Message(BaseModel):
    userId: str
    content: str
    sender: str

class AIMessage(BaseModel):
    content: str
    sender: str = "ai"