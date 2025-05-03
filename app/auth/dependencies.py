from fastapi import Security, HTTPException, status
from fastapi.security.api_key import APIKeyHeader
import os

API_KEY = os.getenv("BEARER_TOKEN")
api_key_header = APIKeyHeader(name="Authorization", auto_error=False)

def verify_token(api_key: str = Security(api_key_header)):
    if not api_key or not api_key.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or malformed Bearer token")

    token = api_key.split(" ")[1]
    if token != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid token")
