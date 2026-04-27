import pytest
from guard_core.core.events.composite_handler import CompositeAgentHandler
from guard_core.models import SecurityConfig

from tornadoapi_guard import SecurityMiddleware


@pytest.mark.asyncio
async def test_event_bus_routes_through_composite_when_otel_enabled() -> None:
    config = SecurityConfig(
        enable_otel=True, otel_service_name="wire-test", enable_redis=False
    )
    mw = SecurityMiddleware(config=config)

    await mw.initialize()

    assert isinstance(mw.event_bus.agent_handler, CompositeAgentHandler)
    assert isinstance(mw.metrics_collector.agent_handler, CompositeAgentHandler)
    await mw.reset()


@pytest.mark.asyncio
async def test_event_bus_routes_through_composite_when_logfire_enabled() -> None:
    config = SecurityConfig(
        enable_logfire=True, logfire_service_name="wire-test", enable_redis=False
    )
    mw = SecurityMiddleware(config=config)

    await mw.initialize()

    assert isinstance(mw.event_bus.agent_handler, CompositeAgentHandler)
    assert isinstance(mw.metrics_collector.agent_handler, CompositeAgentHandler)
    await mw.reset()


@pytest.mark.asyncio
async def test_event_bus_stays_bare_when_no_telemetry_configured() -> None:
    config = SecurityConfig(enable_redis=False)
    mw = SecurityMiddleware(config=config)

    await mw.initialize()

    assert not isinstance(mw.event_bus.agent_handler, CompositeAgentHandler)
    assert not isinstance(mw.metrics_collector.agent_handler, CompositeAgentHandler)
    await mw.reset()


@pytest.mark.asyncio
async def test_contexts_use_the_post_initialize_event_bus() -> None:
    config = SecurityConfig(
        enable_otel=True, otel_service_name="wire-test", enable_redis=False
    )
    mw = SecurityMiddleware(config=config)

    await mw.initialize()

    assert mw.validator.context.event_bus is mw.event_bus
    assert mw.behavioral_processor.context.event_bus is mw.event_bus
    assert mw.response_factory.context.metrics_collector is mw.metrics_collector
    await mw.reset()
