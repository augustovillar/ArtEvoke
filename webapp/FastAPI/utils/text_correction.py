"""
Generic JSON parsing utilities for LLM responses.
"""
import json
from typing import Optional, Dict, Any, Union


def extract_json_from_response(response_content: str) -> Optional[str]:
    """Extract JSON string from LLM response content."""
    response_content = response_content.strip()
    
    if "```json" in response_content:
        start = response_content.find("```json") + 7
        end = response_content.find("```", start)
        if end != -1:
            return response_content[start:end].strip()
    elif "```" in response_content:
        start = response_content.find("```") + 3
        end = response_content.find("```", start)
        if end != -1:
            extracted = response_content[start:end].strip()
            if extracted.startswith(('{', '[')):
                return extracted
    
    if response_content.startswith('{') or response_content.startswith('['):
        return response_content
    
    return None


def parse_llm_json_response(
    response_content: str,
    json_key: Optional[str] = None,
    raise_on_error: bool = False,
    fallback_value: Optional[Any] = None
) -> Union[Dict[str, Any], str, Any]:
    """Parse JSON from LLM response. Returns full dict if json_key is None, otherwise extracts the key."""
    response_content = response_content.strip()
    json_str = extract_json_from_response(response_content)
    
    if not json_str:
        if raise_on_error:
            raise ValueError("The AI response does not contain valid JSON format")
        return fallback_value if fallback_value is not None else response_content
    
    try:
        parsed_response = json.loads(json_str)
        
        if json_key is not None:
            if isinstance(parsed_response, dict):
                return parsed_response.get(json_key, fallback_value if fallback_value is not None else response_content)
            return fallback_value if fallback_value is not None else response_content
        
        return parsed_response
        
    except json.JSONDecodeError:
        if raise_on_error:
            raise
        return fallback_value if fallback_value is not None else response_content


