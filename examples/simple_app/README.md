TornadoAPI Guard Example App
============================

This example demonstrates how to use TornadoAPI Guard inside a Tornado application.

___

Running the example
-------------------

Using Docker Compose
--------------------

```bash
# Start the example app and Redis
docker compose up

# Restart
docker compose restart

# Stop
docker compose down
```

Running locally (no Docker)
---------------------------

```bash
cd examples/simple_app
pip install -r requirements.txt
python main.py
```

The app listens on `http://127.0.0.1:8000` by default. Override host/port with the
`HOST` and `PORT` environment variables.

___

Available endpoints
-------------------

- `/` — API overview with feature list and route map
- `/basic/` — Basic endpoint (subject to global rate limit)
- `/basic/ip` — Return client IP information
- `/basic/health` — Health check (excluded from all security checks)
- `/basic/echo` — Echo POST body with headers and method
- `/access/ip-whitelist` — Require whitelisted client IP
- `/access/ip-blacklist` — Reject blacklisted client IP
- `/access/country-block` — Block requests from specific countries
- `/access/country-allow` — Allow only specific countries
- `/access/no-cloud` — Block all known cloud provider IPs
- `/access/no-aws` — Block AWS IPs only
- `/access/bypass-demo` — Bypass rate limit + geo check for this route
- `/auth/https-only` — Require HTTPS
- `/auth/bearer-auth` — Require Bearer token in Authorization header
- `/auth/api-key` — Require `X-API-Key` header
- `/auth/custom-headers` — Require arbitrary custom headers
- `/rate/custom-limit` — 5 requests per 60 seconds
- `/rate/strict-limit` — 1 request per 10 seconds
- `/rate/geo-rate-limit` — Per-country rate limits
- `/behavior/usage-monitor` — Log when >10 calls in 5 minutes
- `/behavior/return-monitor/{status_code}` — Ban IP after 3 HTTP 404s within 60s
- `/behavior/suspicious-frequency` — Throttle high-frequency requests
- `/behavior/behavior-rules` (POST) — Combined frequency + return pattern rules
- `/headers/` — Security headers overview
- `/headers/test-page` — HTML page demonstrating CSP
- `/headers/csp-report` (POST) — CSP violation report receiver
- `/headers/frame-test` — X-Frame-Options demonstration
- `/headers/hsts-info` — HSTS configuration info
- `/headers/security-analysis` — Per-request security analysis
- `/content/no-bots` — Block common bot user agents
- `/content/json-only` (POST) — Require `Content-Type: application/json`
- `/content/size-limit` (POST) — Limit request body to 100 KB
- `/content/referrer-check` — Require allowed `Referer` header
- `/content/custom-validation` — Reject a custom user-agent pattern
- `/advanced/business-hours` — Access only during 09:00–17:00 UTC
- `/advanced/weekend-only` — Demonstrates `time_window` decorator
- `/advanced/honeypot` (POST) — Honeypot bot detection
- `/advanced/suspicious-patterns` — Enhanced suspicious pattern detection
- `/admin/unban-ip` (POST) — Admin: unban an IP (localhost only)
- `/admin/stats` — Admin: security statistics (localhost only)
- `/admin/clear-cache` (POST) — Admin: clear security caches (localhost only)
- `/admin/emergency-mode` (PUT) — Admin: toggle emergency mode (localhost only)
- `/admin/cloud-status` — Admin: cloud provider refresh status (localhost only)
- `/test/xss-test` (POST) — XSS detection test
- `/test/sql-injection` — SQL injection detection test
- `/test/path-traversal/{path}` — Path traversal detection test
- `/test/command-injection` (POST) — Command injection detection test
- `/test/mixed-attack` (POST) — Combined attack vectors
- `/ws` — WebSocket echo endpoint

___

Note on `/docs`
---------------

Tornado does not auto-generate an OpenAPI UI. Unlike `fastapi-guard`, there is no
`/docs` page in this example. Use the `/` endpoint for the route map, and refer to the
MkDocs tutorial under `docs/tutorial/examples/example-app.md` for a walkthrough of
each feature.

___

Environment variables
---------------------

- `REDIS_URL` — Redis connection string (default `redis://localhost:6379`)
- `REDIS_PREFIX` — Key prefix for Redis entries (default `tornadoapi_guard:`)
- `IPINFO_TOKEN` — Token for IPInfo geolocation (optional)
- `HOST` — Host interface to bind (default `127.0.0.1`)
- `PORT` — Listen port (default `8000`)
