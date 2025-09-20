import os
import logging
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import ConnectionFailure

MONGO_URI = os.getenv("MONGODB_URI")
DATABASE_NAME = "VisualCues"

logging.basicConfig(level=logging.INFO)

client = None
db = None

async def connect_to_mongo():
    global client, db
    try:
        client = AsyncIOMotorClient(MONGO_URI)
        db = client.get_database(DATABASE_NAME)
        await client.server_info() #forces a connection to happen.
        logging.info("Connected to MongoDB")
    except ConnectionFailure as e:
        logging.error(f"Could not connect to MongoDB: {e}")
        client = None
        db = None
    except ValueError as e:
        logging.error(f"Invalid MONGO_URI: {e}")
        client = None
        db = None

async def disconnect_from_mongo():
    global client
    if client:
        client.close()
        client = None
        db = None
        logging.info("Disconnected from MongoDB")