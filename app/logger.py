import os
import logging
from datetime import datetime
from typing import Dict, Any

# Create logs directory if it doesn't exist
os.makedirs("logs", exist_ok=True)

# Configure logger
logger = logging.getLogger("order_processor")
logger.setLevel(logging.INFO)

# File handler for logs
file_handler = logging.FileHandler("logs/orders.log")
file_handler.setLevel(logging.INFO)

# Format for logs
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
file_handler.setFormatter(formatter)

# Add the handlers to the logger
logger.addHandler(file_handler)


async def log_order_event(event_type: str, order_data: Dict[str, Any]) -> None:
    """
    Background task to log order events

    Args:
        event_type: Type of event (success, failure)
        order_data: Data about the order
    """
    # Format the event message

    if event_type == "success":
        logger.info(
            f"ORDER SUCCESS - ID: {order_data['order_id']} - Items: {order_data['items']} - Amount: {order_data['payment_amount']}"
        )
    elif event_type == "failure":
        logger.error(
            f"ORDER FAILURE - Items: {order_data['items']} - Amount: {order_data['payment_amount']} - Error: {order_data.get('error', 'Unknown error')}"
        )
    elif event_type == "duplicate":
        logger.info(
            f"ORDER DUPLICATE - ID: {order_data['order_id']} - Items: {order_data['items']} - Amount: {order_data['payment_amount']}"
        )
    else:
        logger.warning(f"UNKNOWN EVENT - Type: {event_type} - Data: {order_data}")
