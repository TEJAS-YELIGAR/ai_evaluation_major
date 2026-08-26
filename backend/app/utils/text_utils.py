import re
import logging

logger = logging.getLogger(__name__)

def split_by_question(full_text: str) -> dict:
    """
    Split full OCR text into per-question answers.
    Handles both clear and garbled OCR text.
    """
    answers = {}

    # Try multiple patterns for question markers
    patterns = [
        r'(?:Answer|Ans|Question|Q)[\s\.\:\-]?\s*(\d+)[\s\.\:\-]',
        r'(\d+)[\.\)]\s+[A-Z]',  # "1. CPU..." or "1) CPU..."
        r'(?:answer|ans)\s*(\d+)',  # lowercase
    ]

    for pattern in patterns:
        parts = re.split(pattern, full_text, flags=re.IGNORECASE)
        if len(parts) > 1:
            i = 1
            while i < len(parts) - 1:
                try:
                    q_num = int(parts[i])
                    answer_text = parts[i + 1].strip() if i + 1 < len(parts) else ""
                    if answer_text and q_num <= 20:
                        answers[q_num] = answer_text
                        logger.info(f"Q{q_num}: {len(answer_text)} chars")
                except (ValueError, IndexError):
                    pass
                i += 2

            if answers:
                logger.info(f"Found {len(answers)} answers using pattern")
                return answers

    # No markers found — try to split by SoE question count
    # For now treat entire text as Q1
    if not answers and full_text.strip():
        logger.warning("No markers found — using full text as Q1")
        answers[1] = full_text.strip()

    return answers