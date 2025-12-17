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
"""Cache decorators for the Peak SDK.

This module provides decorators for caching function results and invalidating cache entries.
"""

from __future__ import annotations

import functools
import inspect
import logging
from typing import Any, Callable, List, Optional, TypeVar, Union

from .repository import PlatformCacheRepository
from .utils import (
    _add_cache_control_headers,
    _extract_entity_id_from_args,
    extract_ttl_from_result,
    generate_cache_key_with_entity_id,
    generate_cache_key_with_prefix,
    get_deployment_id_for_cache,
    get_effective_ttl,
)

T = TypeVar("T")

logger: logging.Logger = logging.getLogger("peak.cache")


def _invalidate_cache_decorator_wrapper(
    func: Callable[..., T],
    *,
    is_coroutine: bool,
    invalidate_func: Callable[..., None],
) -> Callable[..., T]:
    """Create sync or async wrapper with common error handling."""

    @functools.wraps(func)
    def sync_wrapper(*args: Any, **kwargs: Any) -> T:
        try:
            result = func(*args, **kwargs)
            invalidate_func(*args, **kwargs)
            return _add_cache_control_headers(result)  # type: ignore[return-value]
        except Exception:
            logger.exception("Function failed, skipping cache invalidation")
            raise

    @functools.wraps(func)
    async def async_wrapper(*args: Any, **kwargs: Any) -> T:
        try:
            result = await func(*args, **kwargs)  # type: ignore[misc]
            invalidate_func(*args, **kwargs)
            return _add_cache_control_headers(result)  # type: ignore[return-value]
        except Exception:
            logger.exception("Async function failed, skipping cache invalidation")
            raise

    return async_wrapper if is_coroutine else sync_wrapper  # type: ignore[return-value]


def invalidate_cache_patterns(patterns: List[str], additional_prefix: Optional[str] = None) -> None:
    """Invalidate cache entries matching the given patterns.

    Args:
        patterns: List of cache key patterns to invalidate
        additional_prefix: Optional additional prefix for cache keys
    """
    try:
        cache_repo = PlatformCacheRepository()

        for pattern in patterns:
            if additional_prefix:
                full_pattern = f"{additional_prefix}:{pattern}"
            else:
                deployment_id = get_deployment_id_for_cache()
                full_pattern = f"{deployment_id}:{pattern}"

            logger.info("Invalidating cache pattern %s", full_pattern)
            cache_repo.delete_by_prefix(full_pattern)

    except Exception:
        logger.exception("Error during cache pattern invalidation")


def _handle_broad_patterns_invalidation(broad_patterns: Optional[List[str]], deployment_id: str) -> None:
    """Handle invalidation of broad cache patterns."""
    if broad_patterns:
        invalidate_cache_patterns(broad_patterns, deployment_id)


def _handle_entity_id_invalidation(
    entity_id_param: Optional[str],
    args: tuple[Any, ...],
    kwargs: dict[str, Any],
    deployment_id: str,
) -> None:
    """Handle invalidation based on entity ID."""
    if entity_id_param:
        entity_id = _extract_entity_id_from_args(args, kwargs, entity_id_param)
        if entity_id:
            specific_patterns = [f"*:{entity_id}:*"]
            invalidate_cache_patterns(specific_patterns, deployment_id)


def _create_invalidate_function(
    entity_id_param: Optional[str],
    broad_patterns: Optional[List[str]],
) -> Callable[..., None]:
    """Create the invalidation function with the given parameters."""

    def invalidate(*args: Any, **kwargs: Any) -> None:
        try:
            deployment_id = get_deployment_id_for_cache()
            logger.info("Invalidating cache for deployment: %s", deployment_id)

            if deployment_id:
                _handle_broad_patterns_invalidation(broad_patterns, deployment_id)
                _handle_entity_id_invalidation(entity_id_param, args, kwargs, deployment_id)

        except Exception:
            logger.exception("Error during cache invalidation")

    return invalidate


def _create_decorator_wrapper(
    inner_func: Callable[..., T],
    invalidate_func: Callable[..., None],
) -> Callable[..., T]:
    """Create the decorator wrapper for the given function."""
    is_coroutine = inspect.iscoroutinefunction(inner_func)

    @functools.wraps(inner_func)
    async def async_wrapper(*args: Any, **kwargs: Any) -> T:
        return await _invalidate_cache_decorator_wrapper(  # type: ignore[no-any-return,misc]
            inner_func,
            is_coroutine=True,
            invalidate_func=invalidate_func,
        )(*args, **kwargs)

    @functools.wraps(inner_func)
    def sync_wrapper(*args: Any, **kwargs: Any) -> T:
        return _invalidate_cache_decorator_wrapper(
            inner_func,
            is_coroutine=False,
            invalidate_func=invalidate_func,
        )(*args, **kwargs)

    return async_wrapper if is_coroutine else sync_wrapper  # type: ignore[return-value]


