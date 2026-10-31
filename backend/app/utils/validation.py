import re


USN_PATTERN = re.compile(r"[1-9][A-Z]{2}[0-9]{2}[A-Z]{2}[0-9]{3}")
ALLOWED_NAME_PUNCTUATION = frozenset(" .'-’")


def normalize_usn(usn: str) -> str:
    normalized = usn.strip().upper()
    if not USN_PATTERN.fullmatch(normalized):
        raise ValueError("USN must match the format 4JD23IS107")
    return normalized


def validate_full_name(full_name: str) -> str:
    normalized = " ".join(full_name.split())
    if not 2 <= len(normalized) <= 100:
        raise ValueError("Full name must be between 2 and 100 characters")
    if not any(character.isalpha() for character in normalized):
        raise ValueError("Full name must contain at least one letter")
    if any(
        not (character.isalpha() or character in ALLOWED_NAME_PUNCTUATION)
        for character in normalized
    ):
        raise ValueError(
            "Full name may contain only letters, spaces, apostrophes, periods, and hyphens"
        )
    return normalized
