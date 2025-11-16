from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Callable

from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import aiohttp_client, event
from homeassistant.util.dt import utcnow
from homeassistant.components.camera import async_get_image

from .const import (
    CONF_CAMERA_ENTITY,
    CONF_MODE,
    CONF_RUNS_PER_DAY,
    CONF_PROVIDER,
    CONF_MODEL,
    CONF_API_KEY,
    CONF_BASE_URL,
    MODE_AUTO,
)
from .llm_client import LLMClient, LLMClientError


@dataclass
class CleanMeState:
    status: str = "unknown"  # clean | messy | error | unknown
    tasks: List[Dict[str, Any]] = field(default_factory=list)
    comment: str | None = None
    last_error: str | None = None
    last_checked: datetime | None = None

    @property
    def needs_tidy(self) -> bool:
        return self.status == "messy" and bool(self.tasks)


class CleanMeZone:
    """One tidy zone (room/area)."""

    def __init__(self, hass: HomeAssistant, entry_id: str, name: str, data: Dict[str, Any]) -> None:
        self.hass = hass
        self.entry_id = entry_id
        self._name = name

        self._camera_entity_id: str = data[CONF_CAMERA_ENTITY]
        self._mode: str = data.get(CONF_MODE, MODE_AUTO)
        self._runs_per_day: int = int(data.get(CONF_RUNS_PER_DAY, 1))
        if self._runs_per_day < 1:
            self._runs_per_day = 1

        provider = data[CONF_PROVIDER]
        model = data.get(CONF_MODEL) or ""
        api_key = data.get(CONF_API_KEY) or ""
        base_url = data.get(CONF_BASE_URL) or ""

        self._llm_client = LLMClient(provider, api_key, model, base_url)

        self._state = CleanMeState()
        self._listeners: list[Callable[[], None]] = []
        self._unsub_timer: Optional[Callable[[], None]] = None
        self._snooze_until: Optional[datetime] = None

    @property
    def name(self) -> str:
        return self._name

    @property
    def camera_entity_id(self) -> str:
        return self._camera_entity_id

    @property
    def state(self) -> CleanMeState:
        return self._state

    @property
    def needs_tidy(self) -> bool:
        return self._state.needs_tidy

    async def async_setup(self) -> None:
        """Set up timers if in auto mode."""
        if self._mode == MODE_AUTO:
            self._setup_auto_timer()

    @callback
    def _setup_auto_timer(self) -> None:
        """Set up periodic checks based on runs/day."""
        if self._unsub_timer:
            self._unsub_timer()

        interval_hours = 24 / float(self._runs_per_day)
        interval = timedelta(hours=interval_hours)

        async def _handle(now) -> None:
            await self.async_request_check(reason="auto")

        self._unsub_timer = event.async_track_time_interval(
            self.hass, _handle, interval
        )

    async def async_unload(self) -> None:
        """Clean up on unload."""
        if self._unsub_timer:
            self._unsub_timer()
            self._unsub_timer = None
        self._listeners.clear()

    @callback
    def add_listener(self, listener: Callable[[], None]) -> None:
        """Register an entity listener."""
        self._listeners.append(listener)

    @callback
    def _notify_listeners(self) -> None:
        for listener in list(self._listeners):
            try:
                listener()
            except Exception:
                continue

    async def async_snooze(self, minutes: int) -> None:
        """Snooze auto checks for some minutes."""
        self._snooze_until = utcnow() + timedelta(minutes=minutes)

    async def async_clear_tasks(self) -> None:
        """Clear tasks and mark as clean."""
        self._state.tasks = []
        self._state.status = "clean"
        self._state.comment = "Tasks cleared manually."
        self._state.last_error = None
        self._state.last_checked = utcnow()
        self._notify_listeners()

    async def async_request_check(self, reason: str = "manual") -> None:
        """Run a check now (may be called by service or timer)."""
        now = utcnow()
        if reason == "auto" and self._snooze_until and now < self._snooze_until:
            return

        try:
            image = await async_get_image(self.hass, self._camera_entity_id)
            image_bytes = image.content
        except Exception as err:
            self._state.last_error = f"Failed to capture camera image: {err}"
            self._state.status = "error"
            self._state.last_checked = now
            self._notify_listeners()
            return

        session = aiohttp_client.async_get_clientsession(self.hass)

        try:
            result = await self._llm_client.analyze_image(
                session=session,
                image_bytes=image_bytes,
                room_name=self._name,
            )
        except LLMClientError as err:
            self._state.last_error = str(err)
            self._state.status = "error"
            self._state.last_checked = now
            self._notify_listeners()
            return
        except Exception as err:
            self._state.last_error = f"Unexpected LLM error: {err}"
            self._state.status = "error"
            self._state.last_checked = now
            self._notify_listeners()
            return

        self._state.status = result.get("status", "unknown")
        self._state.tasks = result.get("tasks", [])
        self._state.comment = result.get("comment", "")
        self._state.last_error = None
        self._state.last_checked = now

        self._notify_listeners()
