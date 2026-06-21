from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.models.customer import Customer
from app.models.order import Order, OrderStatus
from app.models.product import Product
from app.schemas.dashboard import DashboardRead


def get_dashboard(db: Session) -> DashboardRead:
    settings = get_settings()
    low_stock_threshold = settings.dashboard_low_stock_threshold

    return DashboardRead(
        total_products=_count(db, Product.id),
        total_customers=_count(db, Customer.id),
        total_orders=_count(db, Order.id),
        total_inventory_units=_sum_int(db, Product.quantity),
        low_stock_threshold=low_stock_threshold,
        low_stock_product_count=_count_low_stock_products(db, low_stock_threshold),
        pending_order_count=_count_orders_by_status(db, OrderStatus.PENDING),
        fulfilled_order_count=_count_orders_by_status(db, OrderStatus.FULFILLED),
        cancelled_order_count=_count_orders_by_status(db, OrderStatus.CANCELLED),
        active_order_value=_sum_order_value(
            db,
            excluded_status=OrderStatus.CANCELLED,
        ),
        fulfilled_revenue=_sum_order_value(
            db,
            included_status=OrderStatus.FULFILLED,
        ),
        low_stock_products=_list_low_stock_products(db, low_stock_threshold),
        recent_orders=_list_recent_orders(db),
    )


def _count(db: Session, column) -> int:
    return db.scalar(select(func.count(column))) or 0


def _sum_int(db: Session, column) -> int:
    return db.scalar(select(func.coalesce(func.sum(column), 0))) or 0


def _count_low_stock_products(db: Session, threshold: int) -> int:
    statement = select(func.count(Product.id)).where(Product.quantity <= threshold)
    return db.scalar(statement) or 0


def _count_orders_by_status(db: Session, order_status: OrderStatus) -> int:
    statement = select(func.count(Order.id)).where(Order.status == order_status)
    return db.scalar(statement) or 0


def _sum_order_value(
    db: Session,
    included_status: OrderStatus | None = None,
    excluded_status: OrderStatus | None = None,
) -> Decimal:
    statement = select(func.coalesce(func.sum(Order.total_amount), 0))
    if included_status is not None:
        statement = statement.where(Order.status == included_status)
    if excluded_status is not None:
        statement = statement.where(Order.status != excluded_status)

    return db.scalar(statement) or Decimal("0.00")


def _list_low_stock_products(db: Session, threshold: int) -> list[Product]:
    statement = (
        select(Product)
        .where(Product.quantity <= threshold)
        .order_by(Product.quantity.asc(), Product.id.asc())
        .limit(10)
    )
    return list(db.scalars(statement).all())


def _list_recent_orders(db: Session) -> list[Order]:
    statement = select(Order).order_by(Order.created_at.desc(), Order.id.desc()).limit(10)
    return list(db.scalars(statement).all())
