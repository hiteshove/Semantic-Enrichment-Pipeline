import spacy

nlp = spacy.load("en_core_web_sm")

def extract_entities(text: str):
    """Extract entities using spaCy (backup if Gemini fails)."""
    doc = nlp(text)
    entities = {
        "persons": [ent.text for ent in doc.ents if ent.label_ == "PERSON"],
        "organizations": [ent.text for ent in doc.ents if ent.label_ == "ORG"],
        "locations": [ent.text for ent in doc.ents if ent.label_ in ["GPE","LOC"]],
        "dates": [ent.text for ent in doc.ents if ent.label_ == "DATE"],
    }
    return entities
