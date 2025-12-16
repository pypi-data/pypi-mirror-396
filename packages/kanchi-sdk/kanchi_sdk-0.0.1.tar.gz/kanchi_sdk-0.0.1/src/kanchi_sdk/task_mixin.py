from __future__ import annotations

import contextlib
from typing import Optional, Sequence

try:
    from celery import Task  # type: ignore
except Exception:  # pragma: no cover - Celery optional at import time
    Task = object  # type: ignore

from .progress import (
    StepDef,
    define_kanchi_steps as _define_kanchi_steps,
    send_kanchi_progress as _send_kanchi_progress,
)


class KanchiTaskMixin(Task):
    """
    Celery Task mixin that exposes typed helpers for Kanchi progress/steps.
    """

    abstract = True

    def __init__(self):
        super().__init__()
        self._kanchi_dispatcher = None
        self._kanchi_dispatcher_conn = None

    def _dispatcher(self):
        if self._kanchi_dispatcher:
            return self._kanchi_dispatcher

        with contextlib.suppress(Exception):
            conn = self.app.connection_for_write()  # type: ignore[attr-defined]
            self._kanchi_dispatcher_conn = conn
            self._kanchi_dispatcher = self.app.events.Dispatcher(conn)  # type: ignore[attr-defined]
        return self._kanchi_dispatcher

    def _reset_dispatcher(self):
        with contextlib.suppress(Exception):
            if self._kanchi_dispatcher_conn:
                self._kanchi_dispatcher_conn.release()  # type: ignore[attr-defined]
        self._kanchi_dispatcher = None
        self._kanchi_dispatcher_conn = None

    def __del__(self):
        self._reset_dispatcher()
        with contextlib.suppress(Exception):
            super().__del__()  # type: ignore[misc]

    def define_kanchi_steps(self, steps: Sequence[StepDef]) -> None:
        _define_kanchi_steps(
            steps,
            task_id=self.request.id,  # type: ignore[attr-defined]
            task_name=self.name,  # type: ignore[attr-defined]
            dispatcher=self._dispatcher(),
        )

    def send_kanchi_progress(
        self,
        progress: float,
        *,
        step_key: Optional[str] = None,
        message: Optional[str] = None,
        meta: Optional[dict] = None,
    ) -> None:
        """
        Dispatch a Kanchi progress event from within a Celery task.
        """
        try:
            _send_kanchi_progress(
                progress,
                step_key=step_key,
                message=message,
                meta=meta,
                task_id=self.request.id,  # type: ignore[attr-defined]
                task_name=self.name,  # type: ignore[attr-defined]
                dispatcher=self._dispatcher(),
            )
        finally:
            # If dispatcher connection was closed externally, allow recreation next call.
            if self._kanchi_dispatcher and getattr(self._kanchi_dispatcher, "connection", None):
                if getattr(self._kanchi_dispatcher.connection, "closed", False):  # type: ignore[attr-defined]
                    self._reset_dispatcher()
