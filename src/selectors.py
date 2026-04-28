import random
from typing import Optional


def pick_person(state: dict, people: list) -> dict:
    recent = set(state.get("recent_people", []))
    candidates = [p for p in people if p["name"] not in recent]
    if not candidates:
        candidates = list(people)

    # Prefer a different field from the most recent pick
    recent_list = state.get("recent_people", [])
    if recent_list:
        last_field = next((p["field"] for p in people if p["name"] == recent_list[-1]), None)
        if last_field:
            diverse = [p for p in candidates if p["field"] != last_field]
            if diverse:
                candidates = diverse

    return random.choice(candidates)


def pick_principle(state: dict, principles: list) -> dict:
    recent = set(state.get("recent_principles", []))
    candidates = [p for p in principles if p["name"] not in recent]
    if not candidates:
        candidates = list(principles)

    # Prefer a different tradition from the most recent pick
    recent_list = state.get("recent_principles", [])
    if recent_list:
        last_tradition = next(
            (p["tradition"] for p in principles if p["name"] == recent_list[-1]), None
        )
        if last_tradition:
            diverse = [p for p in candidates if p["tradition"] != last_tradition]
            if diverse:
                candidates = diverse

    return random.choice(candidates)


def get_concept(state: dict, curriculum: list) -> dict:
    day = state.get("current_day", 1)
    idx = (day - 1) % len(curriculum)
    return curriculum[idx]
