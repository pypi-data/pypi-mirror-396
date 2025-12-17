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
"""Logging module, a wrapper around `structlog <https://www.structlog.org/en/stable/>`_ library."""

from __future__ import annotations

import functools
import inspect
import logging
import os
import sys
from types import MappingProxyType
from typing import Any, Callable, Final, Hashable, List, MutableMapping, Optional, Tuple, Union

import orjson
import structlog

from .log_handler import LogHandler
from .log_level import LOG_LEVEL_NAMES_TO_LOG_LEVEL, LogLevel, LogLevelNames
from .utils import mask_nested_pii_data

__title__ = "logging"
__author__ = "PEAK AI"
__license__ = "Apache License, Version 2.0"
__copyright__ = "2024, Peak AI"
__status__ = "production"
__date__ = "14 March 2024"

__all__: List[str] = [
    "DEFAULT_SHARED_PROCESSORS",
    "LOG_LEVEL_NAMES_TO_LOG_LEVEL",
    "LogHandler",
    "LogLevelNames",
    "LogLevel",
    "PeakLogger",
    "setup_logging",
    "default_processors_factory",
    "get_logger",
    "pii_masking_processor",
    "peak_contexts_processor",
]


# ---------------------------------------------------------------------------
# Global Configuration State
# ---------------------------------------------------------------------------


_global_config: dict[str, Any] = {
    "configured": False,
    "default_level": LogLevel.INFO,
    "disable_masking": False,
    "legacy": True,
}

_explicit_level_loggers: set[str] = set()
_legacy_set_loggers: set[str] = set()


def setup_logging(
    *,
    default_level: LogLevel = LogLevel.INFO,
    disable_masking: bool = False,
) -> None:
    """Configure global defaults for all Peak loggers.

    This function sets a global configuration that affects all subsequently created
    loggers via `get_logger()`. Call this once at application startup.

    Args:
        default_level (LogLevel): Default log level for new loggers. Defaults to INFO.
        disable_masking (bool): Disable PII masking in logs globally. Defaults to False.

    Example:
        Application with hierarchy (recommended for module-level loggers):

        >>> # module.py - module-level logger created at import time
        >>> from peak.tools.logging import get_logger
        >>> module_logger = get_logger("myapp.module")
        >>>
        >>> # main.py - configure logging after imports
        >>> from peak.tools.logging import setup_logging, LogLevel
        >>> setup_logging(default_level=LogLevel.DEBUG)
        >>>
        >>> # module_logger now inherits DEBUG level from root
        >>> module_logger.debug("This will be visible!")  # Works!

        Application with logger levels:

        >>> from peak.tools.logging import setup_logging, get_logger, LogLevel
        >>> setup_logging(default_level=LogLevel.INFO)
        >>> logger = get_logger("myapp", level=LogLevel.DEBUG)  # Explicit level overrides global

    """
    _global_config["configured"] = True
    _global_config["default_level"] = default_level
    _global_config["disable_masking"] = disable_masking
    _global_config["legacy"] = False

    root_logger = logging.getLogger()
    root_logger.setLevel(default_level.value)

    if not root_logger.handlers:
        root_logger.addHandler(logging.NullHandler())

    for logger_name in list(logging.Logger.manager.loggerDict.keys()):
        if not logger_name or logger_name in _explicit_level_loggers:
            continue

        existing_logger = logging.getLogger(logger_name)
        if isinstance(existing_logger, logging.Logger):
            existing_logger.setLevel(logging.NOTSET)

    for logger_name in list(_legacy_set_loggers):
        if logger_name not in _explicit_level_loggers:
            existing_logger = logging.getLogger(logger_name)
            if isinstance(existing_logger, logging.Logger):
                existing_logger.setLevel(logging.NOTSET)
        _legacy_set_loggers.discard(logger_name)


# ---------------------------------------------------------------------------
# Utility private functions
# ---------------------------------------------------------------------------


