from pathlib import Path
import chromadb
from sentence_transformers import SentenceTransformer

DB_DIR = Path(__file__).resolve().parents[2] / "chroma_db"
_model = None
_col = None


def _load():
    """Load the search model once, the first time it is needed."""
    global _model, _col
    if _model is None:
        _model = SentenceTransformer("all-MiniLM-L6-v2")
        _col = chromadb.PersistentClient(path=str(DB_DIR)).get_collection("visa_kb")


def search(query, country=None, k=4):
    """Return the k best notebook pieces for a question."""
    _load()
    if country:
        query = f"{country} {query}"
    result = _col.query(query_embeddings=_model.encode([query]).tolist(), n_results=k)
    pieces = []
    for meta, doc, dist in zip(result["metadatas"][0], result["documents"][0], result["distances"][0]):
        pieces.append({"id": meta["id"], "title": meta["title"],
                       "text": doc, "score": round(1 - dist, 3)})
    return pieces