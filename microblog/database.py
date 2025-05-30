from typing import Optional
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from dynaconf import settings
import logging

from microblog.models.user import User
from microblog.models.post import Post
from microblog.models.like import Like
from microblog.models.social import Social

logger = logging.getLogger(__name__)

async def init_db():
    """Initialize MongoDB and Beanie ODM"""
    try:
        uri = settings.get("MICROBLOG_DB.uri")
        if not uri:
            raise ValueError("MongoDB URI not found in settings.")

        client = AsyncIOMotorClient(uri)
        await init_beanie(
            database=client.get_default_database(),  # ou client["microblog"] se quiser fixar o nome
            document_models=[User, Post, Like, Social],
        )
        logger.info("✅ Beanie initialized successfully.")
    except Exception as e:
        logger.error(f"❌ Failed to initialize database: {e}")
        raise e
