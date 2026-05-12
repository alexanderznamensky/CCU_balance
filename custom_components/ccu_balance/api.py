"""API client for CCU Balance."""

from __future__ import annotations

import asyncio
import json
import math
from typing import Any

from aiohttp import BasicAuth, ClientError, ClientSession

from .const import CMD, HEADERS, URL


class CcuBalanceApiClient:
    """Small async API client for ccu.su."""

    def __init__(self, session: ClientSession, login: str, password: str) -> None:
        self._session = session
        self._login = login
        self._password = password

    async def async_get_balance(self) -> dict[str, Any]:
        """Fetch balance and return normalized result.

        To match the original script behavior, any invalid response becomes
        balance 0.0 instead of raising an exception.
        """
        payload = json.dumps(CMD, separators=(",", ":"))

        try:
            async with asyncio.timeout(20):
                response = await self._session.post(
                    URL,
                    auth=BasicAuth(self._login, self._password),
                    headers=HEADERS,
                    data=payload,
                )

                if response.status != 200:
                    return {
                        "balance": 0.0,
                        "ok": False,
                        "status": f"http_{response.status}",
                        "raw_balance": None,
                    }

                try:
                    data = await response.json(content_type=None)
                except Exception:
                    return {
                        "balance": 0.0,
                        "ok": False,
                        "status": "invalid_json",
                        "raw_balance": None,
                    }

        except TimeoutError:
            return {"balance": 0.0, "ok": False, "status": "timeout", "raw_balance": None}
        except (ClientError, OSError):
            return {"balance": 0.0, "ok": False, "status": "connection_error", "raw_balance": None}
        except Exception as err:  # defensive: state should stay numeric
            return {"balance": 0.0, "ok": False, "status": f"error: {err.__class__.__name__}", "raw_balance": None}

        raw_balance = data.get("Balance") if isinstance(data, dict) else None

        if raw_balance in (None, "", "NotValid"):
            return {
                "balance": 0.0,
                "ok": False,
                "status": "not_valid",
                "raw_balance": raw_balance,
            }

        try:
            value = abs(float(raw_balance))
        except (TypeError, ValueError):
            return {
                "balance": 0.0,
                "ok": False,
                "status": "invalid_balance",
                "raw_balance": raw_balance,
            }

        if not math.isfinite(value):
            return {
                "balance": 0.0,
                "ok": False,
                "status": "invalid_balance",
                "raw_balance": raw_balance,
            }

        return {
            "balance": round(value, 2),
            "ok": True,
            "status": "ok",
            "raw_balance": raw_balance,
        }
