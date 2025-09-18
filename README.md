<<<<<<< HEAD
# 📚 Semantic Enrichment Pipeline

This project implements a **Semantic Enrichment Pipeline** for processing historical and archival documents.  
It transforms raw JSON files (captions, transcripts, descriptions, OCR outputs) into **structured knowledge assets** with entities, tags, timelines, geolocations, and strong cross-document linkages.

---

## ✨ Features

### 1. Named Entity Recognition (NER)
- Extracts **persons, organizations, locations, and dates** from text.

### 2. Semantic Tagging
- Assigns **high-level categories** (e.g., factory, portrait, interview, contract, sports).

### 3. Timeline Extraction & Geolocation
- Identifies **temporal expressions** and **geographical references**.
- Normalizes dates (`YYYY-MM-DD`) and attaches coordinates where possible.

### 4. Asset Linkage
- Detects **connections across documents**:
  - Same person(s)
  - Same organization(s)
  - Same date(s)
- Produces **structured, explainable JSON links** with clear reasons.
- Example:
  ```json
  "links": [
    {
      "related_document_id": "1155_01_1929_0192_0006.json",
      "relation": "strong_link",
      "reason": [
        "Both documents mention the exact date(s): 1929-08-29",
        "Both documents mention the same person(s): Giuseppe Rava"
      ]
    }
  ]
=======
# Semantic-Enrichment-Pipeline
Semantic Enrichment Pipeline – A Python-based system that transforms raw archival data (captions, transcripts, OCR) into structured knowledge. Features NER, semantic tagging, timelines, geolocation, and strong cross-document linkages using Gemini LLM. Outputs enriched JSON + summary reports.
>>>>>>> 56b2229d62b6aec0ea1392b461af87cd2902bb59
