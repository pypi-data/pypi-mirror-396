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
"""Custom exceptions for the cache decorators module."""

from __future__ import annotations


class CacheError(Exception):
    """Base exception for cache-related errors."""


class CacheSerializationError(CacheError):
    """Raised when there's an error serializing data for cache storage."""


class CacheDeserializationError(CacheError):
    """Raised when there's an error deserializing data from cache storage."""


class CacheKeyError(CacheError):
    """Raised when there's an error with cache key generation or validation."""


class CacheConnectionError(CacheError):
    """Raised when there's an error connecting to the cache service."""


class CacheTimeoutError(CacheError):
    """Raised when a cache operation times out."""
