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
"""Utility functions for cache decorators.

This module provides utility functions for cache key generation, serialization,
deserialization, and cache control header handling.
"""

from __future__ import annotations

import ast
import base64
import json
import logging
import os
import uuid
from collections import defaultdict
from datetime import date, datetime
from decimal import Decimal
from functools import lru_cache
from importlib.util import find_spec
from typing import TYPE_CHECKING, Any, Dict, Optional, Union

if TYPE_CHECKING:
    import numpy as np
    import pandas as pd
    from starlette.responses import JSONResponse, Response
else:
    # Runtime imports with fallbacks
    try:
        import numpy as np  # type: ignore[attr-defined]
    except ImportError:
        np = None  # type: ignore[assignment,misc]

    try:
        import pandas as pd  # type: ignore[attr-defined]
    except ImportError:
        pd = None  # type: ignore[assignment,misc]

    try:
        from starlette.responses import JSONResponse, Response
    except ImportError:
        JSONResponse = None
        Response = None

from peak.press.blocks import get_client

from .exceptions import CacheDeserializationError, CacheSerializationError

logger: logging.Logger = logging.getLogger("peak.cache")

# Check for pydantic availability
if find_spec("pydantic") is not None:
    import pydantic  # type: ignore[import-not-found]
else:
    pydantic = None

# Registry of safe object types that can be evaluated
SAFE_OBJECTS = {
    "Decimal": Decimal,
    "datetime": datetime,
    "date": date,
    "pd.Timestamp": pd.Timestamp if pd else None,
    "Timestamp": pd.Timestamp if pd else None,
    "uuid.UUID": uuid.UUID,
    "UUID": uuid.UUID,
}

MIN_ARGS_LENGTH = 2
MIN_TUPLE_LENGTH = 2
ISO_DATE_LENGTH = 10
ISO_DATE_HYPHENS = 2
UUID_LENGTH = 36
UUID_HYPHENS = 4


def _safe_eval_string(obj_str: str) -> Any:
    """Safely evaluate a string representation of an object.

    Handles custom object types by using a registry of safe objects.
    """
    try:
        return ast.literal_eval(obj_str)
    except (ValueError, SyntaxError):
        try:
            safe_dict: dict[str, Any] = {"__builtins__": {}}
            safe_dict.update({k: v for k, v in SAFE_OBJECTS.items() if v is not None})

            return eval(obj_str, safe_dict)  # noqa: S307
        except Exception:  # noqa: BLE001
            return obj_str


def deserialize_from_cache(obj: Any) -> Any:  # noqa: PLR0911
    """Deserializes cached data back to its original format.Handles the case where objects were converted to strings during serialization.This function mirrors the types handled by serialize_for_cache."""
    if obj is None or isinstance(obj, (int, float, bool)):
        return obj

    if isinstance(obj, str):
        try:
            parsed = json.loads(obj)
            return deserialize_from_cache(parsed)
        except (json.JSONDecodeError, ValueError):
            pass

        if obj.startswith("{") and obj.endswith("}"):  # noqa: SIM114
            try:
                parsed = _safe_eval_string(obj)
                return deserialize_from_cache(parsed)
            except Exception:  # noqa: BLE001
                return obj
        elif obj.startswith("[") and obj.endswith("]"):
            try:
                parsed = _safe_eval_string(obj)
                return deserialize_from_cache(parsed)
            except Exception:  # noqa: BLE001
                return obj

    if isinstance(obj, (list, tuple)):
        return [deserialize_from_cache(item) for item in obj]

    if isinstance(obj, dict):
        return {key: deserialize_from_cache(value) for key, value in obj.items()}

    return obj


def _serialize_basic_types(obj: Any) -> Any:
    """Serialize basic types that don't need special handling."""
    if obj is None or isinstance(obj, (int, float, bool, str)):
        return obj
    return None


def _serialize_numpy_objects(obj: Any) -> Any:
    """Serialize numpy objects."""
    if np is not None:
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.bool_):
            return bool(obj)
    return None


def _serialize_pandas_objects(obj: Any) -> Any:
    """Serialize pandas objects."""
    if pd is not None:
        if isinstance(obj, pd.DataFrame):
            return obj.to_dict(orient="records")
        if isinstance(obj, pd.Series):
            return obj.to_dict()
        if isinstance(obj, pd.Timestamp):
            return obj.isoformat()
    return None


