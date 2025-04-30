import random
from typing import Dict, Any, Tuple, Optional
from datetime import datetime

from pymongo.errors import DuplicateKeyError, PyMongoError

from .database import orders_collection
from .models import Order, OrderRequest


async def process_order(
    order_request: OrderRequest,
) -> Tuple[Dict[str, Any], bool, Optional[str]]:
    """
    Process an order request with idempotency and simulated failures

    Args:
        order_request: The order request data

    Returns:
        Tuple of (response_data, success, error_message)
    """
    # Convert items to a sorted list
    sorted_items = sorted(order_request.items)

    # 1. Check if order already exists
    existing_order = await orders_collection.find_one(
        {"items": sorted_items, "payment_amount": order_request.payment_amount}
    )

    if existing_order:
        # Return the existing order without reprocessing
        return (
            {
                "order_id": existing_order["order_id"],
                "status": existing_order["status"],
            },
            True,
            "duplicate",
        )

    # 2. Simulate random failures (10% chance)
    if random.random() < 0.1:
        return {}, False, "Simulated database error"

    try:
        # 3. Create new order
        order = Order(items=sorted_items, payment_amount=order_request.payment_amount)

        order_dict = order.model_dump()
        await orders_collection.insert_one(order_dict)

        return {"order_id": order.order_id, "status": order.status}, True, None

    except DuplicateKeyError:
        # 4. Check if order already exists
        existing_order = await orders_collection.find_one(
            {"items": sorted_items, "payment_amount": order_request.payment_amount}
        )

        if existing_order:
            return (
                {
                    "order_id": existing_order["order_id"],
                    "status": existing_order["status"],
                },
                True,
                "duplicate",
            )
        else:
            return {}, False, "Duplicate key error but couldn't find original"

    except PyMongoError as e:
        # Handle any MongoDB errors
        return {}, False, f"Database error: {str(e)}"
