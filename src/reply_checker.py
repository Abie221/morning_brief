"""
v2: round-trip reply checker.

Polls Telegram for new messages, scores them against yesterday's concept,
sends feedback back. Designed to run on a schedule via GitHub Actions.
"""

import json
import os
from pathlib import Path
from typing import Optional

import anthropic
import requests

CONTENT_DIR = Path(__file__).parent.parent / "content"
STATE_PATH = Path(__file__).parent.parent / "state.json"
MODEL = "claude-opus-4-7"


# ── Telegram helpers ──────────────────────────────────────────────────────────

def _token() -> str:
    return os.environ["TELEGRAM_BOT_TOKEN"]


def _chat_id() -> str:
    return os.environ["TELEGRAM_CHAT_ID"]


def get_updates(offset: Optional[int] = None) -> list:
    params = {"timeout": 0, "allowed_updates": ["message"]}
    if offset is not None:
        params["offset"] = offset
    r = requests.get(
        f"https://api.telegram.org/bot{_token()}/getUpdates",
        params=params,
        timeout=10,
    )
    r.raise_for_status()
    return r.json().get("result", [])


def send_message(text: str) -> None:
    import re
    text = re.sub(r"\*\*(.+?)\*\*", r"*\1*", text, flags=re.DOTALL)
    requests.post(
        f"https://api.telegram.org/bot{_token()}/sendMessage",
        json={"chat_id": _chat_id(), "text": text, "parse_mode": "Markdown"},
        timeout=10,
    ).raise_for_status()


# ── Scoring ───────────────────────────────────────────────────────────────────

_SCORE_PROMPT = """\
You are reviewing a reply from Abay to a daily check question.

Yesterday's concept:
{concept_json}

The check question asked him to explain or apply the concept — not recall facts.

His reply:
{reply}

Write a short response (3–6 sentences):
- Acknowledge what he got right, specifically.
- Point out any gap or misconception, directly and without softening.
- Give one concrete thing to think about or try.

Tone rules (non-negotiable):
- No praise-padding. No "great job", "well done", "excellent".
- No emoji. No exclamation marks.
- Plain language. Short sentences.
- Do not repeat the question back to him.
- Do not summarize what he said before commenting on it.
"""


def score_reply(reply_text: str, concept: dict) -> str:
    prompt = _SCORE_PROMPT.format(
        concept_json=json.dumps(concept, indent=2, ensure_ascii=False),
        reply=reply_text.strip(),
    )
    client = anthropic.Anthropic()
    msg = client.messages.create(
        model=MODEL,
        max_tokens=512,
        messages=[{"role": "user", "content": prompt}],
    )
    return msg.content[0].text


# ── State helpers ─────────────────────────────────────────────────────────────

def load_state() -> dict:
    with open(STATE_PATH) as f:
        return json.load(f)


def save_state(state: dict) -> None:
    with open(STATE_PATH, "w") as f:
        json.dump(state, f, indent=2)
        f.write("\n")


def find_concept(topic_name: str) -> Optional[dict]:
    import yaml
    with open(CONTENT_DIR / "curriculum.yaml") as f:
        curriculum = yaml.safe_load(f)
    return next((c for c in curriculum if c.get("topic") == topic_name), None)


# ── Main ──────────────────────────────────────────────────────────────────────

def run() -> None:
    state = load_state()

    yesterday_topic = state.get("yesterday_topic")
    if not yesterday_topic:
        print("No yesterday_topic in state — nothing to check against.")
        return

    concept = find_concept(yesterday_topic)
    if not concept:
        print(f"Concept '{yesterday_topic}' not found in curriculum.")
        return

    offset = state.get("telegram_offset")
    updates = get_updates(offset)

    if not updates:
        print("No new messages.")
        return

    # Advance offset past all fetched updates
    new_offset = updates[-1]["update_id"] + 1

    # Filter to messages from our own chat only
    my_chat = str(_chat_id())
    replies = [
        u["message"]["text"]
        for u in updates
        if "message" in u and str(u["message"]["chat"]["id"]) == my_chat
        and "text" in u["message"]
    ]

    processed = []
    for reply_text in replies:
        print(f"Scoring reply: {reply_text[:80]}...")
        feedback = score_reply(reply_text, concept)
        send_message(feedback)
        processed.append({"reply": reply_text, "feedback": feedback})

    # Persist
    state["telegram_offset"] = new_offset
    state.setdefault("replies", []).extend(processed)
    save_state(state)

    print(f"Processed {len(processed)} reply(ies).")


if __name__ == "__main__":
    run()
