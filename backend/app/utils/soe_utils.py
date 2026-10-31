import re


QUESTION_REFERENCE = re.compile(
    r"^(?:q(?:uestion)?\s*)?(\d{1,2})\s*(?:\(\s*([a-z])\s*\))?$",
    re.IGNORECASE,
)


def parse_question_reference(value) -> tuple[int, str | None]:
    if isinstance(value, bool) or value is None:
        raise ValueError("Question reference is required")

    if isinstance(value, (int, float)):
        if not float(value).is_integer():
            raise ValueError(f"Invalid question reference: {value}")
        question_no = int(value)
        label = None
    else:
        reference = str(value).strip()
        match = QUESTION_REFERENCE.fullmatch(reference)
        if not match:
            raise ValueError(f"Invalid question reference: {reference}")
        question_no = int(match.group(1))
        label = match.group(2)

    if not 1 <= question_no <= 10:
        raise ValueError(f"Question number must be between 1 and 10: {question_no}")

    return question_no, label.lower() if label else None