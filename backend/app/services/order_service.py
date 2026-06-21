from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.customer import Customer
from app.models.order import Order, OrderItem, OrderStatus
from app.models.product import Product
from app.schemas.order import OrderCreate, OrderUpdate


def create_order(db: Session, payload: OrderCreate) -> Order:
    if db.get(Customer, payload.customer_id) is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found.",
        )

    requested_quantities = _aggregate_requested_quantities(payload)
    products = _get_products_for_update(db, requested_quantities)

    missing_product_ids = sorted(set(requested_quantities) - set(products))
    if missing_product_ids:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Products not found: {missing_product_ids}.",
        )

    _validate_stock(products, requested_quantities)

    order = Order(customer_id=payload.customer_id, status=OrderStatus.PENDING, total_amount=Decimal("0.00"))
    total_amount = Decimal("0.00")

    for product_id, quantity in requested_quantities.items():
        product = products[product_id]
        unit_price = product.price
        line_total = unit_price * quantity
        total_amount += line_total
        product.quantity -= quantity
        order.items.append(
            OrderItem(
                product_id=product_id,
                quantity=quantity,
                unit_price=unit_price,
                line_total=line_total,
            )
        )

    order.total_amount = total_amount
    db.add(order)
    db.commit()
    return get_order(db, order.id)


def list_orders(db: Session) -> list[Order]:
    statement = (
        select(Order)
        .options(selectinload(Order.items))
        .order_by(Order.id)
    )
    return list(db.scalars(statement).all())


def get_order(db: Session, order_id: int) -> Order:
    statement = (
        select(Order)
        .where(Order.id == order_id)
        .options(selectinload(Order.items))
    )
    order = db.scalars(statement).first()
    if order is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found.",
        )

    return order


def update_order(db: Session, order_id: int, payload: OrderUpdate) -> Order:
    order = get_order(db, order_id)
    if order.status == payload.status:
        return order

    if order.status == OrderStatus.CANCELLED and payload.status != OrderStatus.CANCELLED:
        _reserve_stock_for_order_items(db, order.items)

    if payload.status == OrderStatus.CANCELLED and order.status != OrderStatus.CANCELLED:
        _restore_stock_for_order_items(db, order.items)

    order.status = payload.status
    db.commit()
    return get_order(db, order.id)


def delete_order(db: Session, order_id: int) -> None:
    order = get_order(db, order_id)
    if order.status != OrderStatus.CANCELLED:
        _restore_stock_for_order_items(db, order.items)

    db.delete(order)
    db.commit()


def _aggregate_requested_quantities(payload: OrderCreate) -> dict[int, int]:
    requested_quantities: dict[int, int] = {}
    for item in payload.items:
        requested_quantities[item.product_id] = (
            requested_quantities.get(item.product_id, 0) + item.quantity
        )

    return requested_quantities


def _get_products_for_update(
    db: Session,
    requested_quantities: dict[int, int],
) -> dict[int, Product]:
    statement = (
        select(Product)
        .where(Product.id.in_(requested_quantities))
        .with_for_update()
    )
    return {product.id: product for product in db.scalars(statement).all()}


def _validate_stock(
    products: dict[int, Product],
    requested_quantities: dict[int, int],
) -> None:
    insufficient_stock = [
        product_id
        for product_id, quantity in requested_quantities.items()
        if products[product_id].quantity < quantity
    ]
    if insufficient_stock:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Insufficient stock for products: {sorted(insufficient_stock)}.",
        )


def _restore_stock_for_order_items(db: Session, items: list[OrderItem]) -> None:
    product_ids = [item.product_id for item in items]
    products = {
        product.id: product
        for product in db.scalars(
            select(Product).where(Product.id.in_(product_ids)).with_for_update()
        ).all()
    }

    for item in items:
        products[item.product_id].quantity += item.quantity


def _reserve_stock_for_order_items(db: Session, items: list[OrderItem]) -> None:
    requested_quantities: dict[int, int] = {}
    for item in items:
        requested_quantities[item.product_id] = (
            requested_quantities.get(item.product_id, 0) + item.quantity
        )

    products = _get_products_for_update(db, requested_quantities)
    _validate_stock(products, requested_quantities)

    for item in items:
        products[item.product_id].quantity -= item.quantity
