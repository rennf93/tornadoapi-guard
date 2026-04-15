---

title: Utilities API - TornadoAPI Guard
description: Helper functions and utilities for logging, security checks, and request handling in TornadoAPI Guard
keywords: security utilities, logging functions, security checks, request handling
---

Utilities
=========

The `utils` module provides various helper functions for security operations.

___

Logging Functions
-----------------

setup_custom_logging
---------------------

```python
def setup_custom_logging(
    log_file: str | None = None
) -> logging.Logger:
    """
    Setup custom logging for TornadoAPI Guard.
    
    Configures a hierarchical logger that outputs to both console and file.
    Console output is ALWAYS enabled for visibility.
    File output is optional for persistence.
    
    Args:
        log_file: Optional path to log file. If None, only console output is enabled.
                  If provided, creates the directory if it doesn't exist.
    
    Returns:
        logging.Logger: Configured logger with namespace "tornadoapi_guard"
    
    Note: This function is synchronous (not async).
    """
```

log_activity
------------

```python
async def log_activity(
    request: GuardRequest,
    logger: logging.Logger,
    log_type: str = "request",
    reason: str = "",
    passive_mode: bool = False,
    trigger_info: str = "",
    level: Literal["INFO", "DEBUG", "WARNING", "ERROR", "CRITICAL"] | None = "WARNING",
) -> None: ...
```

`GuardRequest` is the framework-agnostic request protocol from `guard_core`. In a Tornado handler, wrap the incoming request with `TornadoGuardRequest(self)` before passing it.

Parameters:

- `request`: A `GuardRequest` instance (wrap the Tornado handler with `TornadoGuardRequest(self)`)
- `logger`: The logger instance
- `log_type`: Type of log entry (default: "request", can also be "suspicious")
- `reason`: Reason for flagging an activity
- `passive_mode`: Whether to enable passive mode logging format
- `trigger_info`: Details about what triggered detection
- `level`: The logging level to use. If `None`, logging is disabled. Defaults to "WARNING".

This is a unified logging function that handles regular requests, suspicious activities, and passive mode logging.

___

Security Check Functions
------------------------

is_user_agent_allowed
---------------------

```python
async def is_user_agent_allowed(
    user_agent: str,
    config: SecurityConfig
) -> bool:
    """
    Check if user agent is allowed.
    """
```

check_ip_country
----------------

```python
async def check_ip_country(
    request: str | GuardRequest,
    config: SecurityConfig,
    geo_ip_handler: GeoIPHandler,
) -> bool: ...
```

is_ip_allowed
-------------

```python
async def is_ip_allowed(
    ip: str,
    config: SecurityConfig,
    ipinfo_db: IPInfoManager | None = None
) -> bool:
    """
    Check if IP address is allowed.
    """
```

The `ipinfo_db` parameter is now properly optional - it's only needed when country filtering is configured. If it's not provided when country filtering is configured, the function will work correctly but won't apply country filtering rules rules.

This function intelligently handles:

- Whitelist/blacklist checking
- Country filtering (only when IPInfoManager is provided)
- Cloud provider detection (only when cloud blocking is configured)

This selective processing aligns with TornadoAPI Guard's smart resource loading to optimize performance.

detect_penetration_attempt
--------------------------

```python
async def detect_penetration_attempt(
    request: GuardRequest,
) -> tuple[bool, str]
```

Detect potential penetration attempts in the request using the enhanced Detection Engine.

This function analyzes various parts of the request (query params, body, path, headers) using the Detection Engine's components including pattern matching, semantic analysis, and performance monitoring.

Parameters:

- `request`: A `GuardRequest` instance. In a Tornado handler, wrap the handler with `TornadoGuardRequest(self)` before calling.

Returns a tuple where:

- First element is a boolean: `True` if a potential attack is detected, `False` otherwise
- Second element is a string with details about what triggered the detection, or empty string if no attack detected

The Detection Engine provides:
- Timeout-protected pattern matching (configured via `detection_compiler_timeout` in SecurityConfig)
- Intelligent content preprocessing that preserves attack patterns
- Semantic analysis for obfuscated attacks (when enabled)
- Performance monitoring for pattern effectiveness

Example usage:

```python
from guard_core.utils import detect_penetration_attempt
from tornadoapi_guard import SecurityHandler
from tornadoapi_guard.adapters import TornadoGuardRequest


class SubmitHandler(SecurityHandler):
    async def post(self) -> None:
        guard_request = TornadoGuardRequest(self)
        is_suspicious, trigger_info = await detect_penetration_attempt(guard_request)
        if is_suspicious:
            logger.warning(f"Attack detected: {trigger_info}")
            self.write({"error": "Suspicious activity detected"})
            return
        self.write({"success": True})


class CriticalHandler(SecurityHandler):
    async def post(self) -> None:
        guard_request = TornadoGuardRequest(self)
        is_suspicious, trigger_info = await detect_penetration_attempt(guard_request)
        if is_suspicious:
            self.write({"error": "Security check failed"})
            return
        self.write({"success": True})
```

extract_client_ip
-----------------

```python
def extract_client_ip(
    request: GuardRequest,
    config: SecurityConfig,
    agent_handler: AgentHandlerProtocol | None = None,
) -> str: ...
```

This function provides a secure way to extract client IPs by:

1. Only trusting X-Forwarded-For headers from configured trusted proxies
2. Using the connecting IP when not from a trusted proxy
3. Properly handling proxy chains based on configured depth

___

Usage Examples
--------------

```python
from guard_core.utils import (
    setup_custom_logging,
    log_activity,
    detect_penetration_attempt
)

# Setup logging (synchronous function)
# Console only
logger = setup_custom_logging()  # or setup_custom_logging(None)

# Console + file
logger = setup_custom_logging("security.log")

# Log regular request
await log_activity(request, logger)

# Log suspicious activity
await log_activity(
    request,
    logger,
    log_type="suspicious",
    reason="Suspicious pattern detected"
)

# Check for penetration attempts
is_suspicious, trigger_info = await detect_penetration_attempt(request)
```
