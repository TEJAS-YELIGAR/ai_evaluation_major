import pytest

from app.utils.soe_utils import parse_question_reference


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (1, (1, None)),
        ("Q1", (1, None)),
        ("Q1(a)", (1, "a")),
        ("Question 10 (C)", (10, "c")),
    ],
)
def test_parse_question_reference(value, expected):
    assert parse_question_reference(value) == expected


@pytest.mark.parametrize("value", [None, "Q1(a)(i)", "Q11", 2.5])
def test_reject_invalid_question_reference(value):
    with pytest.raises(ValueError):
        parse_question_reference(value)