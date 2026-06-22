from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.customers import router as customers_router
from app.api.dashboard import router as dashboard_router
from app.api.health import router as health_router
from app.api.orders import router as orders_router
from app.api.products import router as products_router
from app.core.config import get_settings

settings = get_settings()

app = FastAPI(title=settings.app_name)
if settings.cors_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.include_router(health_router, prefix=settings.api_v1_prefix)
app.include_router(products_router, prefix=settings.api_v1_prefix)
app.include_router(customers_router, prefix=settings.api_v1_prefix)
app.include_router(orders_router, prefix=settings.api_v1_prefix)
app.include_router(dashboard_router, prefix=settings.api_v1_prefix)
