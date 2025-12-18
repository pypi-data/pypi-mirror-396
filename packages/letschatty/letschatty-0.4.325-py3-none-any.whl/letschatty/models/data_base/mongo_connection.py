from ..base_models.singleton import SingletonMeta
from pymongo import MongoClient
from motor.motor_asyncio import AsyncIOMotorClient
from typing import Optional
from urllib.parse import quote_plus
import os
import atexit
import asyncio
import logging

logger = logging.getLogger(__name__)

class MongoConnection(metaclass=SingletonMeta):
    def __init__(
        self,
        username: Optional[str] = None,
        password: Optional[str] = None,
        uri_base: Optional[str] = None,
        instance: Optional[str] = None,
        verify_on_init: bool = True
    ):
        self.username = username or os.getenv('MONGO_USERNAME')
        self.password = password or os.getenv('MONGO_PASSWORD')
        self.uri_base = uri_base or os.getenv('MONGO_URI_BASE')
        self.instance = instance or os.getenv('MONGO_INSTANCE_COMPONENT')

        if not all([self.username, self.password, self.uri_base, self.instance]):
            raise ValueError("Missing required MongoDB connection parameters")

        # URL-encode username and password to handle special characters per RFC 3986
        encoded_username = quote_plus(self.username)
        encoded_password = quote_plus(self.password)

        uri = f"{self.uri_base}://{encoded_username}:{encoded_password}@{self.instance}.mongodb.net"

        # Sync client (existing)
        self.client = MongoClient(uri)

        # NEW: Async client for async operations
        # Don't pass io_loop - Motor will automatically use the current event loop
        # This is important for Lambda where the event loop changes between invocations
        self.async_client = AsyncIOMotorClient(uri)

        # Verify connections if requested
        if verify_on_init:
            try:
                # Try to get running loop
                loop = asyncio.get_running_loop()
                # If we get here, there's a running loop
                logger.warning(
                    "Event loop is already running. Skipping connection verification in __init__. "
                    "Call verify_connection_async() from async context to verify connection."
                )
                self._connection_verified = False
            except RuntimeError:
                # No running loop, safe to use run_until_complete
                try:
                    # Test sync client
                    self.client.admin.command('ping')

                    # Test async client in sync context
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    loop.run_until_complete(self.async_client.admin.command('ping'))
                    self._connection_verified = True
                    loop.close()
                except Exception as e:
                    self.client.close()
                    self.async_client.close()
                    raise ConnectionError(f"Failed to connect to MongoDB: {str(e)}")
        else:
            self._connection_verified = False

        atexit.register(self.close)

    def _ensure_async_client_loop(self):
        """Ensure async client is using the current event loop (for Lambda compatibility)"""
        try:
            current_loop = asyncio.get_running_loop()
            # Check if client's loop is closed or different
            client_loop = getattr(self.async_client, '_io_loop', None)
            if client_loop is not None:
                try:
                    # Try to check if the loop is closed
                    if client_loop.is_closed():
                        # Recreate client with current loop
                        logger.warning("Async client's event loop is closed, recreating client")
                        old_client = self.async_client
                        uri = f"{self.uri_base}://{quote_plus(self.username)}:{quote_plus(self.password)}@{self.instance}.mongodb.net"
                        self.async_client = AsyncIOMotorClient(uri)
                        try:
                            old_client.close()
                        except:
                            pass
                except AttributeError:
                    # _io_loop might not exist in newer Motor versions
                    pass
        except RuntimeError:
            # No running loop, which is fine - Motor will handle it
            pass

    async def verify_connection_async(self) -> bool:
        """Verify MongoDB connection asynchronously. Safe to call from async context."""
        try:
            # Ensure we're using the current event loop
            self._ensure_async_client_loop()
            await self.async_client.admin.command('ping')
            self._connection_verified = True
            return True
        except Exception as e:
            logger.error(f"Failed to verify MongoDB connection: {e}")
            raise ConnectionError(f"Failed to verify MongoDB connection: {e}")

    def close(self) -> None:
        if hasattr(self, 'client'):
            self.client.close()
        if hasattr(self, 'async_client'):
            self.async_client.close()
