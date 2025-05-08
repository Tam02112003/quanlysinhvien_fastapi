from fastapi import Request, HTTPException
from functools import wraps
from jose import jwt, JWTError

import os
from dotenv import load_dotenv
load_dotenv()
ALGORITHM= os.getenv("ALGORITHM")
SECRET_KEY= os.getenv("SECRET_KEY")

def auth_required(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        request = kwargs.get("request")
        if not request:
            request = next((a for a in args if isinstance(a, Request)), None)
        if not request:
            raise HTTPException(status_code=400, detail="Request object not found")

        # Lấy token từ Authorization header
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Missing or invalid Authorization header")

        token = auth_header.split(" ")[1]

        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            user_email = payload.get("sub")
            if not user_email:
                raise HTTPException(status_code=401, detail="Invalid token content")
            request.state.user = user_email
        except JWTError:
            raise HTTPException(status_code=401, detail="Invalid token")

        return await func(*args, **kwargs)

    return wrapper
