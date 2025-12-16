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
"""In-memory cache implementation for the Peak SDK.

This module provides a thread-safe in-memory cache with TTL support.
"""

from __future__ import annotations

import logging
import threading
from typing import Any, Dict, Optional

from cachetools import TTLCache

logger = logging.getLogger(__name__)


class InMemoryCache:
    """Thread-safe in-memory cache with TTL support using cachetools."""

    def __init__(self, maxsize: int = 1000, default_ttl: int = 3600) -> None:
        """Initialize the in-memory cache.

        Args:
            maxsize: Maximum number of items in the cache.
            default_ttl: Default time-to-live for cache entries in seconds.
        """
        self.default_ttl = default_ttl
        self.maxsize = maxsize
        self._cache: TTLCache[str, Any] = TTLCache(maxsize=maxsize, ttl=default_ttl)
        self._lock = threading.RLock()
        self._ttl_caches: Dict[int, TTLCache[str, Any]] = {}

    def _get_cache_for_ttl(self, ttl: Optional[int]) -> TTLCache[str, Any]:
        """Get the appropriate cache instance for the given TTL.

        Args:
            ttl: Time-to-live in seconds, or None for default.

        Returns:
            TTLCache instance for the specified TTL.
        """
        if ttl is None:
            return self._cache

        if ttl not in self._ttl_caches:
            self._ttl_caches[ttl] = TTLCache(maxsize=self.maxsize, ttl=ttl)
        return self._ttl_caches[ttl]

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Store a value in the cache with an optional TTL.

        Args:
            key: Cache key.
            value: Value to store.
            ttl: Time-to-live in seconds, or None for default.
        """
        with self._lock:
            # Remove key from all caches before setting
            self._cache.pop(key, None)
            for cache in self._ttl_caches.values():
                cache.pop(key, None)
            cache = self._get_cache_for_ttl(ttl)
            cache[key] = value

    def get(self, key: str) -> Optional[Any]:
        """Retrieve a value from the cache if present and not expired.

        Args:
            key: Cache key.

        Returns:
            Cached value if found and not expired, None otherwise.
        """
        with self._lock:
            if key in self._cache:
                return self._cache[key]

            for cache in self._ttl_caches.values():
                if key in cache:
                    return cache[key]

            return None

    def delete(self, key: str) -> None:
        """Remove a value from the cache.

        Args:
            key: Cache key to remove.
        """
        with self._lock:
            self._cache.pop(key, None)

            for cache in self._ttl_caches.values():
                cache.pop(key, None)

    def delete_by_prefix(self, prefix: str) -> None:
        """Delete all cache entries whose keys start with the given prefix.

        Args:
            prefix: Key prefix to match for deletion.
        """
        with self._lock:
            keys_to_delete = [k for k in self._cache if k.startswith(prefix)]
            for k in keys_to_delete:
                self._cache.pop(k, None)

            for cache in self._ttl_caches.values():
                keys_to_delete = [k for k in cache if k.startswith(prefix)]
                for k in keys_to_delete:
                    cache.pop(k, None)

    def clear(self) -> None:
        """Clear all cache entries."""
        with self._lock:
            self._cache.clear()
            for cache in self._ttl_caches.values():
                cache.clear()

    def set_additional_prefix(self, prefix: str) -> None:
        """Set additional prefix for cache keys.

        This method is here for compatibility with Platform implementation.

        Args:
            prefix: Additional prefix to set.
        """
        logger.info("Setting additional prefix: %s", prefix)

    def flush_by_pattern(self, pattern: str) -> int:
        """Delete keys matching the given pattern.

        Supports prefix-style matching (e.g., 'abc*').

        Args:
            pattern: Pattern to match for deletion.

        Returns:
            Number of keys deleted.
        """
        with self._lock:
            deleted_count = 0

            # Handle prefix patterns (e.g., 'abc*')
            if pattern.endswith("*"):
                prefix = pattern[:-1]
                keys_to_delete = [k for k in self._cache if k.startswith(prefix)]
                for k in keys_to_delete:
                    self._cache.pop(k, None)
                    deleted_count += 1

                for cache in self._ttl_caches.values():
                    keys_to_delete = [k for k in cache if k.startswith(prefix)]
                    for k in keys_to_delete:
                        cache.pop(k, None)
                        deleted_count += 1
            else:
                # Exact match
                if pattern in self._cache:
                    self._cache.pop(pattern, None)
                    deleted_count += 1

                for cache in self._ttl_caches.values():
                    if pattern in cache:
                        cache.pop(pattern, None)
                        deleted_count += 1

            return deleted_count

    def flush_tenant(self) -> int:
        """Flush all cache entries for the current tenant.

        Returns:
            Number of keys deleted.
        """
        with self._lock:
            total_keys = len(self._cache) + sum(len(cache) for cache in self._ttl_caches.values())
            self.clear()
            return total_keys

    def get_all_caches(self) -> list[TTLCache[str, Any]]:
        """Get all cache instances including the main cache and TTL-specific caches.

        Returns:
            List of all TTLCache instances.
        """
        return [self._cache, *list(self._ttl_caches.values())]
