import json, os
from collections import defaultdict
from modules import preprocessor, enrichment
import google.generativeai as genai

DATA_DIR = "data"
OUTPUT_DIR = "output"

# Configure Gemini if API key available
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)


def get_text_from_json(data):
    """Extract text from multiple possible fields and merge them."""
    candidates = [
        "cleaned_text",
        "extracted_text",
        "caption",
        "detailed_description",
        "summary",
        "description",
    ]
    texts = []
    for field in candidates:
        if field in data and isinstance(data[field], str) and data[field].strip():
            texts.append(data[field].strip())
    return " ".join(texts).strip() if texts else ""


def process_file(filepath):
    """Enrich a single JSON document."""
    filename = os.path.basename(filepath)
    output_path = os.path.join(OUTPUT_DIR, filename)

    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)

    text = get_text_from_json(data)
    if not text:
        print(f"⚠️ No usable text found in {filename}, skipping.")
        return None

    text = preprocessor.clean_text(text)
    enriched = enrichment.enrich_with_gemini(text, data.get("filename", filename))

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(enriched, f, indent=2, ensure_ascii=False)

    print(f"✅ Processed: {filename} → {output_path}")
    return enriched


def build_entity_index(output_dir):
    """Scan all enriched JSON files and build an entity-to-documents mapping."""
    entity_index = defaultdict(set)
    docs = {}

    for file in os.listdir(output_dir):
        if not file.endswith(".json"):
            continue

        with open(os.path.join(output_dir, file), "r", encoding="utf-8") as f:
            data = json.load(f)

        doc_id = data.get("document_id", file)
        docs[doc_id] = data

        entities = data.get("entities", {})
        for category, values in entities.items():
            for v in values:
                norm = v.strip().lower()
                entity_index[norm].add(doc_id)

    return entity_index, docs


def clean_gemini_output(output: str) -> str:
    """Clean Gemini output to ensure valid JSON only."""
    raw_output = output.strip()

    if raw_output.startswith("```"):
        raw_output = raw_output.strip("`").replace("json", "").strip()

    if "[" in raw_output and "]" in raw_output:
        raw_output = raw_output[raw_output.find("["): raw_output.rfind("]") + 1]
    elif "{" in raw_output and "}" in raw_output:
        raw_output = raw_output[raw_output.find("{"): raw_output.rfind("}") + 1]

    return raw_output


def consolidate_entities_with_gemini(entities):
    """Ask Gemini to normalize entity variants (if API available)."""
    if not GEMINI_API_KEY:
        return entities

    model = genai.GenerativeModel("gemini-1.5-flash")
    prompt = f"""
    You are given a list of named entities from historical documents.
    - Merge duplicates and variants (e.g., "G. Rava" = "Giuseppe Rava").
    - Return a clean JSON list of unique entities.
    Entities: {entities}
    """

    try:
        response = model.generate_content(prompt)
        raw_output = clean_gemini_output(response.text)
        return json.loads(raw_output)
    except Exception as e:
        print(f"⚠️ Gemini consolidation failed: {e}")
        print(f"🔎 Gemini raw output:\n{response.text[:300]}...\n")
        return entities


def infer_complex_links_with_gemini(doc1, doc2):
    """Ask Gemini to infer relationships beyond same-entity matches."""
    if not GEMINI_API_KEY:
        return []

    model = genai.GenerativeModel("gemini-1.5-flash")
    prompt = f"""
    Compare these two documents. Only return a link if there is a **clear, meaningful relationship**
    such as same date, same event, or person-organization connection.
    Do NOT guess. If no valid relationship, return [].

    Return JSON in this format:
    [
      {{
        "related_document_id": "<doc_id>",
        "relation": "<relation_type>",
        "reason": "<why these documents are linked>"
      }}
    ]

    Document A (ID: {doc1['document_id']}):
    Entities: {doc1.get('entities', {})}
    Timeline: {doc1.get('timeline', [])}

    Document B (ID: {doc2['document_id']}):
    Entities: {doc2.get('entities', {})}
    Timeline: {doc2.get('timeline', [])}
    """

    try:
        response = model.generate_content(prompt)
        raw_output = clean_gemini_output(response.text)
        return json.loads(raw_output)
    except Exception as e:
        print(f"⚠️ Complex link inference JSON parse failed: {e}")
        print(f"🔎 Gemini raw output:\n{response.text[:300]}...\n")
        return []


def add_links(output_dir):
    """Add precise cross-document links into each enriched JSON file."""
    entity_index, docs = build_entity_index(output_dir)
    consolidate_entities_with_gemini(list(entity_index.keys()))

    for doc_id, data in docs.items():
        links = []

        for other_id, other_data in docs.items():
            if other_id == doc_id:
                continue

            reasons = []

            # Match on exact dates
            dates1 = set(data.get("entities", {}).get("dates", []))
            dates2 = set(other_data.get("entities", {}).get("dates", []))
            exact_dates = dates1 & dates2
            if exact_dates:
                reasons.append(f"Both documents mention the exact date(s): {', '.join(exact_dates)}")

            # Match on persons
            persons1 = set(data.get("entities", {}).get("persons", []))
            persons2 = set(other_data.get("entities", {}).get("persons", []))
            common_persons = persons1 & persons2
            if common_persons:
                reasons.append(f"Both documents mention the same person(s): {', '.join(common_persons)}")

            # Match on organizations
            orgs1 = set(data.get("entities", {}).get("organizations", []))
            orgs2 = set(other_data.get("entities", {}).get("organizations", []))
            common_orgs = orgs1 & orgs2
            if common_orgs:
                reasons.append(f"Both documents mention the same organization(s): {', '.join(common_orgs)}")

            # Build link only if strong reasons exist
            if reasons:
                links.append({
                    "related_document_id": other_id,
                    "relation": "strong_link",
                    "reason": reasons
                })

        data["links"] = links  # always include field

        output_path = os.path.join(output_dir, os.path.basename(doc_id))
        if not output_path.endswith(".json"):
            output_path = os.path.join(output_dir, os.path.basename(doc_id) + ".json")

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        if links:
            print(f"🔗 Added {len(links)} strong links for {doc_id}")
        else:
            print(f"ℹ️ No valid links found for {doc_id}")


if __name__ == "__main__":
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    files = [f for f in os.listdir(DATA_DIR) if f.endswith(".json")]
    print(f"📂 Found {len(files)} input files in {DATA_DIR}")
    for file in files:
        process_file(os.path.join(DATA_DIR, file))

    print("\n🔍 Running asset linkage and complex relationship inference...")
    add_links(OUTPUT_DIR)
    print("✅ Asset linkage complete.")
