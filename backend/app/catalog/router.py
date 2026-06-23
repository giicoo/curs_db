from fastapi import APIRouter, Depends, Query
from typing import Optional

from app.database import get_pool

router = APIRouter()


@router.get("")
async def get_catalog(
    type_id: Optional[int] = None,
    seller_id: Optional[int] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    search: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    pool=Depends(get_pool),
):
    filter_parts: list[str] = []
    filter_params: list = []
    idx = 1

    if type_id is not None:
        filter_parts.append(f"p.type_id = ${idx}")
        filter_params.append(type_id)
        idx += 1
    if seller_id is not None:
        filter_parts.append(f"p.seller_id = ${idx}")
        filter_params.append(seller_id)
        idx += 1
    if min_price is not None:
        filter_parts.append(f"p.price >= ${idx}")
        filter_params.append(min_price)
        idx += 1
    if max_price is not None:
        filter_parts.append(f"p.price <= ${idx}")
        filter_params.append(max_price)
        idx += 1
    if search:
        filter_parts.append(f"p.name ILIKE ${idx}")
        filter_params.append(f"%{search}%")
        idx += 1

    where = ("WHERE " + " AND ".join(filter_parts)) if filter_parts else ""
    offset = (page - 1) * page_size

    query = f"""
        SELECT p.id, p.name, p.price, p.stock_quantity,
               p.type_id, pt.name AS type_name,
               p.seller_id, s.name AS seller_name,
               ROUND(AVG(r.rating)::numeric, 2) AS avg_rating,
               COUNT(r.id) AS review_count
        FROM products p
        JOIN product_types pt ON pt.id = p.type_id
        JOIN sellers s ON s.id = p.seller_id
        LEFT JOIN reviews r ON r.product_id = p.id
        {where}
        GROUP BY p.id, pt.name, s.name
        ORDER BY p.id
        LIMIT ${idx} OFFSET ${idx + 1}
    """

    count_query = f"SELECT COUNT(*) FROM products p {where}"

    async with pool.acquire() as conn:
        rows = await conn.fetch(query, *filter_params, page_size, offset)
        total = await conn.fetchval(count_query, *filter_params)

    return {
        "items": [
            {**dict(r), "price": float(r["price"]), "avg_rating": float(r["avg_rating"]) if r["avg_rating"] else None}
            for r in rows
        ],
        "total": total,
        "page": page,
        "page_size": page_size,
    }
