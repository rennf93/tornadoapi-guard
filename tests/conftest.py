from __future__ import annotations

import os
from collections.abc import AsyncGenerator

import pytest
from guard_core.handlers.cloud_handler import cloud_handler
from guard_core.handlers.ipban_handler import reset_global_state
from guard_core.handlers.ipinfo_handler import IPInfoManager
from guard_core.handlers.ratelimit_handler import (
    RateLimitManager,
    rate_limit_handler,
)
from guard_core.handlers.redis_handler import RedisManager
from guard_core.handlers.security_headers_handler import security_headers_manager
from guard_core.handlers.suspatterns_handler import sus_patterns_handler
from guard_core.models import SecurityConfig

from tornadoapi_guard import SecurityMiddleware

IPINFO_TOKEN = os.getenv("IPINFO_TOKEN", "")
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
REDIS_PREFIX = os.getenv("REDIS_PREFIX", "tornadoapi_guard_test")


def _maybe_geo_ip() -> IPInfoManager | None:
    if not IPINFO_TOKEN:
        return None
    return IPInfoManager(IPINFO_TOKEN, None)


@pytest.fixture(autouse=True)
async def reset_state() -> AsyncGenerator[None, None]:
    await reset_global_state()
    await security_headers_manager.reset()
    original_patterns = sus_patterns_handler.patterns.copy()

    cloud_instance = cloud_handler._instance
    if cloud_instance:
        cloud_instance.ip_ranges = {"AWS": set(), "GCP": set(), "Azure": set()}
        cloud_instance.redis_handler = None

    if IPInfoManager._instance:
        if IPInfoManager._instance.reader:
            IPInfoManager._instance.reader.close()
        IPInfoManager._instance = None

    RateLimitManager._instance = None

    yield
    sus_patterns_handler.patterns = original_patterns.copy()


@pytest.fixture(autouse=True)
async def reset_rate_limiter() -> None:
    config = SecurityConfig(geo_ip_handler=_maybe_geo_ip(), enable_redis=False)
    limiter = rate_limit_handler(config)
    await limiter.reset()


@pytest.fixture
def security_config() -> SecurityConfig:
    return SecurityConfig(
        geo_ip_handler=_maybe_geo_ip(),
        enable_redis=False,
        enable_penetration_detection=False,
        whitelist=["127.0.0.1"],
        blacklist=["192.168.1.1"],
        blocked_user_agents=[r"badbot"],
        auto_ban_threshold=3,
        auto_ban_duration=300,
        custom_error_responses={
            403: "Custom Forbidden",
            429: "Custom Too Many Requests",
        },
    )


@pytest.fixture
async def security_middleware(
    security_config: SecurityConfig,
) -> AsyncGenerator[SecurityMiddleware, None]:
    middleware = SecurityMiddleware(config=security_config)
    await middleware.initialize()
    yield middleware
    await middleware.reset()


@pytest.fixture
async def redis_cleanup() -> AsyncGenerator[None, None]:
    config = SecurityConfig(
        geo_ip_handler=_maybe_geo_ip(),
        redis_url=REDIS_URL,
        redis_prefix=REDIS_PREFIX,
    )
    handler = RedisManager(config)
    try:
        await handler.initialize()
        await handler.delete_pattern(f"{REDIS_PREFIX}*")
    except Exception:
        pass
    yield
    try:
        await handler.close()
    except Exception:
        pass
