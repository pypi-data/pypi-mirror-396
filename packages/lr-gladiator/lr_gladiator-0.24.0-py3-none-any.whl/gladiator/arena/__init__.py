from __future__ import annotations

from typing import Optional

import requests

from ..config import LoginConfig
from .base import ArenaError, BaseArenaClient
from .changes import ChangeClient
from .items import ItemClient


class ArenaClient(ItemClient):
    """Backwards-compatible client focused on item/file workflows."""

    def __init__(
        self,
        cfg: LoginConfig,
        *,
        session: Optional[requests.Session] = None,
    ) -> None:
        super().__init__(cfg, session=session)


class ArenaService:
    """Aggregates multiple domain clients (items, changes, …) on a shared session."""

    def __init__(
        self,
        cfg: LoginConfig,
        *,
        session: Optional[requests.Session] = None,
    ) -> None:
        shared_session = session or requests.Session()
        self._base = BaseArenaClient(cfg, session=shared_session)
        self.items = ItemClient(cfg, session=self._base.session)
        self.changes = ChangeClient(cfg, session=self._base.session)

    @property
    def session(self) -> requests.Session:
        return self._base.session


__all__ = [
    "ArenaClient",
    "ArenaService",
    "ArenaError",
    "ItemClient",
    "ChangeClient",
]
