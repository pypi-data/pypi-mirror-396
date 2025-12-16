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
"""Decorators module for Peak SDK.

This module provides decorator-based caching functionality with support for:
- InMemoryCache: Thread-safe in-memory cache with TTL support
- PlatformCacheRepository: Unified cache repository with platform cache and fallback
- Cache decorator: Function decorator for automatic result caching with Cache-Control support
- Cache invalidation: Decorator and utilities for cache invalidation after write operations
- Cache utilities: Helper functions for cache key generation, result processing, and Cache-Control parsing
- Cache exceptions: Custom exceptions for cache-related errors

The cache system supports both platform cache (when available) and in-memory fallback.

Optional Dependencies:
- numpy: For serializing numpy arrays (installed with: pip install peak-sdk[types])
- pandas: For serializing pandas DataFrames and Series (installed with: pip install peak-sdk[types])
- starlette: For handling Starlette Response objects (installed with: pip install peak-sdk[types])

These dependencies are optional and the cache decorator will work without them, but with limited
serialization support for these specific data types.
"""

from .decorator import cache_result, invalidate_cache

__all__ = [
    "cache_result",
    "invalidate_cache",
]