def invalidate_cache(  # noqa: C901
    func: Optional[Callable[..., T]] = None,
    *,
    entity_id_param: Optional[str] = None,
    targeted_patterns: Optional[List[str]] = None,
    broad_patterns: Optional[List[str]] = None,
) -> Union[Callable[..., T], Callable[..., Any]]:
    """Cache invalidation utility usable both as a decorator and standalone function.

    Args:
        func: The function to decorate (only when used as a decorator)
        entity_id_param: Name of the parameter containing the entity ID
        targeted_patterns: List of patterns for targeted invalidation
        broad_patterns: List of patterns for broad invalidation

    Returns:
        Either the decorated function (when used as decorator) or a decorator function.
    """

    def invalidate(*args: Any, **kwargs: Any) -> None:
        try:
            entity_id = _extract_entity_id_from_args(args, kwargs, entity_id_param)
            if targeted_patterns and entity_id:
                patterns = [f"{p}:{entity_id}" for p in targeted_patterns]
                logger.info("Targeted invalidation patterns %s", patterns)
                invalidate_cache_patterns(patterns)
            if broad_patterns:
                logger.info("Broad invalidation patterns: %s", broad_patterns)
                invalidate_cache_patterns(broad_patterns)
        except Exception:
            logger.exception("Error during cache invalidation")
            raise

    def decorator(inner_func: Callable[..., T]) -> Callable[..., T]:
        is_coroutine = inspect.iscoroutinefunction(inner_func)

        @functools.wraps(inner_func)
        async def async_wrapper(*args: Any, **kwargs: Any) -> T:
            result = await inner_func(*args, **kwargs)  # type: ignore[misc]
            invalidate(*args, **kwargs)
            return result  # type: ignore[no-any-return]

        @functools.wraps(inner_func)
        def sync_wrapper(*args: Any, **kwargs: Any) -> T:
            result = inner_func(*args, **kwargs)
            invalidate(*args, **kwargs)
            return result

        return async_wrapper if is_coroutine else sync_wrapper  # type: ignore[return-value]

    if func is not None:
        return decorator(func)
    else:  # noqa: RET505

        def wrapper(*args: Any, **kwargs: Any) -> T:
            if args and callable(args[0]) and not kwargs:
                return decorator(args[0])  # type: ignore[return-value]
            invalidate(*args, **kwargs)
            return args[0] if args else kwargs  # type: ignore[return-value]

        return wrapper


def _get_additional_prefix(additional_prefix: Optional[str]) -> Optional[str]:
    """Get the additional prefix for cache keys."""
    if additional_prefix:
        return additional_prefix
    try:
        return get_deployment_id_for_cache()
    except Exception:
        logger.exception("Error getting deployment ID")
        return None


def _get_cache_key(
    func: Callable[..., T],
    args: tuple[Any, ...],
    kwargs: dict[str, Any],
    custom_key_func: Optional[Callable[[Callable[..., Any], tuple[Any, ...], dict[str, Any]], str]],
    entity_id_param: Optional[str],
    key_prefix: Optional[str],
) -> str:
    """Generate cache key for the function call."""
    if custom_key_func:
        base_key = custom_key_func(func, args, kwargs)
    else:
        base_key = generate_cache_key_with_entity_id(args, kwargs, key_prefix or "cached", entity_id_param)
    current_additional_prefix = get_deployment_id_for_cache()
    return generate_cache_key_with_prefix(base_key, current_additional_prefix)


def _get_cache_client() -> Optional[PlatformCacheRepository]:
    """Get the cache client instance."""
    try:
        return PlatformCacheRepository()
    except Exception:
        logger.exception("Error getting cache client")
        return None


def _handle_cache_operations(
    func: Callable[..., T],
    args: tuple[Any, ...],
    kwargs: dict[str, Any],
    cache_client: PlatformCacheRepository,
    cache_key: str,
    ttl: Optional[int],
    *,
    respect_cache_control: bool = False,
) -> T:
    """Handle cache operations for sync functions."""
    logger.info("Checking cache for key: %s", cache_key)

    cached_value = cache_client.get(cache_key)
    if cached_value is not None:
        logger.info("Cache hit for key: %s", cache_key)
        return cached_value  # type: ignore[no-any-return]

    logger.info("Cache miss for key: %s", cache_key)
    result = func(*args, **kwargs)
    effective_ttl = get_effective_ttl(args, kwargs, ttl or 3600, respect_cache_control)
    if effective_ttl is None:
        logger.info("Skipping cache due to Cache-Control directives")
        return func(*args, **kwargs)

    final_ttl = extract_ttl_from_result(result) or effective_ttl

    if final_ttl is not None:
        cache_client.set(cache_key, result, final_ttl)
        logger.info("Cached result for key: %s with TTL: %s", cache_key, effective_ttl)

    return result


