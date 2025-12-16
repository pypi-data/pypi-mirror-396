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
"""Logger for the Peak SDK."""
from __future__ import annotations

import logging
import sys
from typing import Any, List

from peak.constants import LOG_FORMAT, LOG_LEVELS

_logger: logging.Logger = logging.getLogger("peak-sdk")

# Add NullHandler to prevent "No handler found" warnings.
# This follows Python library best practices.
# See: https://docs.python.org/3/howto/logging-cookbook.html#adding-handlers-other-than-nullhandler-to-a-logger-in-a-library
_logger.addHandler(logging.NullHandler())

_handler_configured: bool = False


def _ensure_handler() -> None:
    """Lazily configure a StreamHandler if no logging has been set up.

    This provides backward compatibility for users who don't configure logging,
    while respecting application logging configuration when present.

    Called on first log operation to check if user has configured logging
    after importing the SDK.
    """
    global _handler_configured  # noqa: PLW0603
    if _handler_configured:
        return

    _handler_configured = True

    # If user has configured logging (root has handlers or level changed), respect their config
    if logging.root.handlers or logging.root.level != logging.WARNING:
        _logger.propagate = True
        return

    # No logging configured - add handler for backward compatibility
    stream_handler = logging.StreamHandler(sys.stdout)  # pragma: no cover
    stream_handler.setFormatter(LOG_FORMAT)  # pragma: no cover
    _logger.addHandler(stream_handler)  # pragma: no cover
    _logger.propagate = False  # pragma: no cover


class _LazyLogger:
    """Wrapper that ensures handler is configured on first use.

    This allows users to configure logging after importing the SDK:

        from peak import Session  # Import first
        import logging
        logging.basicConfig(level=logging.DEBUG)  # Configure later
        # SDK will now use user's config instead of adding its own handler
    """

    def __getattr__(self, name: str) -> Any:
        _ensure_handler()
        return getattr(_logger, name)


# Export lazy wrapper - configures handler on first actual log call
logger: _LazyLogger = _LazyLogger()


def set_log_level(log_level: LOG_LEVELS) -> None:
    """Update log level for Peak SDK logger.

    Args:
        log_level (LOG_LEVELS): new logging level for the logger.

    Note:
        If logging has been configured by the application (e.g., via
        logging.basicConfig()), you may also need to configure handlers
        on the root logger or 'peak-sdk' logger to see output.
    """
    _ensure_handler()
    _logger.setLevel(log_level)
    for handler in _logger.handlers:
        handler.setLevel(log_level)


__all__: List[str] = ["logger", "set_log_level"]
