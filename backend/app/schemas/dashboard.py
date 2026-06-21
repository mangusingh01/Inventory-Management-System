from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict

from app.models.order import OrderStatus


class DashboardLowStockProduct(BaseModel):
    id: int
    name: str
    sku: str
    quantity: int

    model_config = ConfigDict(from_attributes=True)


class DashboardRecentOrder(BaseModel):
    id: int
    customer_id: int
    status: OrderStatus
    total_amount: Decimal
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DashboardRead(BaseModel):
    total_products: int
    total_customers: int
    total_orders: int
    total_inventory_units: int
    low_stock_threshold: int
    low_stock_product_count: int
    pending_order_count: int
    fulfilled_order_count: int
    cancelled_order_count: int
    active_order_value: Decimal
    fulfilled_revenue: Decimal
    low_stock_products: list[DashboardLowStockProduct]
    recent_orders: list[DashboardRecentOrder]
