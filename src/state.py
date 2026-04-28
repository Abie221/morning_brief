import json
from pathlib import Path

STATE_PATH = Path(__file__).parent.parent / "state.json"

DEFAULT_STATE = {
    "current_day": 1,
    "recent_people": [],
    "recent_principles": [],
    "yesterday_topic": None,
    "last_run": None,
    "replies": [],
}


def load_state() -> dict:
    if not STATE_PATH.exists():
        return DEFAULT_STATE.copy()
    with open(STATE_PATH) as f:
        return json.load(f)


def save_state(state: dict) -> None:
    with open(STATE_PATH, "w") as f:
        json.dump(state, f, indent=2)
        f.write("\n")
