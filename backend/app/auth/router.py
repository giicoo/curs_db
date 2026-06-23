from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException
from jose import jwt
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

from app.config import settings
from app.database import get_pool
from app.auth.schemas import RegisterRequest, LoginRequest, TokenResponse
from app.auth.deps import get_current_user

router = APIRouter()
ph = PasswordHasher()


def _make_token(user_id: int, role: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.jwt_expire_minutes)
    return jwt.encode(
        {"user_id": user_id, "role": role, "exp": expire},
        settings.jwt_secret,
        algorithm=settings.jwt_algorithm,
    )


@router.post("/register", response_model=TokenResponse)
async def register(body: RegisterRequest, pool=Depends(get_pool)):
    async with pool.acquire() as conn:
        async with conn.transaction():
            existing = await conn.fetchrow(
                "SELECT id FROM users WHERE login=$1 OR email=$2",
                body.login, body.email,
            )
            if existing:
                raise HTTPException(400, "Login or email already taken")

            password_hash = ph.hash(body.password)
            user = await conn.fetchrow(
                "INSERT INTO users (login, password_hash, email) VALUES ($1,$2,$3) RETURNING id",
                body.login, password_hash, body.email,
            )
            user_id = user["id"]

            if body.role == "customer":
                if not body.last_name or not body.first_name:
                    raise HTTPException(400, "last_name and first_name are required for customer")
                await conn.execute(
                    "INSERT INTO customers (user_id, last_name, first_name, phone, delivery_address) VALUES ($1,$2,$3,$4,$5)",
                    user_id, body.last_name, body.first_name, body.phone, body.delivery_address,
                )
            elif body.role == "seller":
                if not body.seller_name:
                    raise HTTPException(400, "seller_name is required for seller")
                await conn.execute(
                    "INSERT INTO sellers (user_id, name, description) VALUES ($1,$2,$3)",
                    user_id, body.seller_name, body.description,
                )
            else:
                raise HTTPException(400, "role must be 'customer' or 'seller'")

    return TokenResponse(access_token=_make_token(user_id, body.role))


@router.post("/login", response_model=TokenResponse)
async def login(body: LoginRequest, pool=Depends(get_pool)):
    async with pool.acquire() as conn:
        user = await conn.fetchrow(
            "SELECT id, password_hash FROM users WHERE login=$1",
            body.login,
        )
        if not user:
            raise HTTPException(401, "Invalid credentials")

        try:
            ph.verify(user["password_hash"], body.password)
        except VerifyMismatchError:
            raise HTTPException(401, "Invalid credentials")

        customer = await conn.fetchrow("SELECT id FROM customers WHERE user_id=$1", user["id"])
        if customer:
            role = "customer"
        else:
            seller = await conn.fetchrow("SELECT id FROM sellers WHERE user_id=$1", user["id"])
            if seller:
                role = "seller"
            else:
                raise HTTPException(500, "User has no role assigned")

    return TokenResponse(access_token=_make_token(user["id"], role))


@router.get("/me")
async def me(current_user: dict = Depends(get_current_user), pool=Depends(get_pool)):
    async with pool.acquire() as conn:
        user = await conn.fetchrow(
            "SELECT id, login, email, registered_at FROM users WHERE id=$1",
            current_user["user_id"],
        )
        profile = {}
        if current_user["role"] == "customer":
            row = await conn.fetchrow(
                "SELECT id, last_name, first_name, phone, delivery_address FROM customers WHERE user_id=$1",
                current_user["user_id"],
            )
            if row:
                profile = dict(row)
        else:
            row = await conn.fetchrow(
                "SELECT id, name, description, registered_at FROM sellers WHERE user_id=$1",
                current_user["user_id"],
            )
            if row:
                profile = {k: (str(v) if hasattr(v, "isoformat") else v) for k, v in dict(row).items()}

        return {
            "id": user["id"],
            "login": user["login"],
            "email": user["email"],
            "registered_at": user["registered_at"].isoformat(),
            "role": current_user["role"],
            "profile": profile,
        }
