# core/auth.py

from fastapi import Request
from orbmem.utils.exceptions import AuthError
from orbmem.core.config import load_config

def validate_api_key(request: Request):
    """
    Validates API key using latest .env values.
    Reloads config every time to avoid stale values.
    """
    config = load_config()  # <-- reloads fresh env each request

    auth_header = request.headers.get("Authorization")
    if not auth_header:
        raise AuthError("Missing Authorization header")

    if not auth_header.startswith("Bearer "):
        raise AuthError("Invalid Authorization format. Use: Bearer <API_KEY>")

    api_key = auth_header.replace("Bearer ", "").strip()

    if api_key not in config.api.api_keys:
        raise AuthError("Invalid API key. Access denied.")

    return True
