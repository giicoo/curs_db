from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional
from datetime import date, datetime, timezone

from app.database import get_pool
from app.auth.deps import get_current_user

router = APIRouter()


def _month_start(months_back: int) -> datetime:
    now = datetime.now(timezone.utc)
    m = now.month - months_back
    y = now.year
    while m <= 0:
        m += 12
        y -= 1
    return datetime(y, m, 1, tzinfo=timezone.utc)


@router.get("/revenue-by-month")
async def revenue_by_month(
    months: int = Query(12, ge=3, le=24),
    current_user: dict = Depends(get_current_user),
    pool=Depends(get_pool),
):
    start_date = _month_start(months)

    if current_user["role"] == "seller":
        async with pool.acquire() as conn:
            seller = await conn.fetchrow(
                "SELECT id FROM sellers WHERE user_id=$1", current_user["user_id"]
            )
        if not seller:
            return []

        query = """
            WITH month_series AS (
                SELECT generate_series(
                    DATE_TRUNC('month', $1::timestamptz),
                    DATE_TRUNC('month', NOW()),
                    INTERVAL '1 month'
                ) AS mo
            ),
            seller_data AS (
                SELECT
                    DATE_TRUNC('month', o.order_date) AS mo,
                    SUM(oi.quantity * oi.price_at_order) AS revenue,
                    COUNT(DISTINCT o.id) AS order_count,
                    SUM(oi.quantity) AS units_sold
                FROM order_items oi
                JOIN orders o ON o.id = oi.order_id
                JOIN products p ON p.id = oi.product_id
                WHERE p.seller_id = $2
                  AND o.order_date >= $1::timestamptz
                GROUP BY DATE_TRUNC('month', o.order_date)
            )
            SELECT
                TO_CHAR(ms.mo, 'YYYY-MM') AS month,
                COALESCE(sd.revenue, 0) AS revenue,
                COALESCE(sd.order_count, 0) AS order_count,
                COALESCE(sd.units_sold, 0) AS units_sold
            FROM month_series ms
            LEFT JOIN seller_data sd ON sd.mo = ms.mo
            ORDER BY ms.mo
        """
        async with pool.acquire() as conn:
            rows = await conn.fetch(query, start_date, seller["id"])
    else:
        query = """
            WITH month_series AS (
                SELECT generate_series(
                    DATE_TRUNC('month', $1::timestamptz),
                    DATE_TRUNC('month', NOW()),
                    INTERVAL '1 month'
                ) AS mo
            ),
            all_data AS (
                SELECT
                    DATE_TRUNC('month', o.order_date) AS mo,
                    SUM(oi.quantity * oi.price_at_order) AS revenue,
                    COUNT(DISTINCT o.id) AS order_count,
                    SUM(oi.quantity) AS units_sold
                FROM order_items oi
                JOIN orders o ON o.id = oi.order_id
                WHERE o.order_date >= $1::timestamptz
                GROUP BY DATE_TRUNC('month', o.order_date)
            )
            SELECT
                TO_CHAR(ms.mo, 'YYYY-MM') AS month,
                COALESCE(ad.revenue, 0) AS revenue,
                COALESCE(ad.order_count, 0) AS order_count,
                COALESCE(ad.units_sold, 0) AS units_sold
            FROM month_series ms
            LEFT JOIN all_data ad ON ad.mo = ms.mo
            ORDER BY ms.mo
        """
        async with pool.acquire() as conn:
            rows = await conn.fetch(query, start_date)

    return [
        {**dict(r), "revenue": float(r["revenue"])} for r in rows
    ]


@router.get("/sales")
async def sales_report(
    from_date: Optional[date] = Query(None, alias="from"),
    to_date: Optional[date] = Query(None, alias="to"),
    group_by: str = Query("product", pattern="^(product|type|seller)$"),
    current_user: dict = Depends(get_current_user),
    pool=Depends(get_pool),
):
    filters = []
    params: list = []
    idx = 1

    if from_date:
        filters.append(f"o.order_date >= ${idx}")
        params.append(from_date)
        idx += 1
    if to_date:
        filters.append(f"o.order_date < (${idx}::date + INTERVAL '1 day')")
        params.append(to_date)
        idx += 1

    # Seller sees only their own data
    if current_user["role"] == "seller":
        async with pool.acquire() as conn:
            seller = await conn.fetchrow(
                "SELECT id FROM sellers WHERE user_id=$1", current_user["user_id"]
            )
        if not seller:
            raise HTTPException(404, "Seller profile not found")
        filters.append(f"p.seller_id = ${idx}")
        params.append(seller["id"])
        idx += 1

    where = ("WHERE " + " AND ".join(filters)) if filters else ""

    if group_by == "product":
        select = "p.id AS group_id, p.name AS group_name"
        group = "p.id, p.name"
    elif group_by == "type":
        select = "pt.id AS group_id, pt.name AS group_name"
        group = "pt.id, pt.name"
    else:
        select = "s.id AS group_id, s.name AS group_name"
        group = "s.id, s.name"

    query = f"""
        SELECT {select},
               SUM(oi.quantity) AS total_quantity,
               SUM(oi.quantity * oi.price_at_order) AS total_revenue,
               COUNT(DISTINCT o.id) AS order_count
        FROM order_items oi
        JOIN orders o ON o.id = oi.order_id
        JOIN products p ON p.id = oi.product_id
        JOIN product_types pt ON pt.id = p.type_id
        JOIN sellers s ON s.id = p.seller_id
        {where}
        GROUP BY {group}
        ORDER BY total_revenue DESC
        LIMIT 100
    """

    async with pool.acquire() as conn:
        rows = await conn.fetch(query, *params)

    return [
        {**dict(r), "total_revenue": float(r["total_revenue"])} for r in rows
    ]


