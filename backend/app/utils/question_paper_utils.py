import re


def split_question_paper(text: str) -> list[dict]:
    """Split extracted paper text into numbered questions."""
    pattern = r"(?:^|\n)\s*(?:Q(?:uestion)?\s*)?(\d{1,2})\s*[.) :-]+"
    matches = list(re.finditer(pattern, text, flags=re.IGNORECASE))
    questions = []
    for index, match in enumerate(matches):
        question_text = text[match.end():matches[index + 1].start() if index + 1 < len(matches) else len(text)].strip()
        if question_text:
            questions.append({
                "question_no": int(match.group(1)),
                "question_text": question_text,
            })
    return questions