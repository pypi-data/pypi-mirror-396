#
# # Copyright © 2025 Peak AI Limited. or its affiliates. All Rights Reserved.
# #
# # Licensed under the Apache License, Version 2.0 (the "License"). You
# # may not use this file except in compliance with the License. A copy of
# # the License is located at:
# #
# # https://github.com/PeakBI/peak-sdk/blob/main/LICENSE
# #
# # or in the "license" file accompanying this file. This file is
# # distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF
# # ANY KIND, either express or implied. See the License for the specific
# # language governing permissions and limitations under the License.
# #
# # This file is part of the peak-sdk.
# # see (https://github.com/PeakBI/peak-sdk)
# #
# # You should have received a copy of the APACHE LICENSE, VERSION 2.0
# # along with this program. If not, see <https://apache.org/licenses/LICENSE-2.0>
#
"""Platform cache repository for the Peak SDK.

This module provides a unified interface for cache operations with platform cache
and in-memory fallback support.
"""

from __future__ import annotations

#
# # Copyright © 2025 Peak AI Limited. or its affiliates. All Rights Reserved.
# #
# # Licensed under the Apache License, Version 2.0 (the "License"). You
# # may not use this file except in compliance with the License. A copy of
# # the License is located at:
# #
# # https://github.com/PeakBI/peak-sdk/blob/main/LICENSE
# #
# # or in the "license" file accompanying this file. This file is
# # distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF
# # ANY KIND, either express or implied. See the License for the specific
# # language governing permissions and limitations under the License.
# #
# # This file is part of the peak-sdk.
# # see (https://github.com/PeakBI/peak-sdk)
# #
# # You should have received a copy of the APACHE LICENSE, VERSION 2.0
# # along with this program. If not, see <https://apache.org/licenses/LICENSE-2.0>
#
import logging
import threading
from typing import Any, Optional, Union

from peak.decorators.utils import deserialize_from_cache, serialize_for_cache
from peak.resources.cache import CacheClient

from .inmemory_cache import InMemoryCache

logger = logging.getLogger(__name__)


class PlatformCacheRepository:
    """Peak Platform cache repository that provides a unified interface for cache operations.

    Handles platform cache with InMemoryCache fallback internally.
    """

    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args: tuple[Any, ...], **kwargs: dict[str, Any]) -> Any:
        """Create a singleton instance of the cache repository."""
        del args, kwargs  # Unused arguments for singleton pattern
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, maxsize: int = 1000, default_ttl: int = 3600) -> None:
        """Initialize the cache repository.

        Args:
            maxsize: Maximum number of items in the cache.
            default_ttl: Default time-to-live for cache entries in seconds.
        """
        self._cache: Union[CacheClient, InMemoryCache]
        self._cache_client: Optional[CacheClient]
        self._platform_cache_available: bool

        if not hasattr(self, "_cache"):
            self._init_cache(maxsize, default_ttl)

    def _initialize_platform_cache(self) -> bool:
        """Initialize platform cache client.

        This method is called lazily when needed.

        Returns:
            True if platform cache is available, False otherwise.
        """
        if hasattr(self, "_platform_cache_available"):
            return self._platform_cache_available

        try:
            self._cache_client = CacheClient()
            self._cache_client.ping()
            self._platform_cache_available = True
            logger.info("Platform cache initialized successfully")
        except (ConnectionError, TimeoutError, OSError):
            logger.warning(
                "Platform cache not available, will use InMemoryCache as fallback",
            )
            logger.exception("Platform cache initialization failed")
            self._cache_client = None
            self._platform_cache_available = False

        return self._platform_cache_available

    def _init_cache(self, maxsize: int, default_ttl: int) -> None:
        """Initialize the cache with platform cache or fallback.

        Args:
            maxsize: Maximum number of items in the cache.
            default_ttl: Default time-to-live for cache entries in seconds.
        """
        fallback_cache = InMemoryCache(maxsize=maxsize, default_ttl=default_ttl)
        if self._initialize_platform_cache() and self._cache_client is not None:
            try:
                self._cache = self._cache_client
            except (ConnectionError, TimeoutError, OSError) as e:
                logger.warning("Failed to initialize platform cache: %s", e)
                self._cache = fallback_cache
        else:
            self._cache = fallback_cache

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set a value in the cache with proper serialization.

        Ensures the value is properly serialized before passing to the cache client.

        Args:
            key: Cache key.
            value: Value to store.
            ttl: Time-to-live in seconds, or None for default.
        """
        serialized_value = serialize_for_cache(value)
        self._cache.set(key, serialized_value, ttl)

    def get(self, key: str) -> Optional[Any]:
        """Get a value from the cache with proper deserialization.

        Args:
            key: Cache key.

        Returns:
            Deserialized value if found, None otherwise.
        """
        cached_value = self._cache.get(key)
        if cached_value is not None:
            return deserialize_from_cache(cached_value)
        return None

    def delete(self, key: str) -> None:
        """Delete a value from the cache.

        Args:
            key: Cache key to delete.
        """
        self._cache.delete(key)

    def delete_by_prefix(self, prefix: str) -> None:
        """Delete all cache entries whose keys start with the given prefix. Uses flush_by_pattern for efficient pattern-based deletion."""
        try:
            pattern = prefix if prefix.endswith("*") else prefix + "*"
            deleted_count = self._cache.flush_by_pattern(pattern)
            logger.info("Deleted %d keys with prefix '%s' using flush_by_pattern", deleted_count, prefix)
        except Exception as e:  # noqa: BLE001
            logger.warning("Failed to use flush_by_pattern for prefix '%s': %s", prefix, e)

    def clear(self) -> None:
        """Clear all cache entries."""
        try:
            if hasattr(self._cache, "clear"):
                self._cache.clear()
            else:
                logger.warning("clear not supported by current cache implementation")
        except (ConnectionError, TimeoutError, OSError):
            logger.exception("Error clearing cache")

    def set_additional_prefix(self, prefix: str) -> None:
        """Set additional prefix for cache keys.

        Args:
            prefix: Additional prefix to set.
        """
        try:
            self._cache.set_additional_prefix(prefix)
        except (ConnectionError, TimeoutError, OSError):
            logger.exception("Error setting additional prefix")

    @classmethod
    def reset_instance(cls: type[PlatformCacheRepository]) -> None:
        """Reset the singleton instance.

        This is useful for testing purposes.
        """
        cls._instance = None