def pii_masking_processor(
    _: str,
    __: str,
    event_dict: MutableMapping[str, Any],
) -> MutableMapping[str, Any]:
    """Masks sensitive PII data present in event_dict."""
    return mask_nested_pii_data(event_dict)


def peak_contexts_processor(
    _: str,
    __: str,
    event_dict: MutableMapping[str, Any],
) -> MutableMapping[str, Any]:
    """Add the standard attribute to the event_dict."""
    attributes_to_add: dict[str, Any] = {
        "source": "peak-sdk",
        "runtime": os.getenv("PEAK_RUNTIME"),
        "press_deployment_id": os.getenv("PRESS_DEPLOYMENT_ID"),
        "run_id": os.getenv("PEAK_RUN_ID"),
        "exec_id": os.getenv("PEAK_EXEC_ID"),
        "stage": os.getenv("PEAK__STAGE", os.getenv("STAGE")),
        "tenant_name": os.getenv("TENANT_NAME", os.getenv("TENANT")),
        "tenant_id": os.getenv("TENANT_ID"),
        "api_name": os.getenv("PEAK_API_NAME"),
        "api_id": os.getenv("PEAK_API_ID"),
        "step_name": os.getenv("PEAK_STEP_NAME"),
        "step_id": os.getenv("PEAK_STEP_ID"),
        "webapp_name": os.getenv("PEAK_WEBAPP_NAME"),
        "webapp_id": os.getenv("PEAK_WEBAPP_ID"),
        "workflow_name": os.getenv("PEAK_WORKFLOW_NAME"),
        "workflow_id": os.getenv("PEAK_WORKFLOW_ID"),
        "workspace_name": os.getenv("PEAK_WORKSPACE_NAME"),
        "workspace_id": os.getenv("PEAK_WORKSPACE_ID"),
        "image_name": os.getenv("PEAK_IMAGE_NAME"),
        "image_id": os.getenv("PEAK_IMAGE_ID"),
    }

    for attr, value in attributes_to_add.items():
        if value:
            event_dict[attr] = value

    return event_dict


# ---------------------------------------------------------------------------
# Utility functions at module level for main logger factory
# ---------------------------------------------------------------------------


DEFAULT_SHARED_PROCESSORS: Tuple[structlog.types.Processor | Any, ...] = (
    structlog.contextvars.merge_contextvars,
    peak_contexts_processor,
    # NOTE: Removed filter_by_level - redundant when using make_filtering_bound_logger
    structlog.stdlib.add_logger_name,
    structlog.stdlib.add_log_level,
    structlog.stdlib.PositionalArgumentsFormatter(),
    pii_masking_processor,
    structlog.processors.TimeStamper(fmt="iso"),
    structlog.processors.StackInfoRenderer(),
    # NOTE: Removed format_exc_info - using dict_tracebacks in JSONRenderer instead
    # NOTE: Removed UnicodeDecoder - may interfere with orjson byte output
    structlog.processors.EventRenamer("message"),
)

_ORJSON_OPTS: Final[int] = (
    orjson.OPT_SERIALIZE_NUMPY
    | orjson.OPT_SERIALIZE_DATACLASS
    | orjson.OPT_SERIALIZE_UUID
    | orjson.OPT_NON_STR_KEYS
    | orjson.OPT_SORT_KEYS
)


def _orjson_serializer(
    obj: Any,
    sort_keys: Optional[bool] = None,
    default: Callable[[Any], Any] = str,
) -> str:
    """Custom serializer using orjson.dumps for structlog."""
    apply_opts: int = (_ORJSON_OPTS | orjson.OPT_SORT_KEYS) if sort_keys else _ORJSON_OPTS

    return orjson.dumps(obj, option=apply_opts, default=default).decode("utf-8")


