# Fault-Tolerant Order Processor

A fault-tolerant order processing system built with FastAPI, MongoDB, and Docker.

## Features

- REST API for order processing
- Built-in failure handling with retry support
- Idempotent request processing (no duplicate orders)
- Background logging
- Full Docker containerization

## Getting Started

### Prerequisites

- Docker and Docker Compose

### Running the Application

1. Clone this repository
2. Navigate to the project directory
3. Start the application:

```bash
docker-compose up -d
```

The API will be available at: http://localhost:8000

### API Documentation

FastAPI automatically generates interactive API documentation:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## API Endpoints

### Process Order

```
POST /orders
```

Request body:
```json
{
  "items": ["item1", "item2"],
  "payment_amount": 100.50
}
```

Success response (200 OK):
```json
{
  "order_id": "abc123...",
  "status": "processed"
}
```

Failure response (503 Service Unavailable)
```json
{
  "detail": "Order processing failed, please retry after 5 seconds"
}
```
With `Retry-After: 5` header.

### Health Check

```
GET /health
```

Response:
```json
{
  "status": "healthy",
  "database": "connected"
}
```

## Testing

### Testing with curl

1. Submit an order

```bash
curl -X POST http://localhost:8000/orders \
  -H "Content-Type: application/json" \
  -d '{"items": ["item1", "item2"], "payment_amount": 100.50}'
```

2. Submit the same order again (to test idempotency)

```bash
curl -X POST http://localhost:8000/orders \
  -H "Content-Type: application/json" \
  -d '{"items": ["item1", "item2"], "payment_amount": 100.50}'
```

Should return the same `order_id`.

3. Check logs

```bash
docker-compose exec api cat /app/logs/orders.log
```

Or directly from your host machine:

```bash
cat logs/orders.log
```



4. Verified data stored

```bash
docker exec -it order-processor-mongodb-1 mongosh orders_db --eval 'db.orders.find()'
```

## Architecture

- **FastAPI**: Handles HTTP requests, input validation, and response formatting
- **MongoDB**: Stores order data and ensures idempotency through unique indexes
- **Background Tasks**: Async logging without blocking the API responses
- **Docker**: Containerizes the application for consistent deployment