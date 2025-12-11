from llm_runtime.ollama_client import OllamaClient
import json

# Instantiate the LLM client module-level
llm = OllamaClient()

# --- Prompt Templates ---

EXPLAIN_PROMPT_TEMPLATE = """Explain the academic topic '{topic}' in simple language suitable for an undergraduate engineering student. Use concrete examples, one short analogy, and a 3-bullet 'Key takeaways' section. If additional context is provided, use it to focus the explanation. Output only plain text—do NOT wrap in JSON."""

FLASHCARD_PROMPT_TEMPLATE = """You are an educational assistant. Generate {count} concise flashcards for the topic: "{topic}". Each flashcard must have 'q' (question) and 'a' (short answer). Output STRICT JSON only, with the top-level object: {{"flashcards": [{{"q":"...", "a":"..."}}, ...]}}. No extra commentary or plaintext outside JSON."""

MCQ_PROMPT_TEMPLATE = """You are an exam generator. Create {count} high-quality multiple-choice questions for the topic: "{topic}". Each MCQ must include:
- "question": string
- "options": array of exactly 4 strings
- "answer_index": integer (0-based index of correct option)
- "explanation": one sentence

Output STRICT JSON only: {{"mcqs": [ {{...}}, {{...}} ]}}. No extra text."""

STUDYPLAN_PROMPT_TEMPLATE = """You are a curriculum planner. Given topics: {topics} and student mastery: {student_state} (a JSON map topic->mastery 0-100), produce a {days}-day study plan that focuses on weakest topics and spaced repetitions. Output STRICT JSON only:

{{
 "plan": [
   {{"day": 1, "tasks": ["Topic A - 20min reading", "Topic B - 15min quiz"]}},
   ...
 ],
 "plan_text": "Short human-readable summary"
}}

No extra text outside the JSON."""

# --- Tool Functions ---

def explain_topic(args: dict) -> dict:
    """
    Explains an academic topic.
    
    Args:
        args (dict): Must contain 'topic' (str) and optionally 'context' (str).
        
    Returns:
        dict: {"topic": str, "explanation": str}
    """
    topic = args.get("topic")
    context = args.get("context", "")
    
    # Simple check to append context if needed, or just rely on the template implication
    # The template says "If additional context is provided...", so we should probably inject it into the prompt if distinct, 
    # but the template has '{topic}'. It doesn't look like it has a '{context}' placeholder in the text provided in section 4.
    # However, the first section prompt template had "If context is provided, prioritize context." 
    # I will construct the prompt by formatting {topic}. If context exists, I'll append it to the prompt.
    
    prompt = EXPLAIN_PROMPT_TEMPLATE.format(topic=topic)
    if context:
        prompt += f"\n\nContext: {context}"
        
    result_text = llm.ask(prompt)
    return {"topic": topic, "explanation": result_text}

def flashcards_for_topic(args: dict) -> dict:
    """
    Generates flashcards for a given topic.
    
    Args:
        args (dict): 'topic' (str), optional 'count' (int, default 8).
        
    Returns:
        dict: JSON response with flashcards list or raw fallback.
    """
    topic = args.get("topic")
    count = args.get("count", 8)
    
    prompt = FLASHCARD_PROMPT_TEMPLATE.format(topic=topic, count=count)
    response = llm.ask_json(prompt)
    
    # Validate structure if parsed
    if "flashcards" in response and isinstance(response["flashcards"], list):
        return response
    
    # Fallback/Raw
    if "_raw" in response:
         return response
         
    return {"flashcards": [], "_error": "Failed to parse flashcards", "_raw": str(response)}

def generate_mcq(args: dict) -> dict:
    """
    Generates multiple-choice questions.
    
    Args:
        args (dict): 'topic' (str), optional 'count' (int, default 3).
        
    Returns:
        dict: JSON response with mcqs list.
    """
    topic = args.get("topic")
    count = args.get("count", 3)
    
    prompt = MCQ_PROMPT_TEMPLATE.format(topic=topic, count=count)
    response = llm.ask_json(prompt)
    
    # Validation logic could be added here as per prompt instructions check array length etc.
    if "mcqs" in response and isinstance(response["mcqs"], list):
        # Basic validation (optional but requested "validate mcqs before returning")
        valid_mcqs = []
        for mcq in response["mcqs"]:
            if len(mcq.get("options", [])) == 4 and "answer_index" in mcq:
                 valid_mcqs.append(mcq)
        response["mcqs"] = valid_mcqs
        
    return response

def generate_studyplan(args: dict) -> dict:
    """
    Generates a study plan.
    
    Args:
        args (dict): 'topics' (list), 'days' (int), 'student_state' (dict).
        
    Returns:
        dict: Plan JSON and text summary.
    """
    topics = args.get("topics")
    days = args.get("days", 3)
    student_state = args.get("student_state", {})
    
    # Convert lists/dicts to string representation for the prompt
    prompt = STUDYPLAN_PROMPT_TEMPLATE.format(topics=topics, student_state=json.dumps(student_state), days=days)
    return llm.ask_json(prompt)

# --- Schemas ---

EXPLAIN_SCHEMA = {
    "type": "object",
    "properties": {
        "topic": {"type": "string"},
        "context": {"type": "string"}
    },
    "required": ["topic"]
}

FLAShCARD_SCHEMA = {
    "type": "object",
    "properties": {
        "topic": {"type": "string"},
        "count": {"type": "integer"}
    },
    "required": ["topic"]
}

MCQ_SCHEMA = {
    "type": "object",
    "properties": {
        "topic": {"type": "string"},
        "count": {"type": "integer"},
        "difficulty": {"type": "string"}
    },
    "required": ["topic"]
}

STUDYPLAN_SCHEMA = {
    "type": "object",
    "properties": {
        "topics": {"type": "array", "items": {"type": "string"}},
        "days": {"type": "integer"},
        "student_state": {"type": "object"}
    },
    "required": ["topics", "days", "student_state"]
}
