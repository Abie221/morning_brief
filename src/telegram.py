import os
import re

import requests

_API = "https://api.telegram.org/bot{token}/sendMessage"
_MSG_LIMIT = 4096


def send(message: str, dry_run: bool = False) -> None:
    message = _to_telegram_markdown(message)

    if dry_run:
        print(message)
        return

    token = os.environ["TELEGRAM_BOT_TOKEN"]
    chat_id = os.environ["TELEGRAM_CHAT_ID"]
    url = _API.format(token=token)

    for chunk in _split(message, _MSG_LIMIT):
        r = requests.post(
            url,
            json={"chat_id": chat_id, "text": chunk, "parse_mode": "Markdown"},
            timeout=10,
        )
        r.raise_for_status()


def _to_telegram_markdown(text: str) -> str:
    # Claude outputs **bold**; Telegram Markdown (V1) uses *bold*
    return re.sub(r"\*\*(.+?)\*\*", r"*\1*", text, flags=re.DOTALL)


def _split(text: str, limit: int) -> list:
    if len(text) <= limit:
        return [text]
    parts = []
    while text:
        if len(text) <= limit:
            parts.append(text)
            break
        cut = text.rfind("\n", 0, limit)
        if cut == -1:
            cut = limit
        parts.append(text[:cut])
        text = text[cut:].lstrip("\n")
    return parts
