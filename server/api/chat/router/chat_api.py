from fastapi import APIRouter
from pydantic import BaseModel
from typing import List
from api.chat.building_blocks.llm import LanguageModelProcess
import aioredis
import json
from api.chat.schema.schema import Message,AIMessage

router = APIRouter()
llm = LanguageModelProcess()
redis = aioredis.from_url("redis://localhost:6379", decode_responses=True)

@router.post("/send_message", response_model=AIMessage)
async def send_message(message: Message):
    try:
        print(message.content)
        response = llm.generate(message.userId, message.content)
        ai_message = AIMessage(
            content=response,
            sender="ai"
        )

        await redis.rpush(f"chat_history:{message.userId}", json.dumps({"content": message.content, "sender": "user"}))
        await redis.rpush(f"chat_history:{message.userId}", json.dumps({"content": response, "sender": "ai"}))
        
        return ai_message
    except Exception as e:
        print(f"Error : {e}")

@router.get("/get_chat_history/{userId}", response_model=List[Message])
async def get_chat_history(userId: str):
    messages = await redis.lrange(f"chat_history:{userId}", 0, -1)

    if not messages:
        return []
    
    parsed_messages = []
    for msg in messages:
        if msg: 
            try:
                message_data = json.loads(msg)
                parsed_messages.append({
                    "userId": userId,  
                    **message_data  
                })
            except json.JSONDecodeError as e:
                print(f"JSON decoding error: {e} for message: {msg}")

    return parsed_messages
