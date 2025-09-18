import re

def clean_text(text: str) -> str:
    """Basic text normalization."""
    if not isinstance(text, str):
        return ""
    # Collapse multiple spaces/newlines into one space
    text = re.sub(r"\s+", " ", text)
    return text.strip()
