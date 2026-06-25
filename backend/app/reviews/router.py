from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from typing import Optional

from app.database import get_pool
from app.auth.deps import require_customer

router = APIRouter()


class ReviewCreate(BaseModel):
    product_id: int
    rating: int
    comment_text: Optional[str] = None


@router.post("", status_code=201)
async def create_review(
    body: ReviewCreate,
    current_user: dict = Depends(require_customer),
    pool=Depends(get_pool),
):
    if not (1 <= body.rating <= 5):
        raise HTTPException(400, "Rating must be between 1 and 5")

    async with pool.acquire() as conn:
        customer = await conn.fetchrow(
            "SELECT id FROM customers WHERE user_id=$1", current_user["user_id"]
        )
        if not customer:
            raise HTTPException(404, "Customer profile not found")

        already_reviewed = await conn.fetchval(
            "SELECT EXISTS(SELECT 1 FROM reviews WHERE customer_id=$1 AND product_id=$2)",
            customer["id"], body.product_id,
        )
        if already_reviewed:
            raise HTTPException(400, "You have already reviewed this product")

        review = await conn.fetchrow(
            "INSERT INTO reviews (customer_id, product_id, rating, comment_text) VALUES ($1,$2,$3,$4) RETURNING id",
            customer["id"], body.product_id, body.rating, body.comment_text,
        )

    return {"id": review["id"]}


@router.get("")
async def list_reviews(
    product_id: Optional[int] = Query(None),
    pool=Depends(get_pool),
):
    if product_id is None:
        raise HTTPException(400, "product_id is required")

    async with pool.acquire() as conn:
        rows = await conn.fetch(
            """
            SELECT r.id, r.rating, r.comment_text, r.created_at,
                   c.first_name, c.last_name
            FROM reviews r
            JOIN customers c ON c.id = r.customer_id
            WHERE r.product_id=$1
            ORDER BY r.created_at DESC
            """,
            product_id,
        )

    return [
        {**dict(r), "created_at": str(r["created_at"])} for r in rows
    ]
