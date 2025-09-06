import argparse
import requests
import sys

API = "http://localhost:8000/chat/stream"

def stream_chat(prompt: str, session_id: str, model: str, temperature: float):
    payload = {
        "model": model,
        "temperature": temperature,
        "session_id": session_id,
        "messages": [
            {"role": "system", "content": "You are a helpful, concise assistant."},
            {"role": "user", "content": prompt}
        ],
    }
    with requests.post(API, json=payload, stream=True) as r:
        r.raise_for_status()
        for chunk in r.iter_content(chunk_size=None):
            if chunk:
                sys.stdout.write(chunk.decode("utf-8"))
                sys.stdout.flush()
        print()  # newline at end

def main():
    parser = argparse.ArgumentParser(description="Interactive CLI for local chatbot")
    parser.add_argument("--model", default="gpt-4o-mini", help="Model name (default: gpt-4o-mini)")
    parser.add_argument("--session", default="local-cli", help="Session id to preserve memory (default: local-cli)")
    parser.add_argument("--temp", type=float, default=0.7, help="Temperature (default: 0.7)")
    args = parser.parse_args()

    print("💬 Chatbot CLI (Ctrl+C or type 'exit' to quit)")
    print(f"→ Using model={args.model}, session={args.session}, temp={args.temp}")
    print()

    try:
        while True:
            try:
                prompt = input("> ").strip()
            except EOFError:
                print()
                break

            if not prompt:
                continue
            if prompt.lower() in {"exit", "quit", ":q"}:
                break

            try:
                stream_chat(prompt, args.session, args.model, args.temp)
            except requests.HTTPError as e:
                try:
                    print(f"[HTTP {e.response.status_code}] {e.response.text}")
                except Exception:
                    print(f"[HTTP error] {e}")
            except Exception as e:
                print(f"[Error] {e}")

    except KeyboardInterrupt:
        print("\nBye!")

if __name__ == "__main__":
    main()
