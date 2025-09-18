from sentence_transformers import SentenceTransformer, util

model = SentenceTransformer("all-MiniLM-L6-v2")

def link_assets(texts):
    """Return relatedness scores between documents."""
    embeddings = model.encode(texts, convert_to_tensor=True)
    scores = util.cos_sim(embeddings, embeddings)
    return scores.tolist()
       






                                    