def _serialize_datetime_objects(obj: Any) -> Any:
    """Serialize datetime objects."""
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    return None


def _serialize_decimal_objects(obj: Any) -> Any:
    """Serialize decimal objects."""
    if isinstance(obj, Decimal):
        return str(obj)
    return None


def _serialize_uuid_objects(obj: Any) -> Any:
    """Serialize UUID objects."""
    if isinstance(obj, uuid.UUID):
        return str(obj)
    return None


def _serialize_complex_objects(obj: Any) -> Any:
    """Serialize complex objects that need special handling."""
    # Try JSON serialization first
    try:
        json.dumps(obj)
        return obj  # noqa: TRY300
    except (TypeError, ValueError):
        pass

    try:
        return str(obj)
    except Exception as e:  # noqa: BLE001
        error_msg = f"Unable to serialize object of type {type(obj)}"
        raise CacheSerializationError(error_msg) from e


def _serialize_pydantic_object(obj: Any) -> Any:
    """Serialize Pydantic model objects."""
    if pydantic is not None:
        base_model = getattr(pydantic, "BaseModel", None)

        if base_model and isinstance(obj, base_model):
            if hasattr(obj, "model_dump"):
                return obj.model_dump()
            if hasattr(obj, "dict"):
                return obj.dict()

    return None


def serialize_for_cache(obj: Any) -> Any:  # noqa: PLR0911
    """Serializes objects for caching.

    Handles various data types including numpy arrays, pandas objects,
    datetime objects, and custom objects by converting them to JSON-serializable formats.
    """
    # Handle basic types
    basic_result = _serialize_basic_types(obj)
    if basic_result is not None:
        return basic_result

    # Handle numpy objects
    numpy_result = _serialize_numpy_objects(obj)
    if numpy_result is not None:
        return numpy_result

    # Handle pandas objects
    pandas_result = _serialize_pandas_objects(obj)
    if pandas_result is not None:
        return pandas_result

    # Handle datetime objects
    datetime_result = _serialize_datetime_objects(obj)
    if datetime_result is not None:
        return datetime_result

    # Handle decimal objects
    decimal_result = _serialize_decimal_objects(obj)
    if decimal_result is not None:
        return decimal_result

    # Handle UUID objects
    uuid_result = _serialize_uuid_objects(obj)
    if uuid_result is not None:
        return uuid_result

    # Handle lists and dicts
    if isinstance(obj, list):
        return [serialize_for_cache(item) for item in obj]
    if isinstance(obj, dict):
        return {key: serialize_for_cache(value) for key, value in obj.items()}

    # Handle Pydantic models
    pydantic_result = _serialize_pydantic_object(obj)
    if pydantic_result is not None:
        return serialize_for_cache(pydantic_result)

    # Handle complex objects
    return _serialize_complex_objects(obj)


@lru_cache(maxsize=1)
def get_deployment_id_for_cache() -> Optional[str]:
    """Get the deployment ID for cache key generation.

    Returns:
        The deployment ID if available, None otherwise.

    Raises:
        Exception: If there is an error retrieving the deployment information.
    """
    press_deployment_id = os.getenv("PRESS_DEPLOYMENT_ID")
    if not press_deployment_id:
        return None
    try:
        block_deployment = get_client().describe_deployment(press_deployment_id)
        parent = block_deployment.get("parent")
        if parent and parent.get("id"):
            return parent["id"]  # type: ignore [no-any-return]
        else:  # noqa: RET505
            return press_deployment_id
    except Exception:
        logging.exception("Failed to get deployment ID for cache key generation.")
        raise


def encode_data(data: Dict[str, Any]) -> str:
    """Encode data as a base64 string.

    Args:
        data: The data to encode.

    Returns:
        Base64 encoded string.
    """
    json_str = json.dumps(data, sort_keys=True)
    return base64.b64encode(json_str.encode()).decode()


