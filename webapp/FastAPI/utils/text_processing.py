import re
import math


def _get_sentences(text):
    pattern = r"(?<=[.!?])\s+(?=\S)"
    sentences = re.split(pattern, text.strip())
    return [s.strip() for s in sentences if s.strip()]


def _get_sections(sentences, size, step, ensure_last=False, max_segments=None):
    if step is None:
        step = 1 if size > 1 else size
    starts = list(range(0, len(sentences) - size + 1, step))
    if max_segments and len(starts) > max_segments:
        starts = starts[:max_segments]
    if (
        ensure_last
        and starts
        and (len(sentences) - size) not in starts
        and (max_segments is None or len(starts) < max_segments)
    ):
        starts.append(len(sentences) - size)
    starts = sorted(starts)
    return [" ".join(sentences[i : i + size]) for i in starts]


def doTextSegmentation(mode, text, max_sections):
    sentences = _get_sentences(text)

    if mode == "conservative":
        size = 3
        step = 2
        ensure_last = True
    elif mode == "broader":
        size = 2
        step = 1
        ensure_last = False
    else:
        return [text.strip()]

    # Check traditional sections
    sections = _get_sections(sentences, size, step, ensure_last)
    # ensure max_sections
    if len(sections) > max_sections:
        size = math.ceil(len(sentences) / max_sections)
        step = max(1, size - 1)
        sections = _get_sections(sentences, size, step, ensure_last, max_sections)

    return sections
