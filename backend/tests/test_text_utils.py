from app.utils.text_utils import has_unrecognized_glyphs, split_by_question
from app.utils.pdf_utils import prefer_ocr_text


def test_detects_repeated_unrecognized_glyphs():
    assert has_unrecognized_glyphs("Matrix: □ □ □")


def test_does_not_flag_normal_text_or_a_single_square():
    assert not has_unrecognized_glyphs("A matrix may contain one □ placeholder.")


def test_prefers_clean_ocr_text_over_pdf_text_with_missing_glyphs():
    assert prefer_ocr_text("Question matrix □ □ □", "Question matrix 0 1 0") == (
        "Question matrix 0 1 0"
    )


def test_keeps_direct_text_when_ocr_is_empty_or_still_corrupted():
    direct_text = "Question matrix □ □ □"
    assert prefer_ocr_text(direct_text, "") == direct_text
    assert prefer_ocr_text(direct_text, "Question matrix □ □ □") == direct_text


def test_groups_subquestions_and_preserves_out_of_order_answers():
    text = """Q9(a) Hashing answer
1. Division method
2. Mid-square method

Q1(a) Data structure definition
Q1(b) Dynamic memory allocation
"""

    answers = split_by_question(text)

    assert set(answers) == {1, 9}
    assert "Data structure definition" in answers[1]
    assert "Dynamic memory allocation" in answers[1]
    assert "1. Division method" in answers[9]
    assert "2. Mid-square method" in answers[9]


def test_does_not_treat_unlabeled_numbered_steps_as_questions():
    text = "Q3(a) Queue operations\n1. Check overflow\n2. Insert the item"

    answers = split_by_question(text)

    assert answers == {3: "Queue operations\n1. Check overflow\n2. Insert the item"}


def test_falls_back_to_single_answer_when_no_explicit_question_header():
    assert split_by_question("An unlabeled answer") == {1: "An unlabeled answer"}