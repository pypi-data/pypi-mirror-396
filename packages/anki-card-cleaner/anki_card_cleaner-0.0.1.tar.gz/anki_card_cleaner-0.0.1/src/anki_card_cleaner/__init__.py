import re

def clean_card_text(text: str) -> str:
    """
    Cleans the card text by replacing non-breaking spaces, removing cloze deletions,
    and adding spaces after question marks if not present.
    Handles NaN/Float inputs safely.
    """
    # 0. Handle NaN/Float
    if not isinstance(text, str):
        return ""

    # 1. Replace non-breaking spaces
    clean_text = text.replace("\xa0", " ")

    # 2. Remove cloze deletions and move hints into parentheses
    # Handle {{c1::Answer::Hint}} --> Answer (Hint)
    clean_text = re.sub(
        r"\{\{c\d+::(.*?)(::(.*?))?\}\}",
        lambda m: f"{m.group(1)} ({m.group(3)})" if m.group(3) else m.group(1),
        clean_text,
    )

    # Some cloze deletions only have 1 { and 1 }, e.g., {c1::Answer}
    clean_text = re.sub(
        r"\{c\d+::(.*?)\}",
        lambda m: m.group(1),  # Just return the answer part
        clean_text,
    )

    # 3. Add spaces after question marks if not present
    clean_text = re.sub(r"\?\s*", "? ", clean_text)

    # Remove new lines and extra spaces
    clean_text = re.sub(r"\s+", " ", clean_text).strip()

    # 4. Convert to lowercase
    clean_text = clean_text.lower()

    return clean_text
