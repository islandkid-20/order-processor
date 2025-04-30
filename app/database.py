import os
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import ServerSelectionTimeoutError

# Database configuration
MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
MONGODB_DB = os.getenv("MONGODB_DB", "orders_db")

# Create a connection to the database
client = AsyncIOMotorClient(MONGODB_URL)
database = client[MONGODB_DB]

# Collection for orders
orders_collection = database.orders


async def ping_database():
    """Test the database connection."""
    try:
        await client.admin.command("ping")
        return True
    except ServerSelectionTimeoutError:
        return False


async def create_indexes():
    """Create necessary indexes for performance and constraints."""
    await orders_collection.create_index(
        [("items", 1), ("payment_amount", 1)], unique=True
    )
