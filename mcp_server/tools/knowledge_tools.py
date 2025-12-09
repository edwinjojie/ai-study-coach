from typing import Dict, List

from services.knowledge_graph.graph_service import KnowledgeGraphService
from services.knowledge_graph.models import KnowledgeGraph, TopicState


service = KnowledgeGraphService()


def load_knowledge(args: Dict) -> Dict:
    student_id = args.get("student_id", "")
    graph = service.load_graph(student_id)
    return {"graph": graph}


def update_knowledge(args: Dict) -> Dict:
    student_id = args.get("student_id", "")
    topic = args.get("topic", "")
    delta = float(args.get("delta", 0))
    graph = service.load_graph(student_id)
    service.ensure_topic(graph, topic)
    service.update_mastery(graph, topic, delta)
    service.save_graph(student_id, graph)
    mastery = graph["topics"][topic]["mastery"]
    return {"topic": topic, "mastery": mastery}


def get_weak_topics(args: Dict) -> Dict:
    student_id = args.get("student_id", "")
    limit = int(args.get("limit", 5))
    graph = service.load_graph(student_id)
    topics = service.get_weak_topics(graph, limit=limit)
    return {"topics": topics}


def get_graph(args: Dict) -> Dict:
    student_id = args.get("student_id", "")
    graph = service.load_graph(student_id)
    return {"graph": graph}


LOAD_SCHEMA = {
    "input": {"student_id": "string"},
    "output": {"graph": "object"},
}

UPDATE_SCHEMA = {
    "input": {"topic": "string", "delta": "number", "student_id": "string"},
    "output": {"topic": "string", "mastery": "number"},
}

WEAK_SCHEMA = {
    "input": {"student_id": "string", "limit": "number"},
    "output": {"topics": "list"},
}

GRAPH_SCHEMA = {
    "input": {"student_id": "string"},
    "output": {"graph": "object"},
}