@functools.lru_cache(maxsize=4, typed=True)
def default_processors_factory(
    disable_masking: Optional[bool],
) -> list[structlog.types.Processor | Any]:
    """Return the default processors for PeakLogger.

    Args:
        disable_masking (Optional[bool], optional): Whether to disable masking of sensitive data. Defaults to False.

    Returns:
        list[structlog.types.Processor | Any]: List of processors to be used by the logger.
    """
    _processors = list(DEFAULT_SHARED_PROCESSORS)

    if disable_masking:
        _processors.remove(pii_masking_processor)

    # add renderer based on the environment
    if sys.stdout.isatty():
        # Pretty printing when we run in a terminal session.
        _processors.append(
            structlog.dev.ConsoleRenderer(
                colors=True,
                event_key="message",
                timestamp_key="timestamp",
                exception_formatter=structlog.dev.RichTracebackFormatter(color_system="truecolor"),
            ),
        )
    else:
        # Print JSON when we run in production
        # Add dict_tracebacks for proper exception formatting in JSON
        _processors.append(structlog.processors.dict_tracebacks)
        # Use orjson.dumps directly (returns bytes, which JSONRenderer handles)
        _processors.append(structlog.processors.JSONRenderer(serializer=orjson.dumps))

    return _processors


@functools.lru_cache(maxsize=128, typed=True)
def _handle_and_patch_processor_factory_kwargs(
    func: Callable[..., List[structlog.types.Processor | Any]],
    *,
    disable_masking: bool = False,
    **kwargs: Hashable,
) -> List[structlog.types.Processor | Any]:
    """Handle keyword arguments for custom_processors_factory using inspect.signature, additionally patch the processors list to include EventRenamer in the right position if not already present.

    Unknown keyword arguments are ignored.

    Args:
        func (Callable[..., List[structlog.types.Processor | Any]]): Custom processor factory function.
        disable_masking (bool): Whether to disable masking of sensitive data. Defaults to False.
        **kwargs: Additional keyword arguments to be passed to the custom_processors_factory, if provided.
            kwargs received by the factory function must be hashable else TypeError will be raised by this wrapper.

    Returns:
        List[structlog.types.Processor | Any]: List of processors to be used by the logger.

    Raises:
        ValueError: If multiple renderers are found in the processor factory's returned processors list.
    """
    func_params: MappingProxyType[str, inspect.Parameter] = inspect.signature(func).parameters
    filter_kwargs = {"disable_masking": disable_masking, **kwargs}
    _processors = func(**{k: v for k, v in filter_kwargs.items() if k in func_params})

    if "structlog.processors.EventRenamer" not in str(_processors):
        # find index of KeyValueRenderer/JSONRenderer/ConsoleRenderer and push EventRenamer to before either of them
        indices_for_insertion: list[int] = [
            _processors.index(processor)
            for processor in _processors
            if getattr(processor, "__name__", processor.__class__.__name__)
            in ("KeyValueRenderer", "JSONRenderer", "ConsoleRenderer")
        ]

        if len(indices_for_insertion) > 1:
            multiple_renderer_error_msg: str = f"""
            Multiple renderers found in the processors list returned by the `custom_processors_factory` function: {func.__name__}.
            Please ensure only one of KeyValueRenderer, JSONRenderer, or ConsoleRenderer is present in the processors list.
            """
            raise ValueError(multiple_renderer_error_msg)

        _processors.insert(
            min([*indices_for_insertion, len(_processors)]),
            structlog.processors.EventRenamer("message"),
        )

    return _processors


def _resolve_log_level(level: Optional[LogLevel] = None) -> int:
    """Resolve the log level from explicit parameter, environment variables, or default.

    Args:
        level: Explicit log level if provided.

    Returns:
        int: The resolved log level value.
    """
    if level is not None:
        return level.value
    env_log_level = os.getenv("LOG_LEVEL")
    if env_log_level:
        normalized_level = env_log_level.upper()
        resolved_level = LOG_LEVEL_NAMES_TO_LOG_LEVEL.get(normalized_level)  # type: ignore[call-overload]
        if resolved_level is not None:
            return int(resolved_level.value)
    if os.getenv("DEBUG", "false").lower() == "true":
        return logging.DEBUG
    return LogLevel.INFO.value


