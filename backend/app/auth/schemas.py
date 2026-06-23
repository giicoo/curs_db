from pydantic import BaseModel
from typing import Optional


class RegisterRequest(BaseModel):
    login: str
    password: str
    email: str
    role: str  # "customer" or "seller"
    # Customer fields
    last_name: Optional[str] = None
    first_name: Optional[str] = None
    phone: Optional[str] = None
    delivery_address: Optional[str] = None
    # Seller fields
    seller_name: Optional[str] = None
    description: Optional[str] = None


class LoginRequest(BaseModel):
    login: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
