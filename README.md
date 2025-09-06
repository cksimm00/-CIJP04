# py-chatbot

A minimal FastAPI chatbot that uses OpenAI models with support for streaming and simple, server-side conversation memory.

## 1) Setup

```bash
# from the unzipped folder
python -m venv .venv
# macOS/Linux
source .venv/bin/activate
# Windows (Powershell)
# .venv\Scripts\Activate.ps1

pip install -r requirements.txt

# copy env and set your key
cp .env.example .env
# then edit .env to set OPENAI_API_KEY
```

## 2) Run the API

```bash
uvicorn app:app --reload --port 8000
```

- POST `/chat` for a non-streaming reply
- POST `/chat/stream` for streaming text/plain chunks

### Example payload

```json
{
  "model": "gpt-4o-mini",
  "temperature": 0.7,
  "session_id": "my-user-123",
  "messages": [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "Write a haiku about databases."}
  ]
}
```

## 3) Quick local test (CLI)

In another terminal:

```bash
python cli.py
```

You should see a one-sentence greeting streamed to your terminal.

## 4) Notes

- Memory is stored **in-process** and will reset on server restart. For production, use Redis/DB and consider summarizing older turns.
- Avoid sending or storing PII in logs; this demo doesn't log prompts/responses.
- Model names evolve. You can change the default in `cli.py` or the request body.
