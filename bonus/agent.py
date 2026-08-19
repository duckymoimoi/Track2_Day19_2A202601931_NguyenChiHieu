"""Small dependency-free hybrid memory POC."""
from __future__ import annotations
import hashlib, math, re
from dataclasses import dataclass

def _tokens(text: str) -> list[str]:
    return re.findall(r"[\wÀ-ỹ]+", text.lower())

def _vector(text: str, size: int = 128) -> list[float]:
    v = [0.0] * size
    for token in _tokens(text):
        digest = hashlib.blake2b(token.encode("utf-8"), digest_size=4).digest()
        v[int.from_bytes(digest, "big") % size] += 1.0
    norm = math.sqrt(sum(x * x for x in v)) or 1.0
    return [x / norm for x in v]

def _cosine(a: list[float], b: list[float]) -> float:
    return sum(x * y for x, y in zip(a, b))

@dataclass
class Memory:
    user_id: str
    text: str
    vector: list[float]

class HybridMemoryAgent:
    def __init__(self) -> None:
        self.memories: list[Memory] = []
        self.profiles = {"u_001": {"topic_affinity": "cloud", "preferred_language": "vi/en mix", "reading_speed_wpm": 260, "queries_last_hour": ["Kubernetes autoscaling", "cloud security"]}}

    def remember(self, text: str, user_id: str = "u_001") -> None:
        self.memories.append(Memory(user_id, text, _vector(text)))

    def recall(self, query: str, user_id: str = "u_001") -> str:
        profile = self.profiles.get(user_id, {})
        ranked = sorted((m for m in self.memories if m.user_id == user_id), key=lambda m: _cosine(_vector(query), m.vector), reverse=True)[:3]
        memories = "\n".join(f"- {m.text}" for m in ranked) or "- Chưa có memory phù hợp."
        activity = ", ".join(profile.get("queries_last_hour", [])) or "chưa có dữ liệu"
        return (f"User profile: topic_affinity={profile.get('topic_affinity', 'unknown')}; language={profile.get('preferred_language', 'unknown')}; speed={profile.get('reading_speed_wpm', 'unknown')} wpm.\nRecent activity: {activity}.\nTop memories:\n{memories}")