def decode_cache_key(cache_key: str) -> Dict[str, Any]:
    """Decode a cache key back to its original data.

    Args:
        cache_key: The cache key to decode.

    Returns:
        The decoded data.

    Raises:
        CacheDeserializationError: If the cache key cannot be decoded.
    """
    try:
        decoded_bytes = base64.b64decode(cache_key.encode())
        json_str = decoded_bytes.decode()
        return json.loads(json_str)  # type: ignore[no-any-return]
    except Exception as e:  # noqa: BLE001
        error_msg = f"Failed to decode cache key: {e}"
        raise CacheDeserializationError(error_msg) from e


def _find_request_object(args: tuple[Any, ...], kwargs: dict[str, Any]) -> Any:
    """Find a request object in function arguments.

    Args:
        args: Function arguments.
        kwargs: Function keyword arguments.

    Returns:
        The request object if found, None otherwise.
    """
    for arg in args:
        if hasattr(arg, "headers") and hasattr(arg, "method"):
            return arg

    for value in kwargs.values():
        if hasattr(value, "headers") and hasattr(value, "method"):
            return value

    return None


def generate_cache_key_with_entity_id(  # noqa: C901 PLR0912
    args: tuple[Any, ...],
    kwargs: dict[str, Any],
    prefix: str = "cached",
    entity_id_param: Optional[str] = None,
) -> str:
    """Generates a cache key for FastAPI GET requests with entity ID support."""
    request = _find_request_object(args, kwargs)
    entity_id = None

    if entity_id_param and request and hasattr(request, "path_params"):
        entity_id = request.path_params.get(entity_id_param)

    if not entity_id and entity_id_param and entity_id_param in kwargs:
        entity_id = kwargs[entity_id_param]

    if not entity_id and entity_id_param:
        start_idx = 1 if request and request in args else 0
        if len(args) > start_idx:
            entity_id = args[start_idx]

    if not entity_id and request and hasattr(request, "path_params"):
        for param_name, param_value in request.path_params.items():
            if param_name.endswith(("_id", "Id")):
                entity_id = param_value
                break

    if request is not None:
        method = getattr(request, "method", "GET").upper()
        if method != "GET":
            raise Exception("Caching is only supported for GET requests.")  # noqa: TRY002 TRY003 EM101

        query_items = request.query_params.multi_items()
        query_dict: Dict[str, Any] = defaultdict(list)

        for key, value in query_items:
            query_dict[key].append(value)

        for key, value in query_dict.items():
            if len(value) == 1:
                query_dict[key] = value[0]

        path_params = dict(request.path_params)
        combined_params = {
            "path": dict(sorted(path_params.items())),
            "query": dict(sorted(query_dict.items())),
        }

        key_hash = encode_data(combined_params)
        if entity_id:
            return f"{prefix}:{entity_id}:{key_hash}"
        return f"{prefix}:{key_hash}"

    filtered_args = tuple(arg for arg in args if not (hasattr(arg, "query_params") and hasattr(arg, "path_params")))
    fallback_kwargs = {k: v for k, v in kwargs.items() if k != "request"}

    key_data = {
        "args": filtered_args,
        "kwargs": fallback_kwargs,
    }
    key_hash = encode_data(key_data)

    if entity_id:
        return f"{prefix}:{entity_id}:{key_hash}"
    return f"{prefix}:{key_hash}"


def generate_cache_key_with_prefix(
    base_key: str,
    additional_prefix: Optional[str] = None,
) -> str:
    """Generate a cache key with an optional additional prefix."""
    if additional_prefix:
        return f"{additional_prefix}:{base_key}"
    return base_key


def extract_ttl_from_result(result: Any) -> Optional[int]:
    """Extract TTL from a function result.

    Args:
        result: The function result.

    Returns:
        The TTL if found, None otherwise.
    """
    if isinstance(result, tuple) and len(result) == MIN_TUPLE_LENGTH and isinstance(result[1], int):
        return result[1]
    return None


def extract_result_value(result: Any) -> Any:
    """Extract the actual result value from a function result.

    Args:
        result: The function result.

    Returns:
        The actual result value.
    """
    if isinstance(result, tuple) and len(result) == MIN_TUPLE_LENGTH:
        return result[0]
    return result