@router.get("/top-products")
async def top_products(
    limit: int = Query(10, ge=1, le=100),
    current_user: dict = Depends(get_current_user),
    pool=Depends(get_pool),
):
    extra_filter = ""
    params: list = [limit]

    if current_user["role"] == "seller":
        async with pool.acquire() as conn:
            seller = await conn.fetchrow(
                "SELECT id FROM sellers WHERE user_id=$1", current_user["user_id"]
            )
        if seller:
            extra_filter = "WHERE p.seller_id = $2"
            params.append(seller["id"])

    query = f"""
        SELECT p.id, p.name,
               s.name AS seller_name,
               SUM(oi.quantity * oi.price_at_order) AS total_revenue,
               SUM(oi.quantity) AS total_sold
        FROM order_items oi
        JOIN products p ON p.id = oi.product_id
        JOIN sellers s ON s.id = p.seller_id
        {extra_filter}
        GROUP BY p.id, p.name, s.name
        ORDER BY total_revenue DESC
        LIMIT $1
    """

    async with pool.acquire() as conn:
        rows = await conn.fetch(query, *params)

    return [
        {**dict(r), "total_revenue": float(r["total_revenue"])} for r in rows
    ]


@router.get("/order-status-distribution")
async def order_status_distribution(
    current_user: dict = Depends(get_current_user),
    pool=Depends(get_pool),
):
    extra_join = ""
    extra_where = ""
    params: list = []

    if current_user["role"] == "seller":
        async with pool.acquire() as conn:
            seller = await conn.fetchrow(
                "SELECT id FROM sellers WHERE user_id=$1", current_user["user_id"]
            )
        if seller:
            extra_join = "JOIN order_items oi ON oi.order_id = o.id JOIN products p ON p.id = oi.product_id"
            extra_where = "WHERE p.seller_id = $1"
            params.append(seller["id"])

    query = f"""
        SELECT os.name AS status_name, COUNT(DISTINCT o.id) AS order_count
        FROM orders o
        JOIN order_statuses os ON os.id = o.status_id
        {extra_join}
        {extra_where}
        GROUP BY os.name, os.sort_order
        ORDER BY os.sort_order
    """

    async with pool.acquire() as conn:
        rows = await conn.fetch(query, *params)

    return [dict(r) for r in rows]


@router.get("/customer-activity")
async def customer_activity(
    from_date: Optional[date] = Query(None, alias="from"),
    to_date: Optional[date] = Query(None, alias="to"),
    limit: int = Query(10, ge=1, le=100),
    current_user: dict = Depends(get_current_user),
    pool=Depends(get_pool),
):
    filters = []
    params: list = []
    idx = 1

    if from_date:
        filters.append(f"o.order_date >= ${idx}")
        params.append(from_date)
        idx += 1
    if to_date:
        filters.append(f"o.order_date < (${idx}::date + INTERVAL '1 day')")
        params.append(to_date)
        idx += 1

    seller_join = ""
    if current_user["role"] == "seller":
        async with pool.acquire() as conn:
            seller = await conn.fetchrow(
                "SELECT id FROM sellers WHERE user_id=$1", current_user["user_id"]
            )
        if seller:
            seller_join = f"JOIN products sp ON sp.id = oi.product_id AND sp.seller_id = ${idx}"
            params.append(seller["id"])
            idx += 1

    where = ("WHERE " + " AND ".join(filters)) if filters else ""
    params.append(limit)

    query = f"""
        SELECT c.id AS customer_id,
               c.first_name || ' ' || c.last_name AS customer_name,
               COUNT(DISTINCT o.id) AS order_count,
               SUM(oi.quantity * oi.price_at_order) AS total_spent
        FROM customers c
        JOIN orders o ON o.customer_id = c.id
        JOIN order_items oi ON oi.order_id = o.id
        {seller_join}
        {where}
        GROUP BY c.id, c.first_name, c.last_name
        ORDER BY total_spent DESC
        LIMIT ${idx}
    """

    async with pool.acquire() as conn:
        rows = await conn.fetch(query, *params)

    return [
        {**dict(r), "total_spent": float(r["total_spent"])} for r in rows
    ]


@router.get("/review-summary")
async def review_summary(
    product_id: Optional[int] = Query(None),
    seller_id: Optional[int] = Query(None),
    current_user: dict = Depends(get_current_user),
    pool=Depends(get_pool),
):
    if product_id is None and seller_id is None:
        raise HTTPException(400, "Provide product_id or seller_id")

    if product_id:
        async with pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                SELECT COUNT(*) AS review_count,
                       ROUND(AVG(rating)::numeric, 2) AS avg_rating
                FROM reviews WHERE product_id=$1
                """,
                product_id,
            )
        return {"product_id": product_id, **dict(row), "avg_rating": float(row["avg_rating"]) if row["avg_rating"] else None}

    async with pool.acquire() as conn:
        rows = await conn.fetch(
            """
            SELECT p.id AS product_id, p.name AS product_name,
                   COUNT(r.id) AS review_count,
                   ROUND(AVG(r.rating)::numeric, 2) AS avg_rating
            FROM products p
            LEFT JOIN reviews r ON r.product_id = p.id
            WHERE p.seller_id=$1
            GROUP BY p.id, p.name
            ORDER BY avg_rating DESC NULLS LAST
            """,
            seller_id,
        )
    return [
        {**dict(r), "avg_rating": float(r["avg_rating"]) if r["avg_rating"] else None}
        for r in rows
    ]
