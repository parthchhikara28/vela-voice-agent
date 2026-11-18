import json
import time
import uuid
from dataclasses import dataclass, field, asdict
from pathlib import Path

LOG_PATH = Path(__file__).resolve().parents[1] / "logs" / "calls.jsonl"


@dataclass
class TurnTrace:
    call_id: str
    turn_id: str = field(default_factory=lambda: uuid.uuid4().hex[:8])
    t0: float = field(default_factory=time.perf_counter)
    marks: dict = field(default_factory=dict)
    transcript: str = ""
    reply: str = ""
    retrieved_ids: list = field(default_factory=list)
    tool_calls: list = field(default_factory=list)
    barge_in: bool = False

    def mark(self, name):
        """Write down 'this just happened' with a stopwatch time."""
        self.marks[name] = round(time.perf_counter() - self.t0, 4)

    def emit(self):
        """Add one line to the log file."""
        LOG_PATH.parent.mkdir(exist_ok=True)
        data = asdict(self)
        data.pop("t0")
        with open(LOG_PATH, "a", encoding="utf-8") as f:
            f.write(json.dumps(data) + "\n")