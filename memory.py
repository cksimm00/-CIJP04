from collections import defaultdict
from typing import List, Dict

class MemoryStore:
    """
    Super-simple in-memory conversation buffer.
    NOT for production; switch to Redis/DB for multi-process deployments.
    """
    def __init__(self, max_turns: int = 20):
        self.store: Dict[str, List[Dict]] = defaultdict(list)
        self.max_turns = max_turns

    def get(self, session_id: str) -> List[Dict]:
        return self.store.get(session_id, [])

    def append(self, session_id: str, msg: Dict):
        conv = self.store[session_id]
        conv.append(msg)
        # limit memory size
        self.store[session_id] = conv[-self.max_turns :]
