import pytest
from pydantic import ValidationError

from app.schemas.auth import RegisterRequest
from app.utils.validation import normalize_usn, validate_full_name


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("4JD23IS107", "4JD23IS107"),
        (" 4jd23is107 ", "4JD23IS107"),
    ],
)
def test_normalize_usn_accepts_valid_format(value, expected):
    assert normalize_usn(value) == expected


@pytest.mark.parametrize(
    "value",
    ["4JD23IS10", "0JD23IS107", "4J223IS107", "4JD2AIS107", "4JD23I!107"],
)
def test_normalize_usn_rejects_invalid_format(value):
    with pytest.raises(ValueError, match="USN must match"):
        normalize_usn(value)


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("  Jane   Doe ", "Jane Doe"),
        ("Anne-Marie O'Neil", "Anne-Marie O'Neil"),
        ("José García", "José García"),
    ],
)
def test_validate_full_name_accepts_and_normalizes_name(value, expected):
    assert validate_full_name(value) == expected


@pytest.mark.parametrize("value", [" ", "A", "A1 Smith", "!!!", "X" * 101])
def test_validate_full_name_rejects_invalid_name(value):
    with pytest.raises(ValueError):
        validate_full_name(value)


@pytest.mark.parametrize(
    "password",
    ["short", "p" * 73, "😀" * 19],
)
def test_registration_rejects_password_outside_limits(password):
    with pytest.raises(ValidationError):
        RegisterRequest(
            username="teacher",
            full_name="Jane Doe",
            password=password,
        )


@pytest.mark.parametrize("password", ["password", "😀" * 18])
def test_registration_accepts_password_within_limits(password):
    request = RegisterRequest(
        username="teacher",
        full_name="Jane Doe",
        password=password,
    )
    assert request.password == password
