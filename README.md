# Morning Brief

A personal Telegram bot that sends one curated message every morning at ~07:00 Warsaw time. Replaces doom-scrolling.

Each brief contains: a historical figure's takeaway, a mental-model principle, three tech stories with practical hooks, today's AI engineering curriculum concept, and a check question on yesterday's concept.

## One-time Telegram setup

1. Message `@BotFather` on Telegram → `/newbot` → pick a name → copy the token.
2. Send any message to your new bot (so it has a chat to write to).
3. Open in a browser: `https://api.telegram.org/bot<TOKEN>/getUpdates`
4. Find `result[0].message.chat.id` in the JSON — that's your `TELEGRAM_CHAT_ID`.

## GitHub secrets to add

Go to your repo → Settings → Secrets and variables → Actions → New repository secret.

| Secret name | Value |
|---|---|
| `ANTHROPIC_API_KEY` | Your Anthropic API key |
| `TELEGRAM_BOT_TOKEN` | Token from BotFather |
| `TELEGRAM_CHAT_ID` | Your chat ID from getUpdates |

## Test locally

```bash
pip install -r requirements.txt
export ANTHROPIC_API_KEY=sk-ant-...
python -m src.main --dry-run   # prints brief, no Telegram, state still updates
```

## Trigger manually

GitHub → Actions → Morning Brief → Run workflow. Useful for testing the full pipeline before the first scheduled run.

## How state works

`state.json` is committed back to the repo after each run by the workflow. It tracks which day of the curriculum you're on, recent people/principles (to avoid repeats), and yesterday's topic for the check question. Don't delete it.
