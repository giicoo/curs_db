from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import init_db, close_db
from app.auth.router import router as auth_router
from app.catalog.router import router as catalog_router
from app.products.router import router as products_router
from app.orders.router import router as orders_router
from app.reviews.router import router as reviews_router
from app.reports.router import router as reports_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield
    await close_db()


app = FastAPI(title="Marketplace API", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(catalog_router, prefix="/catalog", tags=["catalog"])
app.include_router(products_router, tags=["products"])
app.include_router(orders_router, tags=["orders"])
app.include_router(reviews_router, prefix="/reviews", tags=["reviews"])
app.include_router(reports_router, prefix="/reports", tags=["reports"])
