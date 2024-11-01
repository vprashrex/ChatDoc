from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.dataProcessing.router import embedding_api
from api.chat.router import chat_api
from api.auth.router import auth_api

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],

)

@app.on_event("startup")
async def startup_event():
    print("Starting up...")


@app.get("/")
async def root():
    return {"message": "Chat Server is running"}

app.include_router(embedding_api.router, prefix="/embedding")
app.include_router(chat_api.router, prefix="/chat")
app.include_router(auth_api.router,prefix="/auth")
