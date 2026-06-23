from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt

from app.config import settings

bearer = HTTPBearer()


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(bearer)) -> dict:
    try:
        payload = jwt.decode(
            credentials.credentials,
            settings.jwt_secret,
            algorithms=[settings.jwt_algorithm],
        )
        user_id: int = payload.get("user_id")
        role: str = payload.get("role")
        if user_id is None or role is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return {"user_id": user_id, "role": role}
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


def require_customer(user: dict = Depends(get_current_user)) -> dict:
    if user["role"] != "customer":
        raise HTTPException(status_code=403, detail="Customer role required")
    return user


def require_seller(user: dict = Depends(get_current_user)) -> dict:
    if user["role"] != "seller":
        raise HTTPException(status_code=403, detail="Seller role required")
    return user
