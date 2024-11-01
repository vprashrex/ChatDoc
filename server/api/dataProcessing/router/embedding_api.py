from fastapi import APIRouter
from fastapi.requests import Request

from fastapi import APIRouter, File, UploadFile, HTTPException, Depends
from fastapi.requests import Request
from fastapi.responses import JSONResponse
import os
import shutil
from pathlib import Path
from api.dataProcessing.building_blocks.embedding import Embedding
import redis

router = APIRouter()
redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)


def create_user_directory(user_id: str, base_dir: str = "data/input/") -> Path:
    user_dir = Path(base_dir) / user_id
    user_dir.mkdir(parents=True, exist_ok=True)
    return user_dir

@router.post("/add/document")
async def add_document(request: Request, file: UploadFile = File(...)):
    user_id = request.headers.get('user_id') 
    allowed_extensions = {".pdf", ".csv", ".pptx", ".docx", ".txt"}
    file_extension = Path(file.filename).suffix
    if file_extension not in allowed_extensions:
        raise HTTPException(status_code=400, detail="Invalid file type")

    user_dir = create_user_directory(user_id)
    file_path = user_dir / file.filename

    try:
        with file_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        redis_client.lpush(f"user_files:{user_id}", file.filename)
        Embedding(user_id=user_id)

        return JSONResponse(content={"message": "File uploaded and processed successfully"})
    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail="An error occurred during processing")
    

@router.get("/get/user_files")
async def get_user_files(request: Request):
    user_id = request.headers.get('user_id')
    files = redis_client.lrange(f"user_files:{user_id}", 0, -1)
    files = [file.decode('utf-8') for file in files]
    return JSONResponse(content={"user_id": user_id, "files": files})

