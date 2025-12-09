from typing import Dict, Optional
from pydantic import BaseModel


class TopicState(BaseModel):
    mastery: float
    last_review: Optional[str] = None
    next_review: Optional[str] = None
    attempts: int
    correct: int
    wrong: int
    decay_rate: float


class KnowledgeGraph(BaseModel):
    topics: Dict[str, TopicState]

