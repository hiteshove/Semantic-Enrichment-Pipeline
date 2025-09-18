import os

# Gemini (via Google AI Python SDK or OpenAI-like wrapper)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Choose model
PRIMARY_MODEL = "gemini-2.5-flash"
FALLBACK_MODEL = "sentence-transformers/all-MiniLM-L6-v2"  # open-source
