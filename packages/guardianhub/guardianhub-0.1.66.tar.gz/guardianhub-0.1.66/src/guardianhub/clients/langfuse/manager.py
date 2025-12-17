"""Langfuse Manager for singleton connection management.

This module provides a manager that ensures only one instance of the Langfuse
client is created and used throughout the application.
"""

from __future__ import annotations

import os
from typing import Optional

import httpx
from guardianhub import get_logger
from langfuse import Langfuse

LOGGER = get_logger(__name__)

# --- Configuration ---
os.environ["LANGFUSE_PUBLIC_KEY"] = "pk-lf-f3b04336-2808-4dc1-a83d-aa7944aee2f7"
os.environ["LANGFUSE_SECRET_KEY"] = "sk-lf-737015da-d020-4914-9813-ecb45bdb42f3"
os.environ["LANGFUSE_HOST"] = "http://langfuse.guardianhub.com/"

# TODO: For future reference - ThreadPool impl to handle multiple connection
class LangfuseManager:
    """Manages the singleton instance of the Langfuse client."""
    _client: Optional[Langfuse] = None
    _initialized = False

    @classmethod
    def get_instance(
        cls,
        public_key: Optional[str] = None,
        secret_key: Optional[str] = None,
        host: Optional[str] = None,
        **kwargs
    ) -> Optional[Langfuse]:
        """
        Get the singleton Langfuse client instance.

        Initializes the client on the first call and returns the existing
        instance on subsequent calls.

        Args:
            public_key: Langfuse public key.
            secret_key: Langfuse secret key.
            host: Langfuse host URL.
            **kwargs: Additional arguments for the Langfuse client.

        Returns:
            The initialized Langfuse client instance, or None if initialization fails.
        """
        LOGGER.info("🔍 Initializing Langfuse Service...")

        if cls._initialized:
            return cls._client

        cls._initialized = True  # Mark as initialized even if it fails, to prevent retries.

        public_key = public_key or os.getenv("LANGFUSE_PUBLIC_KEY")
        secret_key = secret_key or os.getenv("LANGFUSE_SECRET_KEY")
        host = host or os.getenv("LANGFUSE_HOST", "http://langfuse.guardianhub.com/")

        if not public_key or not secret_key:
            LOGGER.warning(
                "Langfuse credentials not provided. Set LANGFUSE_PUBLIC_KEY and "
                "LANGFUSE_SECRET_KEY. Langfuse client will not be initialized."
            )
            return None

        try:
            cls._client = Langfuse(
                public_key=public_key,
                secret_key=secret_key,
                host=host,
                **kwargs
            )

            if cls.check_langfuse_connection():
                LOGGER.info("✅ Successfully initialized singleton Langfuse client.")
            else:
                LOGGER.warning("⚠️ Langfuse client initialization failed ")

            return cls._client
        except Exception as exc:
            LOGGER.exception("Failed to initialize singleton Langfuse client: %s", exc)
            cls._client = None
            return None

    @classmethod
    def check_langfuse_connection(cls) -> bool:
        """
        Check if the Langfuse connection is valid by attempting to authenticate.

        Returns:
            bool: True if the connection is valid, False otherwise
        """
        if not cls._client:
            LOGGER.warning("Langfuse client is not initialized")
            return False

        try:
            # Test the connection with a timeout to prevent hanging
            is_authenticated = cls._client.auth_check()
            if is_authenticated:
                LOGGER.info("✅ Successfully authenticated with Langfuse")
                return True
            else:
                LOGGER.warning("❌ Failed to authenticate with Langfuse - Invalid credentials")
                return False
        except httpx.ConnectError as e:
            LOGGER.error(f"❌ Could not connect to Langfuse server: {str(e)}. "
                         "Please check your network connection and Langfuse server status.")
            return False
        except Exception as e:
            LOGGER.error(f"❌ Error connecting to Langfuse: {str(e)}", exc_info=True)
            return False

    @classmethod
    def flush(cls) -> None:
        """Flushes the managed Langfuse client instance."""
        if cls._client:
            cls._client.flush()
            LOGGER.info("Langfuse manager flushed the client.")
