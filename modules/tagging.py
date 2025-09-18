CATEGORIES = ["portrait", "factory", "contract", "interview", "sports",
              "urban development", "public works", "advertisement"]

def classify_tags(text: str, llm_output=None):
    """Assign categories, use LLM output if available, else fallback rules."""
    if llm_output:
        return llm_output
    tags = []
    if "market" in text.lower():
        tags.append("urban development")
    if "factory" in text.lower() or "industry" in text.lower():
        tags.append("factory")
    return tags
