from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List

from app.database import get_pool
from app.auth.deps import get_current_user, require_customer, require_seller

router = APIRouter()


class OrderItem(BaseModel):
    product_id: int
    quantity: int


class OrderCreate(BaseModel):
    delivery_address: str
    items: List[OrderItem]


class StatusUpdate(BaseModel):
    status_id: int


@router.get("/order-statuses")
async def get_order_statuses(pool=Depends(get_pool)):
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            "SELECT id, name, sort_order, is_final FROM order_statuses ORDER BY sort_order"
        )
    return [dict(r) for r in rows]


@router.post("/orders", status_code=201)
async def create_order(
    body: OrderCreate,
    current_user: dict = Depends(require_customer),
    pool=Depends(get_pool),
):
    if not body.items:
        raise HTTPException(400, "Order must have at least one item")

    async with pool.acquire() as conn:
        customer = await conn.fetchrow(
            "SELECT id FROM customers WHERE user_id=$1", current_user["user_id"]
        )
        if not customer:
            raise HTTPException(404, "Customer profile not found")

        # Status "Оформлен" has sort_order=1
        status = await conn.fetchrow(
            "SELECT id FROM order_statuses WHERE sort_order=1"
        )
        if not status:
            raise HTTPException(500, "Initial order status not found")

        async with conn.transaction():
            order = await conn.fetchrow(
                "INSERT INTO orders (customer_id, status_id, delivery_address) VALUES ($1,$2,$3) RETURNING id",
                customer["id"], status["id"], body.delivery_address,
            )
            order_id = order["id"]

            for item in body.items:
                product = await conn.fetchrow(
                    "SELECT id, price, stock_quantity FROM products WHERE id=$1 FOR UPDATE",
                    item.product_id,
                )
                if not product:
                    raise HTTPException(404, f"Product {item.product_id} not found")
                if product["stock_quantity"] < item.quantity:
                    raise HTTPException(
                        400,
                        f"Insufficient stock for product {item.product_id}: "
                        f"available {product['stock_quantity']}, requested {item.quantity}",
                    )

                await conn.execute(
                    "INSERT INTO order_items (order_id, product_id, quantity, price_at_order) VALUES ($1,$2,$3,$4)",
                    order_id, item.product_id, item.quantity, product["price"],
                )
                await conn.execute(
                    "UPDATE products SET stock_quantity = stock_quantity - $1 WHERE id=$2",
                    item.quantity, item.product_id,
                )

    return {"id": order_id}


@router.get("/orders")
async def list_orders(
    current_user: dict = Depends(get_current_user),
    pool=Depends(get_pool),
):
    async with pool.acquire() as conn:
        if current_user["role"] == "customer":
            customer = await conn.fetchrow(
                "SELECT id FROM customers WHERE user_id=$1", current_user["user_id"]
            )
            if not customer:
                raise HTTPException(404, "Customer profile not found")

            rows = await conn.fetch(
                """
                SELECT o.id, o.order_date, o.delivery_address,
                       os.name AS status_name, os.id AS status_id
                FROM orders o
                JOIN order_statuses os ON os.id = o.status_id
                WHERE o.customer_id=$1
                ORDER BY o.order_date DESC
                """,
                customer["id"],
            )
        else:
            seller = await conn.fetchrow(
                "SELECT id FROM sellers WHERE user_id=$1", current_user["user_id"]
            )
            if not seller:
                raise HTTPException(404, "Seller profile not found")

            rows = await conn.fetch(
                """
                SELECT DISTINCT o.id, o.order_date, o.delivery_address,
                       os.name AS status_name, os.id AS status_id
                FROM orders o
                JOIN order_statuses os ON os.id = o.status_id
                JOIN order_items oi ON oi.order_id = o.id
                JOIN products p ON p.id = oi.product_id
                WHERE p.seller_id=$1
                ORDER BY o.order_date DESC
                """,
                seller["id"],
            )

    return [
        {**dict(r), "order_date": r["order_date"].isoformat()} for r in rows
    ]


@router.get("/orders/{order_id}")
async def get_order(
    order_id: int,
    current_user: dict = Depends(get_current_user),
    pool=Depends(get_pool),
):
    async with pool.acquire() as conn:
        order = await conn.fetchrow(
            """
            SELECT o.id, o.order_date, o.delivery_address, o.customer_id,
                   os.name AS status_name, os.id AS status_id, os.is_final
            FROM orders o
            JOIN order_statuses os ON os.id = o.status_id
            WHERE o.id=$1
            """,
            order_id,
        )
        if not order:
            raise HTTPException(404, "Order not found")

        # Access control
        if current_user["role"] == "customer":
            customer = await conn.fetchrow(
                "SELECT id FROM customers WHERE user_id=$1", current_user["user_id"]
            )
            if not customer or order["customer_id"] != customer["id"]:
                raise HTTPException(403, "Access denied")
        else:
            seller = await conn.fetchrow(
                "SELECT id FROM sellers WHERE user_id=$1", current_user["user_id"]
            )
            has_items = await conn.fetchval(
                """
                SELECT EXISTS(
                    SELECT 1 FROM order_items oi
                    JOIN products p ON p.id = oi.product_id
                    WHERE oi.order_id=$1 AND p.seller_id=$2
                )
                """,
                order_id, seller["id"],
            )
            if not has_items:
                raise HTTPException(403, "Access denied")

        items = await conn.fetch(
            """
            SELECT oi.product_id, oi.quantity, oi.price_at_order,
                   p.name AS product_name
            FROM order_items oi
            JOIN products p ON p.id = oi.product_id
            WHERE oi.order_id=$1
            """,
            order_id,
        )

    return {
        **dict(order),
        "order_date": order["order_date"].isoformat(),
        "items": [
            {**dict(i), "price_at_order": float(i["price_at_order"])} for i in items
        ],
    }


@router.patch("/orders/{order_id}/status")
async def update_order_status(
    order_id: int,
    body: StatusUpdate,
    current_user: dict = Depends(require_seller),
    pool=Depends(get_pool),
):
    async with pool.acquire() as conn:
        seller = await conn.fetchrow(
            "SELECT id FROM sellers WHERE user_id=$1", current_user["user_id"]
        )
        if not seller:
            raise HTTPException(404, "Seller profile not found")

        has_items = await conn.fetchval(
            """
            SELECT EXISTS(
                SELECT 1 FROM order_items oi
                JOIN products p ON p.id = oi.product_id
                WHERE oi.order_id=$1 AND p.seller_id=$2
            )
            """,
            order_id, seller["id"],
        )
        if not has_items:
            raise HTTPException(403, "No access to this order")

        order = await conn.fetchrow(
            """
            SELECT o.id, os.sort_order AS current_sort, os.is_final
            FROM orders o
            JOIN order_statuses os ON os.id = o.status_id
            WHERE o.id=$1
            """,
            order_id,
        )
        if not order:
            raise HTTPException(404, "Order not found")
        if order["is_final"]:
            raise HTTPException(400, "Order is already in a final status")

        new_status = await conn.fetchrow(
            "SELECT id, sort_order, name FROM order_statuses WHERE id=$1", body.status_id
        )
        if not new_status:
            raise HTTPException(404, "Status not found")

        if new_status["sort_order"] <= order["current_sort"]:
            raise HTTPException(400, "Cannot move order to a previous or same status")

        await conn.execute(
            "UPDATE orders SET status_id=$1 WHERE id=$2", body.status_id, order_id
        )

    return {"ok": True, "new_status": new_status["name"]}
