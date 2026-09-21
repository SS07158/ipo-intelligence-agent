import re


def is_heading(text: str) -> bool:
    """
    Heuristic check for whether a line looks like a document heading.
    """

    text = text.strip()

    if not text:
        return False

    if len(text) > 150:
        return False

    letters = [char for char in text if char.isalpha()]

    if not letters:
        return False

    uppercase_ratio = sum(char.isupper() for char in letters) / len(letters)

    return uppercase_ratio > 0.8