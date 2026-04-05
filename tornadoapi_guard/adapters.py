"""
Tornado adapters for guard-core.

Since Tornado is async, this adapter uses the async guard-core
(not guard_core.sync), matching FastAPI Guard's approach.

The adapter must implement the same interface as:
- FastAPI Guard:  guard/adapters.py (StarletteGuardRequest, StarletteGuardResponse)
- FlaskAPI Guard: flaskapi_guard/adapters.py (FlaskGuardRequest, FlaskGuardResponse)

Key Tornado concepts to map:
- RequestHandler is the main abstraction (not a separate request/response pair)
- RequestHandler.request -> HTTPServerRequest
- RequestHandler.prepare() is the async hook for pre-processing (security pipeline)
- RequestHandler.on_finish() is the post-processing hook (metrics, logging)
- No built-in response object — responses are written via handler.write()/handler.finish()
- request.remote_ip for client IP
- request.headers for headers (HTTPHeaders, case-insensitive)
- request.arguments for query params (returns bytes, needs decoding)
- request.body for raw body (bytes, already available — no await needed)
- request.protocol for scheme ("http" or "https")
- request.full_url() for complete URL

Required adapter classes:
- TornadoGuardRequest: wraps RequestHandler + HTTPServerRequest -> GuardRequest interface
- TornadoGuardResponse: standalone response container -> GuardResponse interface
- TornadoResponseFactory: creates TornadoGuardResponse instances
- apply_guard_response(): writes a guard response back through the handler

Per-request state (equivalent to request.state in Starlette / flask.g in Flask):
- Tornado has no built-in per-request state container
- Attach a _guard_state object to the handler instance
"""

# TODO: Implement adapters