# ---------------------------------------------------------------------------
# Logger factory function
# ---------------------------------------------------------------------------


def get_logger(  # noqa: C901, PLR0912
    name: Optional[str] = None,
    level: Optional[LogLevel] = None,
    custom_processors_factory: Optional[Callable[..., List[structlog.types.Processor | Any]]] = None,
    disable_masking: Optional[bool] = None,
    handlers: Optional[List[LogHandler]] = None,
    file_name: Optional[str] = None,
    **kwargs: Any,
) -> PeakLogger:
    """Return an isolated logger instance that does NOT mutate global state.

    This function creates a logger isolated from other loggers in your application.
    It will NOT affect third-party libraries like boto3, urllib3, etc.

    The logger is configured with its own handlers attached to a named stdlib logger
    (not the root logger) and uses structlog.wrap_logger() for isolated structlog configuration.

    When `setup_loging()` has been called, this function respects the global configuration
    for defaults. Per-logger parameters override global settings.

    Args:
        name (Optional[str], optional): Name of the logger. Defaults to "peak" if not provided.
            Using a name ensures the logger is isolated from the root logger.
        level (LogLevel): Log level for this specific logger. Defaults to global config,
            then LogLevel.INFO or value from LOG_LEVEL/DEBUG environment variables.
        custom_processors_factory (Optional[Callable[..., List[structlog.types.Processor | Any]]], optional):
            A factory function that returns a list of custom processors.
            Defaults to None. This disables the default processors provided with the default implementation.
        disable_masking (Optional[bool], optional): Whether to disable masking of sensitive data.
            Defaults to global config value, then False.
            Only applicable when using the default processors.
        handlers (Optional[List[LogHandler]], optional): List of log handlers (CONSOLE, FILE).
            Defaults to CONSOLE. Pass an empty list [] to add no handlers (useful for library usage
            where you want the application to control output).
        file_name (Optional[str], optional): Filename for FILE handler. Required if FILE handler is used.
        **kwargs: Additional keyword arguments passed to custom_processors_factory.
            kwargs must be hashable else TypeError will be raised.

    Returns:
        PeakLogger: An isolated logger instance.

    Raises:
        ValueError: If the `file_name` is not provided for FILE handler or if `multiple renderers`
            are found in the `processor`(s) list returned by the `custom_processors_factory`.

    Example:
        >>> from peak.tools.logging import get_logger, LogLevel
        >>>
        >>> # Create an isolated logger - won't affect boto3 or other libraries
        >>> logger = get_logger("my_app", level=LogLevel.DEBUG)
        >>> logger.info("Hello, world!")
        >>>
        >>> # Create another logger with different settings
        >>> db_logger = get_logger("my_app.database", level=LogLevel.WARNING)
    """
    # Use a default name to ensure we don't configure the root logger
    logger_name = name if name is not None else "peak"

    # Resolve settings from global config with per-logger overrides
    _effective_disable_masking = disable_masking if disable_masking is not None else _global_config["disable_masking"]

    # Track if user provided explicit level
    _has_explicit_level = level is not None

    if level is not None:
        _log_level: int | None = level.value
        _explicit_level_loggers.add(logger_name)
    elif _global_config["configured"]:
        _log_level = _global_config["default_level"].value
    elif _global_config["legacy"]:
        _log_level = _resolve_log_level(None)
        _legacy_set_loggers.add(logger_name)
    else:
        _log_level = None

    _processors: list[structlog.types.Processor | Any] = (
        _handle_and_patch_processor_factory_kwargs(
            custom_processors_factory,
            disable_masking=_effective_disable_masking,
            **kwargs,
        )
        if custom_processors_factory is not None
        else default_processors_factory(
            disable_masking=_effective_disable_masking,
        )
    )

    # Get or create a NAMED stdlib logger (not root logger)
    stdlib_logger = logging.getLogger(logger_name)

    # Only configure if this logger hasn't been configured yet
    # Check if handlers already exist to avoid duplicate handlers
    if not stdlib_logger.handlers:
        # Set level (None means NOTSET - defer to parent, used in hierarchy mode)
        # When _log_level is None, we leave the logger at NOTSET which inherits from parent/root
        if _log_level is not None:
            stdlib_logger.setLevel(_log_level)

        # Add handlers to this specific logger
        if handlers is not None and len(handlers) == 0:
            # Empty list means no handlers (for library usage)
            # Add NullHandler to prevent "No handler found" warnings
            # This follows Python logging cookbook best practices
            stdlib_logger.addHandler(logging.NullHandler())
        else:
            if not handlers or LogHandler.CONSOLE in handlers:
                stdlib_logger.addHandler(logging.StreamHandler())
            if handlers and LogHandler.FILE in handlers:
                if file_name:
                    stdlib_logger.addHandler(logging.FileHandler(file_name))
                else:
                    msg = "filename must be provided for FILE handler."
                    raise ValueError(msg)
    elif level is not None:
        # Logger already configured, just update level if specified
        stdlib_logger.setLevel(level.value)
    elif _global_config["configured"]:
        stdlib_logger.setLevel(logging.NOTSET)

    wrapped_logger = structlog.wrap_logger(
        stdlib_logger,
        processors=_processors,
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        cache_logger_on_first_use=True,
    )

    return PeakLogger(wrapped_logger)


