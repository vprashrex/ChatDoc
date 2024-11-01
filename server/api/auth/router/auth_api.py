from fastapi import HTTPException, Request, Response, APIRouter, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import JWTError, jwt
from fastapi.responses import JSONResponse
import redis
import json
import uuid
from api.auth.schema.schema import User,UserInDB,TokenData,Token

router = APIRouter()

SECRET_KEY = "your_secret_key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

redis_client = redis.Redis(host='localhost', port=6379, db=0)



def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_user_from_db(email: str):
    user = redis_client.get(f"user:{email}")
    if user:
        user_data = json.loads(user.decode('utf-8'))
        return UserInDB(email=user_data['email'], hashed_password=user_data['hashed_password'],user_id=user_data["user_id"])
    return None


async def authenticate_user(email: str, password: str):
    user = await get_user_from_db(email)
    if user and verify_password(password, user.hashed_password):
        return user
    return None


@router.post("/signup", status_code=status.HTTP_201_CREATED,response_model=Token)
async def signup(response: Response,user: User):
    user_exists = await get_user_from_db(user.email)
    if user_exists:
        return JSONResponse(content={"sucess":False},status_code=200)
    hashed_password = get_password_hash(user.password)
    user_id = str(uuid.uuid4())
    redis_client.set(f"user:{user.email}", json.dumps({"user_id":user_id,"email": user.email, "hashed_password": hashed_password}))
    access_token = create_access_token(data={"sub": user.email}, expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    response.set_cookie(key="access_token", value=access_token, httponly=True)
    return {"success":True,"message": "User registered successfully","access_token": access_token,"token_type": "bearer"}


@router.post("/login", response_model=Token)
async def login(response: Response, user: User):
    authenticated_user = await authenticate_user(user.email, user.password)
    if not authenticated_user:
        return JSONResponse(content={"success":False},status_code=200)
    access_token = create_access_token(data={"sub": user.email}, expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    response.set_cookie(key="access_token", value=access_token, httponly=True)
    return {
        "success": True,
        "access_token": access_token,
        "token_type": "bearer",
        "message": "Successfully Logged In!"
    }



@router.get("/verify", status_code=status.HTTP_200_OK)
async def get_current_user(request: Request):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    token = request.cookies.get("access_token")
    if token is None:
        raise credentials_exception

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = TokenData(email=email)
    except JWTError:
        raise credentials_exception

    user = await get_user_from_db(email=token_data.email)
    if user is None:
        raise credentials_exception

    return {"message": "User is verified", "email": email,"user_id":user.user_id}