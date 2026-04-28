import json
from datetime import date
from pathlib import Path
from typing import Optional

import anthropic

PROMPT_PATH = Path(__file__).parent.parent / "prompts" / "synthesize.md"
MODEL = "claude-opus-4-7"
MAX_TOKENS = 4000


def synthesize(
    today: date,
    person: dict,
    principle: dict,
    concept_today: dict,
    concept_yesterday: Optional[dict],
    news: list,
) -> str:
    prompt_template = PROMPT_PATH.read_text()

    payload = {
        "date": today.isoformat(),
        "person": person,
        "principle": principle,
        "concept_today": concept_today,
        "concept_yesterday": concept_yesterday,
        "news": news,
    }

    prompt = prompt_template.replace(
        "{{json_payload}}",
        json.dumps(payload, indent=2, ensure_ascii=False),
    )

    client = anthropic.Anthropic()
    message = client.messages.create(
        model=MODEL,
        max_tokens=MAX_TOKENS,
        messages=[{"role": "user", "content": prompt}],
    )

    return message.content[0].text
