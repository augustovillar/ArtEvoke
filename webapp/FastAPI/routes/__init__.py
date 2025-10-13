from orm import get_db
import re


def correct_grammer_and_translate(text, src_language=None):
    # Since we assume English input, just return the text as-is
    return text


def doTextSegmentation(mode, text):
    def get_segments(sentences, size, step):
        if step is None:
            step = 1 if size > 1 else size
        return [
            " ".join(sentences[i : i + size])
            for i in range(0, len(sentences) - size + 1, step)
        ]

    pattern = r"(?<=[.!?])\s+(?=\S)"
    sentences = re.split(pattern, text.strip())
    sentences = [s.strip() for s in sentences if s.strip()]

    if mode == "conservative":
        segments = get_segments(sentences, 3, step=2)
    elif mode == "broader":
        segments = get_segments(sentences, 2, step=1)
    else:
        segments = []

    return segments if segments else [text.strip()]
