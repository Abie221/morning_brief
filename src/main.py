import argparse
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Optional

import yaml

from .news import fetch_news
from .selectors import get_concept, pick_person, pick_principle
from .state import load_state, save_state
from .synthesizer import synthesize
from .telegram import send

CONTENT_DIR = Path(__file__).parent.parent / "content"


def _load_yaml(filename: str) -> list:
    with open(CONTENT_DIR / filename) as f:
        return yaml.safe_load(f)


def run(dry_run: bool = False) -> None:
    state = load_state()

    people = _load_yaml("people.yaml")
    principles = _load_yaml("principles.yaml")
    curriculum = _load_yaml("curriculum.yaml")

    person = pick_person(state, people)
    principle = pick_principle(state, principles)
    concept_today = get_concept(state, curriculum)

    concept_yesterday: Optional[dict] = None
    yesterday_topic = state.get("yesterday_topic")
    if yesterday_topic:
        concept_yesterday = next(
            (c for c in curriculum if c.get("topic") == yesterday_topic), None
        )

    news = fetch_news()

    brief = synthesize(
        today=date.today(),
        person=person,
        principle=principle,
        concept_today=concept_today,
        concept_yesterday=concept_yesterday,
        news=news,
    )

    send(brief, dry_run=dry_run)

    # Update state after successful send
    state["recent_people"] = (state.get("recent_people", []) + [person["name"]])[-60:]
    state["recent_principles"] = (state.get("recent_principles", []) + [principle["name"]])[-30:]
    state["yesterday_topic"] = concept_today.get("topic")
    state["current_day"] = state.get("current_day", 1) + 1
    state["last_run"] = datetime.now(timezone.utc).isoformat()

    save_state(state)

    if not dry_run:
        print(f"Sent. Day {state['current_day'] - 1} complete.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Morning brief bot")
    parser.add_argument("--dry-run", action="store_true", help="Print brief instead of sending to Telegram")
    args = parser.parse_args()
    run(dry_run=args.dry_run)


if __name__ == "__main__":
    main()