async def _handle_cache_operations_async(
    func: Callable[..., T],
    args: tuple[Any, ...],
    kwargs: dict[str, Any],
    cache_client: PlatformCacheRepository,
    cache_key: str,
    ttl: Optional[int],
    *,
    respect_cache_control: bool = False,
) -> T:
    """Handle cache operations for async functions."""
    logger.info("Checking cache for key: %s", cache_key)

    cached_value = cache_client.get(cache_key)
    if cached_value is not None:
        logger.info("Cache hit for key: %s", cache_key)
        return cached_value  # type: ignore[no-any-return]

    logger.info("Cache miss for key: %s", cache_key)
    result = await func(*args, **kwargs)  # type: ignore[misc]

    effective_ttl = get_effective_ttl(args, kwargs, ttl or 3600, respect_cache_control)
    if effective_ttl is None:
        logger.info("Skipping cache due to Cache-Control directives")
        return func(*args, **kwargs)
    final_ttl = extract_ttl_from_result(result) or effective_ttl
    if final_ttl is not None:
        cache_client.set(cache_key, result, effective_ttl)
        logger.info("Cached result for key: %s with TTL: %s", cache_key, effective_ttl)

    return result  # type: ignore[no-any-return]


def _create_sync_wrapper(
    func: Callable[..., T],
    custom_key_func: Optional[Callable[[Callable[..., Any], tuple[Any, ...], dict[str, Any]], str]],
    entity_id_param: Optional[str],
    key_prefix: Optional[str],
    ttl: Optional[int],
    *,
    respect_cache_control: bool,
) -> Callable[..., T]:
    """Create sync wrapper for caching."""

    @functools.wraps(func)
    def sync_wrapper(*args: Any, **kwargs: Any) -> T:
        try:
            cache_client = _get_cache_client()
            if not cache_client:
                return func(*args, **kwargs)

            cache_key = _get_cache_key(func, args, kwargs, custom_key_func, entity_id_param, key_prefix)
            return _handle_cache_operations(
                func,
                args,
                kwargs,
                cache_client,
                cache_key,
                ttl,
                respect_cache_control=respect_cache_control,
            )

        except Exception:
            logger.exception("Error in cache wrapper")
            return func(*args, **kwargs)

    return sync_wrapper


def _create_async_wrapper(
    func: Callable[..., T],
    custom_key_func: Optional[Callable[[Callable[..., Any], tuple[Any, ...], dict[str, Any]], str]],
    entity_id_param: Optional[str],
    key_prefix: Optional[str],
    ttl: Optional[int],
    *,
    respect_cache_control: bool,
) -> Callable[..., T]:
    """Create async wrapper for caching."""

    @functools.wraps(func)
    async def async_wrapper(*args: Any, **kwargs: Any) -> T:
        try:
            cache_client = _get_cache_client()
            if not cache_client:
                return await func(*args, **kwargs)  # type: ignore[no-any-return,misc]  # type: ignore[no-any-return,misc]
            cache_key = _get_cache_key(func, args, kwargs, custom_key_func, entity_id_param, key_prefix)
            return await _handle_cache_operations_async(
                func,
                args,
                kwargs,
                cache_client,
                cache_key,
                ttl,
                respect_cache_control=respect_cache_control,
            )

        except Exception:
            logger.exception("Error in async cache wrapper")
            return await func(*args, **kwargs)  # type: ignore[no-any-return,misc]

    return async_wrapper  # type: ignore[return-value]


def cache_result(
    ttl: Optional[int] = 3600,
    key_prefix: Optional[str] = None,
    custom_key_func: Optional[Callable[[Callable[..., Any], tuple[Any, ...], dict[str, Any]], str]] = None,
    additional_prefix: Optional[str] = None,
    *,
    respect_cache_control: bool = False,
    entity_id_param: Optional[str] = None,
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """Cache the result of a function call.

    Args:
        ttl: Time to live for cached values in seconds.
        key_prefix: Prefix for cache keys.
        custom_key_func: Custom function to generate cache keys.
        additional_prefix: Additional prefix for cache keys.
        respect_cache_control: Whether to respect HTTP cache control headers.
        entity_id_param: Parameter name containing the entity ID.

    Returns:
        Decorator function that caches the result of the decorated function.
    """
    _get_additional_prefix(additional_prefix)  # Validate but don't use yet

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        is_coroutine = inspect.iscoroutinefunction(func)

        if is_coroutine:
            return _create_async_wrapper(
                func,
                custom_key_func,
                entity_id_param,
                key_prefix,
                ttl,
                respect_cache_control=respect_cache_control,
            )
        return _create_sync_wrapper(
            func,
            custom_key_func,
            entity_id_param,
            key_prefix,
            ttl,
            respect_cache_control=respect_cache_control,
        )

    return decorator
