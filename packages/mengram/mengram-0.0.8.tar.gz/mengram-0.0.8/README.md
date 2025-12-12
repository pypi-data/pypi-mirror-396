# mengram

Local FastAPI service that stores, recalls, and manages lightweight "memories" with hybrid lexical/vector search.

## Quickstart

Install from your local wheel (or PyPI/TestPyPI once published) and initialize the schema once per database:

```bash
pip install mengram
```

```python
from mengram import MemoryClient, init_memory_os_schema

init_memory_os_schema()
client = MemoryClient()

memory = client.remember(
    content="Talked to Alice about refund policy.",
    type="episodic",
    scope="session",
    entity_id="sess-123",
    tags=["support", "refund"],
)

results = client.recall(query="refund policy", scope="session", entity_id="sess-123")

rule = client.create_rule(
    condition={
        "event_type": "tool:error",
        "tool_name": "node_forecast",
        "window_minutes": 10,
        "threshold_count": 3,
    },
    actions={
        "actions": [
            {
                "type": "notify",
                "channel": "stdout",
                "target": "#ops",
                "message": "node_forecast failed 3 times in 10 minutes.",
            },
            {
                "type": "inject_memory",
                "content": "node_forecast is unstable, consider fallback model.",
            },
        ]
    },
)

event_result = client.record_event(
    event_type="tool:error",
    tool_name="node_forecast",
    scope="session",
    entity_id="sess-123",
    payload={"error_code": "TIMEOUT"},
)
```

## Getting Started

1. Install dependencies (ideally inside a virtualenv):

```bash
pip install -r requirements.txt
# or, when installing from a wheel/TestPyPI build:
# pip install 'mengram[server]' --extra-index-url https://pypi.org/simple
```

2. Run the API with Uvicorn:

```bash
uvicorn app.main:app --reload
```

The service exposes:

- `GET /healthz` – health probe
- `POST /v0/remember` – store a memory with optional TTL and tags
- `GET /v0/recall` – hybrid recall with vector + lexical scoring
- `POST /v0/reflect` – naive episodic → semantic session summary
- `POST /v0/plan` – stores prospective-memory rules
- `POST /v0/forget` – delete by id or policy
- `POST /v0/event` – store incoming events and synchronously fire rule actions

SQLite (`memory.db`) is created automatically in the project root on startup.

### Prospective memory rules (V0)

Rules capture the simple pattern → action contracts that `/v0/event` enforces:

```jsonc
POST /v0/plan
{
  "if": {
    "event_type": "tool:error",
    "tool_name": "node_forecast",
    "window_minutes": 10,
    "threshold_count": 3
  },
  "then": {
    "actions": [
      {
        "type": "notify",
        "channel": "slack",
        "target": "#ops",
        "message": "node_forecast is erroring frequently"
      },
      {
        "type": "inject_memory",
        "content": "Last 10 minutes: node_forecast erroring > 3 times."
      }
    ]
  }
}
```

Each time an agent calls `POST /v0/event`, the service persists the event, counts recent matches per active rule, and returns the triggered actions (if any) in the response so the orchestrator can notify humans or inject dynamic context into the next turn.

## Python client

All REST capabilities are also exposed via a lightweight in-process client:

```python
from mengram import MemoryClient, init_memory_os_schema

init_memory_os_schema()  # safe to call multiple times
client = MemoryClient()
client.remember(content="met Alice", type="episodic", scope="session")
memories = client.recall(query="Alice", scope="session")
rule = client.create_rule(
    condition={"event_type": "tool:error", "window_minutes": 10, "threshold_count": 3},
    actions={"actions": [{"type": "notify", "message": "tool is failing"}]},
)
client.record_event(event_type="tool:error", tool_name="search_tool")
```

Run `python scripts/smoke_client.py` for a quick end-to-end smoke test without starting the FastAPI server.

### Custom embeddings / offline smoke test

`MemoryClient` accepts a custom embedding function, so you can plug in OpenAI, Bedrock, or a fake vector generator for offline runs:

```python
import numpy as np
from mengram import MemoryClient, init_memory_os_schema

init_memory_os_schema()

def fake_embed(_: str):
    return np.ones(384, dtype=np.float32)

client = MemoryClient(embed_fn=fake_embed)
```

The shipping `scripts/smoke_client.py` uses the environment variable `MEMORY_OS_FAKE_EMBED=1` to activate the fake embed path, which avoids downloading the `sentence-transformers` model. Example:

```bash
MEMORY_OS_FAKE_EMBED=1 python scripts/smoke_client.py
```
