from fastapi import Depends
import database

def get_db():
    return database.db

import language_tool_python
from deep_translator import GoogleTranslator

language_tools = {
    "en": language_tool_python.LanguageTool("en-US"),
    "fr": language_tool_python.LanguageTool("fr"),
    "nl": language_tool_python.LanguageTool("nl"),
    "es": language_tool_python.LanguageTool("es"),
    "pt": language_tool_python.LanguageTool("pt"),
    "de": language_tool_python.LanguageTool("de")
}

def grammarCorrector(text, language):
    tool = language_tools.get(language)
    if not tool:
        tool = language_tool_python.LanguageTool(language)
        language_tools[language] = tool 
    return tool.correct(text)

def translate(text, src_language):
    return GoogleTranslator(source=src_language, target='en').translate(text)

def correct_grammer_and_translate(text, src_language):
    corrected_text = grammarCorrector(text, src_language)
    if src_language != "en":
        corrected_text = translate(corrected_text, src_language)
    
    return corrected_text

import re

def doTextSegmentation(mode, text):
    def get_segments(sentences, size, step):
        if step is None:
            step = 1 if size > 1 else size
        return [
            " ".join(sentences[i:i+size])
            for i in range(0, len(sentences) - size + 1, step)
        ]
    
    pattern = r'(?<=[.!?])\s+(?=\S)'
    sentences = re.split(pattern, text.strip())
    sentences = [s.strip() for s in sentences if s.strip()] 

    if mode == "conservative":
        segments = get_segments(sentences, 3, step=2)
    elif mode == "broader":
        segments = get_segments(sentences, 2, step=1)
    else:
        segments = []

    return segments if segments else [text.strip()]
    