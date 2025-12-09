import json
import os
from datetime import datetime, timedelta
from typing import Dict, List


class KnowledgeGraphService:
    def _path(self, student_id: str) -> str:
        base = os.path.join("students", student_id)
        os.makedirs(base, exist_ok=True)
        return os.path.join(base, "knowledge.json")

    def load_graph(self, student_id: str) -> Dict[str, dict]:
        path = self._path(student_id)
        if not os.path.exists(path):
            graph = {"topics": {}}
            with open(path, "w", encoding="utf-8") as f:
                json.dump(graph, f, ensure_ascii=False, indent=2)
            return graph
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            if not isinstance(data, dict) or "topics" not in data:
                return {"topics": {}}
            return data
        except Exception:
            return {"topics": {}}

    def save_graph(self, student_id: str, graph: Dict[str, dict]) -> None:
        path = self._path(student_id)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(graph, f, ensure_ascii=False, indent=2)

    def ensure_topic(self, graph: Dict[str, dict], topic: str) -> None:
        topics = graph.setdefault("topics", {})
        if topic not in topics:
            topics[topic] = {
                "mastery": 40,
                "last_review": None,
                "next_review": None,
                "attempts": 0,
                "correct": 0,
                "wrong": 0,
                "decay_rate": 0.05,
            }

    def update_mastery(self, graph: Dict[str, dict], topic: str, delta: float) -> None:
        self.ensure_topic(graph, topic)
        entry = graph["topics"][topic]
        old = float(entry.get("mastery", 0))
        new = max(0.0, min(100.0, old + float(delta)))
        entry["mastery"] = new
        entry["attempts"] = int(entry.get("attempts", 0)) + 1
        if delta > 0:
            entry["correct"] = int(entry.get("correct", 0)) + 1
        elif delta < 0:
            entry["wrong"] = int(entry.get("wrong", 0)) + 1
        now = datetime.utcnow().isoformat()
        entry["last_review"] = now
        if delta > 0:
            if new >= 70:
                days = 3
            elif new >= 40:
                days = 2
            else:
                days = 1
        else:
            days = 1
        entry["next_review"] = (datetime.utcnow() + timedelta(days=days)).isoformat()

    def apply_forgetting_curve(self, graph: Dict[str, dict]) -> None:
        topics = graph.get("topics", {})
        for t, entry in topics.items():
            lr = entry.get("last_review")
            rate = float(entry.get("decay_rate", 0.05))
            if not lr:
                continue
            try:
                last = datetime.fromisoformat(lr)
            except Exception:
                continue
            days = (datetime.utcnow() - last).days
            if days <= 0:
                continue
            factor = (1.0 - rate) ** days
            entry["mastery"] = max(0.0, min(100.0, float(entry.get("mastery", 0)) * factor))

    def get_weak_topics(self, graph: Dict[str, dict], limit: int = 5) -> List[str]:
        topics = graph.get("topics", {})
        ordered = sorted(topics.items(), key=lambda kv: float(kv[1].get("mastery", 0)))
        return [name for name, _ in ordered[:limit]]

