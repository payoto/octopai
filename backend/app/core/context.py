from contextlib import contextmanager
from contextvars import ContextVar
from typing import Optional
from dataclasses import dataclass
from typing import Optional
from contextvars import ContextVar
from pathlib import Path
import json


@dataclass
class RequestContext:
    request_id: Optional[str] = None
    counter: int = 0

    def set_request_id(self, request_id: str):
        self.request_id = request_id

# Create context var with the custom class
request_context: ContextVar[RequestContext] = ContextVar(
    "request_context",
    default=RequestContext()
)

@contextmanager
def request_context_manager():
    token = request_context.set(RequestContext())
    try:
        yield request_context.get()
    finally:
        request_context.reset(token)

def log_response_messages(messages, type="chat"):
    context = request_context.get()
    context.counter += 1
    counter = context.counter
    # Log the request from the model to disk

    print(f"Logging request to disk: {context.request_id}")
    request_log_path = Path(f"logs/requests/{context.request_id}/{counter}_{type}.json")
    request_log_path.parent.mkdir(parents=True, exist_ok=True)
    request_log_path.write_text(json.dumps(messages, indent=2))
