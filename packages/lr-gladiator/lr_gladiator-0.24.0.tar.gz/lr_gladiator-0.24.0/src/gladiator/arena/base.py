from __future__ import annotations

import os
from typing import Optional

import requests

from ..config import LoginConfig


class ArenaError(RuntimeError):
    """Domain-specific error raised for Arena client operations."""


class BaseArenaClient:
    """Base class that configures the HTTP session and shared helpers."""

    def __init__(
        self,
        cfg: LoginConfig,
        *,
        session: Optional[requests.Session] = None,
    ) -> None:
        self.cfg = cfg
        self.session = session or requests.Session()
        self.session.verify = cfg.verify_tls
        self._apply_default_headers()
        self._debug = bool(int(os.environ.get("GLADIATOR_DEBUG", "0")))

    def _apply_default_headers(self) -> None:
        defaults = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "User-Agent": "gladiator-arena/0.1",
            "Arena-Usage-Reason": self.cfg.reason or "gladiator/cli",
        }
        for key, value in defaults.items():
            self.session.headers[key] = value
        if self.cfg.arena_session_id:
            self.session.headers["arena_session_id"] = self.cfg.arena_session_id

    def _api_base(self) -> str:
        return self.cfg.base_url.rstrip("/")

    def _log(self, msg: str) -> None:
        if self._debug:
            print(f"[gladiator debug] {msg}")

    def _ensure_json(self, resp: requests.Response):
        ctype = resp.headers.get("Content-Type", "").lower()
        if "application/json" not in ctype:
            snippet = resp.text[:400].replace("", " ")
            raise ArenaError(
                f"Expected JSON but got '{ctype or 'unknown'}' from {resp.url}. "
                f"Status {resp.status_code}. Body starts with: {snippet}"
            )
        try:
            return resp.json()
        except Exception as exc:  # pragma: no cover - defensive catch
            raise ArenaError(f"Failed to parse JSON from {resp.url}: {exc}") from exc

    def _try_json(self, resp: requests.Response) -> Optional[dict]:
        """Best-effort JSON parse. Returns None if not JSON or parse fails."""
        ctype = resp.headers.get("Content-Type", "").lower()
        if "application/json" not in ctype:
            return None
        try:
            data = resp.json()
            return data if isinstance(data, dict) else {"data": data}
        except Exception:
            return None


__all__ = ["ArenaError", "BaseArenaClient"]
