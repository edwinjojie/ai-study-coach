import json
import re

def extract_json_from_text(text: str) -> dict:
    """
    Finds the first JSON object in text and returns the parsed dict.
    
    Args:
        text (str): The input string containing JSON.
        
    Returns:
        dict: The parsed JSON object.
        
    Raises:
        ValueError: If no JSON object is found or parsing fails.
        
    Example:
        >>> text = "Here is the data: {\"key\": \"value\"} end."
        >>> extract_json_from_text(text)
        {'key': 'value'}
    """
    # Find first balanced JSON object using regex for { ... }
    # This is a naive regex but works for the prompt's context
    m = re.search(r'\{.*\}', text, flags=re.S)
    if not m:
        raise ValueError("No JSON object found")
    candidate = m.group(0)
    return json.loads(candidate)

def safe_parse_json(text: str) -> dict:
    """
    Attempts to parse JSON from text using multiple strategies.
    1. Direct json.loads
    2. Extraction of { ... } substring
    3. Fallback to {"_raw": text}
    
    Args:
        text (str): The input string.
        
    Returns:
        dict: The parsed JSON or a wrapper containing the raw text.
    
    Example:
        >>> safe_parse_json('{"a": 1}')
        {'a': 1}
        >>> safe_parse_json('Output: {"b": 2}')
        {'b': 2}
        >>> safe_parse_json('Not JSON')
        {'_raw': 'Not JSON'}
    """
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    
    try:
        return extract_json_from_text(text)
    except (ValueError, json.JSONDecodeError):
        return {"_raw": text}