def parse_cache_control_header(header_value: Optional[str]) -> Dict[str, Any]:
    """Parse a Cache-Control header value.

    Args:
        header_value: The Cache-Control header value.

    Returns:
        A dictionary of directives and their values.
    """
    if not header_value:
        return {}

    directives: Dict[str, Any] = {}
    parts = header_value.split(",")

    for part in parts:
        directive = part.strip().lower()
        if "=" in directive:
            key, value = directive.split("=", 1)
            key = key.strip()
            value = value.strip()
            try:
                directives[key] = int(value)
            except ValueError:
                directives[key] = value
        else:
            directives[directive] = True

    return directives


def should_cache_response(directives: Dict[str, Any]) -> bool:
    """Determine if a response should be cached based on Cache-Control directives.

    Args:
        directives: Cache-Control directives.

    Returns:
        True if the response should be cached, False otherwise.
    """
    if directives.get("no-store") or directives.get("no-cache"):
        return False

    if directives.get("must-revalidate"):
        return False

    return True


def get_cache_ttl_from_headers(
    directives: Dict[str, Any],
    default_ttl: int,
) -> Optional[int]:
    """Get the TTL from Cache-Control headers.

    Args:
        directives: Cache-Control directives.
        default_ttl: Default TTL to use if no directive is found.

    Returns:
        The TTL if caching is allowed, None otherwise.
    """
    if not should_cache_response(directives):
        return None

    # Use max-age if present
    if "max-age" in directives:
        return int(directives["max-age"])

    # Use s-maxage if present (but only for shared caches)
    if "s-maxage" in directives:
        return int(directives["s-maxage"])

    return default_ttl


def extract_cache_control_from_request(request: Any) -> Optional[str]:
    """Extract Cache-Control header from a request object.

    Args:
        request: The request object.

    Returns:
        The Cache-Control header value if found, None otherwise.
    """
    if not request:
        return None

    if hasattr(request, "headers"):
        headers = request.headers
        if hasattr(headers, "get"):
            cache_control = headers.get("cache-control")
            return str(cache_control) if cache_control is not None else None
        if isinstance(headers, dict):
            return headers.get("cache-control")

    return None


def _extract_entity_id_from_args(
    args: tuple[Any, ...],
    kwargs: dict[str, Any],
    entity_id_param: Optional[str] = None,
) -> Optional[str]:
    """Extract entity ID from function arguments.

    Args:
        args: Function arguments.
        kwargs: Function keyword arguments.
        entity_id_param: Parameter name containing the entity ID.

    Returns:
        The entity ID if found, None otherwise.
    """
    if not entity_id_param:
        return None

    if entity_id_param in kwargs:
        return str(kwargs[entity_id_param])

    for arg in args:
        if hasattr(arg, "path_params") and entity_id_param in arg.path_params:
            return str(arg.path_params[entity_id_param])
        if hasattr(arg, "query_params") and entity_id_param in arg.query_params:
            return str(arg.query_params[entity_id_param])

    return None


def _add_cache_control_headers(
    result: Union[dict[str, Any], Any],
) -> Union[dict[str, Any], Any]:
    """Add cache control headers to a response.

    Args:
        result: The response object.

    Returns:
        The response object with cache control headers added.
    """
    if isinstance(result, dict):
        return result

    if hasattr(result, "headers"):
        result.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        result.headers["Pragma"] = "no-cache"
        result.headers["Expires"] = "0"

    return result


def get_effective_ttl(
    args: tuple[Any, ...],
    kwargs: dict[str, Any],
    default_ttl: int,
    respect_cache_control: bool = False,  # noqa: RUF100 FBT001 FBT002
) -> Optional[int]:  # noqa: RUF100 FBT001 FBT002
    """Get effective TTL considering Cache-Control headers if enabled."""
    if not respect_cache_control:
        return default_ttl

    request = _find_request_object(args, kwargs)
    if not request:
        return default_ttl

    cache_control_header = extract_cache_control_from_request(request)
    if not cache_control_header:
        return default_ttl

    directives = parse_cache_control_header(cache_control_header)
    logger.debug("Parsed Cache-Control directives: %s", directives)

    effective_ttl = get_cache_ttl_from_headers(directives, default_ttl)

    if effective_ttl is None:
        logger.info("Cache-Control directives prevent caching")
    elif effective_ttl != default_ttl:
        logger.info("Using TTL from Cache-Control: %s s (default: %s s)", effective_ttl, default_ttl)

    return effective_ttl
