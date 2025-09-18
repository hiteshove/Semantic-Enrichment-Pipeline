import json
import os
import google.generativeai as genai
from modules import ner, tagging, timeline_geo

# Configure Gemini client with your API key (must be set in environment)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise ValueError("❌ GEMINI_API_KEY is not set. Please export it as an environment variable.")

genai.configure(api_key=GEMINI_API_KEY)


def enrich_with_gemini(text: str, doc_id: str):
    """
    Try to enrich with Gemini. If it fails, fallback to spaCy + rules.
    Output schema:
    {
      "document_id": ...,
      "entities": { "persons": [], "organizations": [], "locations": [], "dates": [] },
      "tags": [],
      "timeline": [],
      "geolocations": [],
      "links": []
    }
    """
    try:
        # Use Gemini model (fast for structured extraction)
        model = genai.GenerativeModel("gemini-1.5-flash")

        prompt = f"""
        Extract structured metadata in strict JSON format from the following text.
        Schema:
        {{
          "entities": {{
            "persons": ["string"],
            "organizations": ["string"],
            "locations": ["string"],
            "dates": ["string"]
          }},
          "tags": ["string"],
          "timeline": [{{"event": "string", "date": "string"}}],
          "geolocations": [{{"place": "string", "coordinates": {{"lat": float, "lon": float}}}}],
          "links": [{{"related_document_id": "string", "relation": "string"}}]
        }}

        Text:
        {text}
        """

        response = model.generate_content(prompt)

        # Gemini may wrap JSON in markdown → extract clean JSON
        raw_output = response.text.strip()
        if raw_output.startswith("```"):
            raw_output = raw_output.strip("`").replace("json", "").strip()

        enriched = json.loads(raw_output)
        enriched["document_id"] = doc_id
        return enriched

    except Exception as e:
        print(f"⚠️ Gemini enrichment failed for {doc_id}: {e}")
        # ---- Fallback using spaCy + rules ----
        entities = ner.extract_entities(text)
        dates = timeline_geo.extract_dates(text)
        timeline = [{"event": "Event mentioned in text", "date": d} for d in dates]

        return {
            "document_id": doc_id,
            "entities": entities,
            "tags": tagging.classify_tags(text),
            "timeline": timeline,
            "geolocations": [],
            "links": [],
        }
