import re
import logging
import unicodedata

logger = logging.getLogger(__name__)

UNRECOGNIZED_GLYPHS = frozenset("\ufffd\u25a1\u25ab\u25ad\u25af\u2610\u25a0\u25aa")


def has_unrecognized_glyphs(text: str) -> bool:
    replacement_count = sum(character in UNRECOGNIZED_GLYPHS for character in text)
    if replacement_count >= 3:
        return True

    unsupported_count = sum(
        unicodedata.category(character) in {"Co", "Cn"}
        for character in text
    )
    return unsupported_count >= 2


QUESTION_HEADER = re.compile(
    r"(?im)^[ \t]*(?:(?:answer|ans(?:wer)?|question|q)\s*[:.\-]?\s*"
    r"(?P<prefixed_no>\d{1,2})(?:\s*\(\s*(?P<prefixed_label>[a-z])\s*\))?"
    r"|(?P<bare_no>\d{1,2})\s*\(\s*(?P<bare_label>[a-z])\s*\))"
    r"[ \t]*(?:[:.)\-][ \t]*)?"
)


def split_by_question(full_text: str) -> dict:
    """
    Split answer text on explicit question headers and combine subquestions.
    """
    matches = list(QUESTION_HEADER.finditer(full_text))
    answers = {}

    for index, match in enumerate(matches):
        question_no = int(match.group("prefixed_no") or match.group("bare_no"))
        if not 1 <= question_no <= 10:
            continue

        end = matches[index + 1].start() if index + 1 < len(matches) else len(full_text)
        answer_text = full_text[match.end():end].strip()
        if not answer_text:
            continue

        if question_no in answers:
            answers[question_no] += "\n\n" + answer_text
        else:
            answers[question_no] = answer_text

    if answers:
        for question_no, answer_text in answers.items():
            logger.info(f"Q{question_no}: {len(answer_text)} chars")
        logger.info(f"Found {len(answers)} explicitly labeled answers")
        return answers

    if full_text.strip():
        logger.warning("No explicit question headers found — using full text as Q1")
        return {1: full_text.strip()}

    return {}