# ---------------------------------------------------------------------------
# Wrapper Logger class
# Basically delegate everything to `structlog`.
# ---------------------------------------------------------------------------


class PeakLogger:
    """Wrapper class for logging with various log levels."""

    # use __slots__ to avoid dynamic attribute creation
    __slots__: list[str] = ["_logger"]

    def __init__(self, logger: Any) -> None:
        """Initialize with a logger object.

        Args:
            logger (Any): Logger object to wrap.
        """
        self._logger: structlog.stdlib.BoundLogger = logger

    def __getattribute__(self, __name: str) -> Any:
        """Return the attribute from the wrapped logger object."""
        if __name in [*PeakLogger.__slots__, *PeakLogger.__dict__.keys()]:
            return object.__getattribute__(self, __name)
        return getattr(self._logger, __name)

    def bind(self, context: Union[dict[str, Any], None] = None, **kwargs: Any) -> None:
        """Bind contextual information to the logger, enriching log messages.

        This method allows attaching context data to the logger, such as additional information
        or system details, to provide more context in log messages.

        Args:
            context (Union[dict[str, Any], None]): A dictionary or None for contextual information.
            **kwargs: Additional key-value pairs to enhance context.
        """
        if context is None:
            context = {}

        if kwargs:
            # file deepcode ignore AttributeLoadOnNone: false positive
            context.update(kwargs)

        self._logger = self._logger.bind(**context)

    def unbind(self, keys: list[str]) -> None:
        """Unbind specified keys from the logger's context.

        Args:
            keys (list[str]): List of keys to unbind.
        """
        context: dict[str, Any] | dict[Any, Any] = structlog.get_context(self._logger)

        for key in keys:
            if key in context:
                del context[key]

        # Rebind the modified context to the logger
        self._logger = self._logger.bind(**context)

    def clone_with_context(self, context: Union[dict[str, Any], None] = None, **kwargs: Any) -> PeakLogger:
        """Return a frozen copy of this logger with the specified context added."""
        new_logger = PeakLogger(self._logger.new())
        new_logger.bind(context, **kwargs)
        return new_logger

    def set_log_level(self, level: LogLevel) -> None:
        """Set the log level of this logger.

        This only affects THIS logger, not other loggers in the application.

        Args:
            level (LogLevel): Log level to set.
        """
        if self._is_valid_log_level(level):
            # Get the underlying stdlib logger name and set level on it
            logger_name = getattr(self._logger, "name", None)
            if logger_name:
                logging.getLogger(logger_name).setLevel(level.value)

    def _is_valid_log_level(self, level: LogLevel) -> bool:
        """Check if a given log level is valid."""
        return level in LogLevel
