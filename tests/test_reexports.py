from __future__ import annotations

import tornadoapi_guard


def test_all_symbols_present() -> None:
    for name in tornadoapi_guard.__all__:
        assert hasattr(tornadoapi_guard, name), f"Missing export: {name}"


def test_core_types_importable() -> None:
    from tornadoapi_guard import (
        BehaviorRule,
        BehaviorTracker,
        GuardRequest,
        GuardResponse,
        GuardResponseFactory,
        IPBanManager,
        RateLimitManager,
        RedisManager,
        RouteConfig,
        SecurityConfig,
        SecurityDecorator,
        SecurityHandler,
        SecurityHeadersManager,
        SecurityMiddleware,
        TornadoGuardRequest,
        TornadoGuardResponse,
        TornadoResponseFactory,
        apply_guard_response,
        unwrap_response,
    )

    assert SecurityConfig is not None
    assert SecurityMiddleware is not None
    assert SecurityHandler is not None
    assert TornadoGuardRequest is not None
    assert TornadoGuardResponse is not None
    assert TornadoResponseFactory is not None
    assert apply_guard_response is not None
    assert unwrap_response is not None
    assert SecurityDecorator is not None
    assert RouteConfig is not None
    assert BehaviorRule is not None
    assert BehaviorTracker is not None
    assert IPBanManager is not None
    assert RateLimitManager is not None
    assert RedisManager is not None
    assert SecurityHeadersManager is not None
    assert GuardRequest is not None
    assert GuardResponse is not None
    assert GuardResponseFactory is not None
