from __future__ import annotations

import logging
import os
import time
from typing import Any, Dict, Iterable, Optional, Sequence, TypedDict

try:
    from celery import current_app, current_task  # type: ignore
except Exception:  # pragma: no cover - Celery optional at import time
    current_app = None  # type: ignore
    current_task = None  # type: ignore

KANCHI_PROGRESS_EVENT = "kanchi-task-progress"
KANCHI_STEPS_EVENT = "kanchi-task-steps"

_VERBOSE = os.getenv("KANCHI_SDK_VERBOSE", "").lower() in {"1", "true", "yes", "on"}
_logger = logging.getLogger("kanchi_sdk")
if _VERBOSE and not logging.getLogger().handlers:
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )


class StepDef(TypedDict, total=False):
    """
    Declarative description for a step in a task.
    """

    key: str
    label: str
    description: str
    total: int
    order: int


def define_kanchi_steps(
    steps: Sequence[StepDef],
    *,
    task_id: Optional[str] = None,
    task_name: Optional[str] = None,
    dispatcher=None,
) -> None:
    """
    Emit a Celery event defining the logical steps of a task.
    """
    if not steps:
        _log_debug("kanchi: no steps provided, skipping dispatch")
        return

    task_id, task_name = _resolve_task_context(task_id, task_name)
    if not task_id or not task_name:
        _log_debug("kanchi: missing task context for steps (id=%s, name=%s)", task_id, task_name)
        return

    payload = {
        "task_id": task_id,
        "task_name": task_name,
        "steps": _normalize_steps(steps),
        "timestamp": time.time(),
    }

    _emit_event(KANCHI_STEPS_EVENT, payload, dispatcher=dispatcher)


def send_kanchi_progress(
    progress: float,
    *,
    step_key: Optional[str] = None,
    message: Optional[str] = None,
    meta: Optional[Dict[str, Any]] = None,
    task_id: Optional[str] = None,
    task_name: Optional[str] = None,
    dispatcher=None,
) -> None:
    """
    Emit a Celery event for progress updates.
    """
    task_id, task_name = _resolve_task_context(task_id, task_name)
    if not task_id or not task_name:
        _log_debug(
            "kanchi: missing task context for progress (id=%s, name=%s)", task_id, task_name
        )
        return

    payload = {
        "task_id": task_id,
        "task_name": task_name,
        "progress": _clamp_progress(progress),
        "timestamp": time.time(),
    }

    if step_key:
        payload["step_key"] = step_key
    if message:
        payload["message"] = message
    if meta:
        payload["meta"] = meta

    _emit_event(KANCHI_PROGRESS_EVENT, payload, dispatcher=dispatcher)


def _emit_event(event_type: str, payload: Dict[str, Any], dispatcher=None) -> None:
    """
    Emit a Celery event, swallowing errors to avoid breaking tasks.
    Prefer a caller-supplied dispatcher; otherwise create a short-lived dispatcher.
    """
    if dispatcher:
        try:
            dispatcher.send(event_type, **payload)
        except Exception as exc:
            _log_warning("kanchi: dispatcher send failed for %s: %s", event_type, exc)
        return

    if not current_app:
        _log_debug("kanchi: no current_app available, skipping %s", event_type)
        return

    try:
        with current_app.connection_for_write() as conn:  # type: ignore[attr-defined]
            disp = current_app.events.Dispatcher(conn)  # type: ignore[attr-defined]
            disp.send(event_type, **payload)
    except Exception as exc:
        _log_warning("kanchi: failed to emit %s: %s", event_type, exc)


def _resolve_task_context(
    task_id: Optional[str],
    task_name: Optional[str],
) -> tuple[Optional[str], Optional[str]]:
    """
    Try to infer task_id/task_name from Celery context when not provided.
    """
    if task_id and task_name:
        return task_id, task_name

    if current_task and getattr(current_task, "request", None):
        req = current_task.request  # type: ignore
        task_id = task_id or getattr(req, "id", None)
        task_name = task_name or getattr(req, "task", None) or getattr(req, "name", None)

    return task_id, task_name


def _normalize_steps(steps: Sequence[StepDef]) -> Iterable[StepDef]:
    normalized: list[StepDef] = []
    for step in steps:
        key = step.get("key")
        label = step.get("label")
        if not key or not label:
            _log_warning("kanchi: dropping step without key/label: %s", step)
            continue

        normalized.append(
            {
                "key": key,
                "label": label,
                **{k: v for k, v in step.items() if k not in {"key", "label"}},
            }
        )

    return normalized


def _clamp_progress(progress: float) -> float:
    try:
        value = float(progress)
    except Exception:
        _log_warning("kanchi: non-numeric progress %s; defaulting to 0", progress)
        return 0.0

    if value < 0:
        _log_warning("kanchi: progress <0 clamped to 0 (value=%s)", value)
        return 0.0
    if value > 100:
        _log_warning("kanchi: progress >100 clamped to 100 (value=%s)", value)
        return 100.0
    return value


def _log_debug(msg: str, *args: Any) -> None:
    if _VERBOSE:
        _logger.debug(msg, *args)


def _log_warning(msg: str, *args: Any) -> None:
    if _VERBOSE:
        _logger.warning(msg, *args)
