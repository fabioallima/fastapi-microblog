from typing import Optional
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from dynaconf import settings
import logging
import asyncio

from microblog.models.user import User
from microblog.models.post import Post
from microblog.models.like import Like
from microblog.models.social import Social

logger = logging.getLogger(__name__)

async def init_db():
    """Initialize MongoDB connection and Beanie ODM"""
    try:
        # Get MongoDB URI from settings
        uri = settings.get("MICROBLOG_DB.uri")
        if not uri:
            raise ValueError("MongoDB URI not found in settings")

        logger.info(f"Connecting to MongoDB at {uri}")
        
        # Initialize MongoDB client with minimal options
        client = AsyncIOMotorClient(uri)
        
        # Get database from client
        db = client.get_default_database()
        
        # Wait for MongoDB to be ready
        logger.info("Waiting for MongoDB to be ready...")
        for attempt in range(30):  # Try for 30 seconds
            try:
                # Try to get server info to verify connection
                server_info = await db.command("serverStatus")
                logger.info(f"Successfully connected to MongoDB version {server_info.get('version', 'unknown')}")
                
                # Try to get database info
                db_info = await db.command("dbStats")
                logger.info(f"Database stats: {db_info}")
                
                break
            except Exception as e:
                logger.warning(f"Attempt {attempt + 1}/30: MongoDB not ready yet. Error: {str(e)}")
                if attempt < 29:  # Don't sleep on the last attempt
                    await asyncio.sleep(1)
        else:
            raise Exception("Could not connect to MongoDB after 30 seconds")

        # Initialize Beanie with the models
        logger.info("Initializing Beanie with models...")
        await init_beanie(
            database=db,
            document_models=[
                User,
                Post,
                Social,
                Like
            ]
        )
        logger.info("✅ Beanie initialized successfully")
    except Exception as e:
        logger.error(f"❌ Failed to initialize database: {e}")
        raise e
