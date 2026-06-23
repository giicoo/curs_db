from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from typing import Optional

from app.database import get_pool
from app.auth.deps import get_current_user, require_seller

router = APIRouter()


class ProductCreate(BaseModel):
    type_id: int
    name: str
    price: float
    stock_quantity: int = 0


class ProductUpdate(BaseModel):
    type_id: Optional[int] = None
    name: Optional[str] = None
    price: Optional[float] = None
    stock_quantity: Optional[int] = None


@router.get("/product-types")
async def get_product_types(pool=Depends(get_pool)):
    async with pool.acquire() as conn:
        rows = await conn.fetch("SELECT id, name FROM product_types ORDER BY name")
    return [dict(r) for r in rows]


@router.get("/products/low-stock")
async def low_stock(
    threshold: int = Query(10, ge=0),
    current_user: dict = Depends(require_seller),
    pool=Depends(get_pool),
):
    async with pool.acquire() as conn:
        seller = await conn.fetchrow(
            "SELECT id FROM sellers WHERE user_id=$1", current_user["user_id"]
        )
        if not seller:
            raise HTTPException(404, "Seller profile not found")

        rows = await conn.fetch(
            """
            SELECT p.id, p.name, p.price, p.stock_quantity, pt.name AS type_name
            FROM products p
            JOIN product_types pt ON pt.id = p.type_id
            WHERE p.seller_id=$1 AND p.stock_quantity <= $2
            ORDER BY p.stock_quantity
            """,
            seller["id"], threshold,
        )
    return [
        {**dict(r), "price": float(r["price"])} for r in rows
    ]


@router.get("/products/{product_id}")
async def get_product(product_id: int, pool=Depends(get_pool)):
    async with pool.acquire() as conn:
        product = await conn.fetchrow(
            """
            SELECT p.id, p.name, p.price, p.stock_quantity,
                   p.type_id, pt.name AS type_name,
                   p.seller_id, s.name AS seller_name,
                   ROUND(AVG(r.rating)::numeric, 2) AS avg_rating,
                   COUNT(r.id) AS review_count
            FROM products p
            JOIN product_types pt ON pt.id = p.type_id
            JOIN sellers s ON s.id = p.seller_id
            LEFT JOIN reviews r ON r.product_id = p.id
            WHERE p.id=$1
            GROUP BY p.id, pt.name, s.name
            """,
            product_id,
        )
        if not product:
            raise HTTPException(404, "Product not found")

        reviews = await conn.fetch(
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

    return {
        **dict(product),
        "price": float(product["price"]),
        "avg_rating": float(product["avg_rating"]) if product["avg_rating"] else None,
        "reviews": [
            {**dict(r), "created_at": str(r["created_at"])} for r in reviews
        ],
    }


@router.post("/products", status_code=201)
async def create_product(
    body: ProductCreate,
    current_user: dict = Depends(require_seller),
    pool=Depends(get_pool),
):
    async with pool.acquire() as conn:
        seller = await conn.fetchrow(
            "SELECT id FROM sellers WHERE user_id=$1", current_user["user_id"]
        )
        if not seller:
            raise HTTPException(404, "Seller profile not found")

        product = await conn.fetchrow(
            """
            INSERT INTO products (seller_id, type_id, name, price, stock_quantity)
            VALUES ($1,$2,$3,$4,$5) RETURNING id
            """,
            seller["id"], body.type_id, body.name, body.price, body.stock_quantity,
        )
    return {"id": product["id"]}


@router.put("/products/{product_id}")
async def update_product(
    product_id: int,
    body: ProductUpdate,
    current_user: dict = Depends(require_seller),
    pool=Depends(get_pool),
):
    async with pool.acquire() as conn:
        seller = await conn.fetchrow(
            "SELECT id FROM sellers WHERE user_id=$1", current_user["user_id"]
        )
        if not seller:
            raise HTTPException(404, "Seller profile not found")

        existing = await conn.fetchrow(
            "SELECT seller_id FROM products WHERE id=$1", product_id
        )
        if not existing:
            raise HTTPException(404, "Product not found")
        if existing["seller_id"] != seller["id"]:
            raise HTTPException(403, "Not your product")

        updates = []
        params = []
        idx = 1
        for field, value in body.model_dump(exclude_none=True).items():
            updates.append(f"{field}=${idx}")
            params.append(value)
            idx += 1

        if not updates:
            raise HTTPException(400, "Nothing to update")

        params.append(product_id)
        await conn.execute(
            f"UPDATE products SET {', '.join(updates)} WHERE id=${idx}",
            *params,
        )
    return {"ok": True}


@router.delete("/products/{product_id}", status_code=204)
async def delete_product(
    product_id: int,
    current_user: dict = Depends(require_seller),
    pool=Depends(get_pool),
):
    async with pool.acquire() as conn:
        seller = await conn.fetchrow(
            "SELECT id FROM sellers WHERE user_id=$1", current_user["user_id"]
        )
        if not seller:
            raise HTTPException(404, "Seller profile not found")

        existing = await conn.fetchrow(
            "SELECT seller_id FROM products WHERE id=$1", product_id
        )
        if not existing:
            raise HTTPException(404, "Product not found")
        if existing["seller_id"] != seller["id"]:
            raise HTTPException(403, "Not your product")

        await conn.execute("DELETE FROM products WHERE id=$1", product_id)
