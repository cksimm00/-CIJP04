import os
import json
from typing import List, Dict, Any, Optional
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from openai import OpenAI
from memory import MemoryStore

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
memory = MemoryStore(max_turns=30)

app = FastAPI(title="Python Chatbot")

# ---- Schemas ----
class ChatMessage(BaseModel):
    role: str = Field(pattern="^(system|user|assistant)$")
    content: str

class ChatRequest(BaseModel):
    messages: List[ChatMessage]
    model: str = "gpt-4o-mini"
    temperature: float = 0.7
    session_id: Optional[str] = "default"

# ---- Helpers ----
def sanitize_for_logs(text: str) -> str:
    return text.replace(os.getenv("OPENAI_API_KEY", ""), "[redacted]") if text else text

def _to_input(messages: List[ChatMessage]) -> List[Dict[str, str]]:
    return [{"role": m.role, "content": m.content} for m in messages]

# ---- Routes ----
@app.post("/chat")
def chat(req: ChatRequest):
    """
    Non-streaming endpoint: returns the full assistant reply in one response.
    """
    try:
        history = memory.get(req.session_id)
        combined = history + _to_input(req.messages)

        resp = client.responses.create(
            model=req.model,
            input=combined,
            temperature=req.temperature,
        )
        text = resp.output_text

        # update memory: append request messages and assistant reply
        for m in _to_input(req.messages):
            memory.append(req.session_id, m)
        memory.append(req.session_id, {"role": "assistant", "content": text})

        return {"reply": text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=sanitize_for_logs(str(e)))

@app.post("/chat/stream")
def chat_stream(req: ChatRequest):
    """
    Streaming endpoint: yields chunks of the assistant's text as they arrive.
    """
    def event_generator():
        acc = []
        try:
            history = memory.get(req.session_id)
            combined = history + _to_input(req.messages)

            with client.responses.stream(
                model=req.model,
                input=combined,
                temperature=req.temperature,
            ) as stream:
                for event in stream:
                    if event.type == "response.output_text.delta":
                        chunk = event.delta or ""
                        acc.append(chunk)
                        yield chunk
                stream.until_done()

            # after stream completes, persist turn
            for m in _to_input(req.messages):
                memory.append(req.session_id, m)
            memory.append(req.session_id, {"role": "assistant", "content": "".join(acc)})
        except Exception as e:
            yield f"\n[STREAM-ERROR] {sanitize_for_logs(str(e))}\n"
    return StreamingResponse(event_generator(), media_type="text/plain")
