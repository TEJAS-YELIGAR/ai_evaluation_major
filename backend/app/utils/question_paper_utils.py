import re


def split_question_paper(text: str) -> list[dict]:
    """Split extracted paper text into numbered questions."""
    pattern = r"(?:^|\n)\s*Q(?:uestion)?\s*[.:]?\s*(\d{1,2})(?=\s|[.):\-]|$)"
    matches = list(re.finditer(pattern, text, flags=re.IGNORECASE))
    questions_by_number = {}
    for index, match in enumerate(matches):
        question_text = text[match.end():matches[index + 1].start() if index + 1 < len(matches) else len(text)].strip()
        if question_text:
            question_no = int(match.group(1))
            if question_no in questions_by_number:
                questions_by_number[question_no]["question_text"] += "\n\n" + question_text
            else:
                questions_by_number[question_no] = {
                    "question_no": question_no,
                    "question_text": question_text,
                }
    return list(questions_by_number.values())