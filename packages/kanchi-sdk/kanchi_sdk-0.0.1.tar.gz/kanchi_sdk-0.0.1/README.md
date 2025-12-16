# Kanchi SDK

Lightweight helper library for emitting Kanchi-compatible Celery events. It provides a small set of helpers to declare task steps and to emit progress updates without coupling your code to Kanchi internals. Celery is a required dependency.

> **Status:** Alpha. Interfaces may change; expect minor breaking tweaks as we iterate.

## Installation

```bash
pip install kanchi-sdk
```

## Quickstart

Send progress/step events from any Celery task:

```python
from kanchi_sdk import KanchiTaskMixin, StepDef
from celery import Celery

app = Celery("example")

class ProcessFileTask(KanchiTaskMixin, app.Task):
    name = "process_file"

    def run(self, file_id: str) -> None:
        steps: list[StepDef] = [
            {"key": "download", "label": "Download file"},
            {"key": "process", "label": "Process file"},
        ]
        self.define_kanchi_steps(steps)

        self.send_kanchi_progress(0, step_key="download", message="Starting download")
        # ... download the file ...
        self.send_kanchi_progress(50, step_key="process", message="Processing")
        # ... process ...
        self.send_kanchi_progress(100, message="Done")
```

Helpers are safe to call even when Celery is not present. Set `KANCHI_SDK_VERBOSE=1` to log debug/warning messages during local development.

## Local development

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
ruff check .
pytest
```

## Why this exists

- Make Kanchi task instrumentation trivial and framework-friendly
- Provide typed, documented helpers with sensible defaults

## License

MIT © Bernhard Hauke
