"""
Spell checking utilities using language_tool_python.
Supports Portuguese (pt-BR) and English (en-US).
"""
import language_tool_python
from api_types.common import Language

LANGUAGE_MAP = {
    Language.en: "en-US",
    Language.pt: "pt-BR", 
}

_tool_instances = {}


def initialize_language_tools():
    """Initialize LanguageTool instances for all supported languages at startup."""
    global _tool_instances
    for language, lang_code in LANGUAGE_MAP.items():
        print(f"Initializing LanguageTool for {lang_code}...")
        _tool_instances[language] = language_tool_python.LanguageTool(lang_code)
        print(f"✅ LanguageTool initialized for {lang_code}")


def get_language_tool(language: Language) -> language_tool_python.LanguageTool:
    """
    Get LanguageTool instance for the specified language.
    Must be initialized first via initialize_language_tools().
    """
    if language not in _tool_instances:
        raise RuntimeError(f"LanguageTool for {language} not initialized. Call initialize_language_tools() first.")
    return _tool_instances[language]


def check_and_correct_text(text: str, language: Language) -> str:
    """
    Check and correct spelling/grammar in text using language_tool_python.
    
    Args:
        text: The text to check and correct
        language: The language of the text (Language.en or Language.pt)
    
    Returns:
        The corrected text. Raises exception if tool fails.
    """
    if not text or not text.strip():
        return text
    
    tool = get_language_tool(language)
    matches = tool.check(text)
    
    if not matches:
        return text
    
    sorted_matches = sorted(matches, key=lambda m: m.offset, reverse=True)
    corrected_text = text
    
    for match in sorted_matches:
        if match.replacements:
            start = match.offset
            end = match.offset + match.error_length
            corrected_text = corrected_text[:start] + match.replacements[0] + corrected_text[end:]
    
    return corrected_text
    
