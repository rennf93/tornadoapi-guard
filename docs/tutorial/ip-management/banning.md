---

title: IP Banning - TornadoAPI Guard
description: Implement automatic and manual IP banning in Tornado applications using TornadoAPI Guard's IPBanManager
keywords: ip banning, ip blocking, security middleware, tornado security
---

IP Banning
==========

TornadoAPI Guard provides powerful IP banning capabilities through the `IPBanManager`.

___

Automatic IP Banning
---------------------

Configure automatic IP banning based on suspicious activity:

```python
config = SecurityConfig(
    auto_ban_threshold=5,  # Ban after 5 suspicious requests
    auto_ban_duration=3600,  # Ban duration in seconds (1 hour)
)
```

___

Manual IP Banning
------------------

You can also manually ban IPs using the `IPBanManager`:

```python
from tornadoapi_guard import SecurityHandler, ip_ban_manager


class BanIPHandler(SecurityHandler):
    async def post(self, ip: str) -> None:
        duration = int(self.get_argument("duration", "3600"))
        await ip_ban_manager.ban_ip(ip, duration)
        self.write({"message": f"IP {ip} banned for {duration} seconds"})
```

Register as `(r"/admin/ban/([^/]+)", BanIPHandler)` in your `tornado.web.Application`.

___

Checking Ban Status
-------------------

Check if an IP is currently banned:

```python
class CheckBanHandler(SecurityHandler):
    async def get(self, ip: str) -> None:
        is_banned = await ip_ban_manager.is_ip_banned(ip)
        self.write({"ip": ip, "banned": is_banned})
```

Register as `(r"/admin/check/([^/]+)", CheckBanHandler)` in your `tornado.web.Application`.

___

Reset All Bans
--------------

Clear all active IP bans:

```python
class ResetBansHandler(SecurityHandler):
    async def post(self) -> None:
        await ip_ban_manager.reset()
        self.write({"message": "All IP bans cleared"})
```

Register as `(r"/admin/reset", ResetBansHandler)` in your `tornado.web.Application`.
