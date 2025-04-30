from fastapi import FastAPI, BackgroundTasks, HTTPException, Response
from fastapi.responses import JSONResponse

from .models import OrderRequest, OrderResponse
from .services import process_order
from .logger import log_order_event
from .database import ping_database, create_indexes


app = FastAPI(title="Order Processing API")


@app.on_event("startup")
async def startup_event():
    """Run operations on server startup"""
    # Check database connection
    if not await ping_database():
        raise RuntimeError("Database connection failed")

    # Create indexes
    await create_indexes()


@app.post("/orders", response_model=OrderResponse)
async def create_order(
    order_request: OrderRequest, background_tasks: BackgroundTasks, response: Response
):
    """
    Process a new order with idempotency and failure handling

    Returns:
        OrderResponse: The processed order details
    """
    # Process the order
    result, success, message = await process_order(order_request)

    # Handle successful case
    if success:
        # Log the success or duplicate event
        event_type = "duplicate" if message == "duplicate" else "success"
        log_data = {
            "order_id": result["order_id"],
            "items": order_request.items,
            "payment_amount": order_request.payment_amount,
        }
        background_tasks.add_task(log_order_event, event_type, log_data)

        # Return the order response
        return result

    # Handle failure case
    # Log the failure
    log_data = {
        "items": order_request.items,
        "payment_amount": order_request.payment_amount,
        "error": message,
    }
    background_tasks.add_task(log_order_event, "failure", log_data)

    # Return error response with retry-after header
    response.headers["Retry-After"] = "5"
    raise HTTPException(
        status_code=503,
        detail="Order processing failed, please retry after 5 seconds",
    )


@app.get("/health")
async def health_check():
    """Health check endpoint to verify the API is running."""
    db_status = await ping_database()

    if not db_status:
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": "Database connection failed"},
        )

    return {"status": "healthy", "database": "connected"}


@app.get("/")
async def read_root():
    return {"message": "Welcome to Order Processing API"}
