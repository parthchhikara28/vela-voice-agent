from pathlib import Path
import yaml
import chromadb
from sentence_transformers import SentenceTransformer

KB_DIR = Path(__file__).parent
DB_DIR = KB_DIR.parent.parent / "chroma_db"   # saved next to your project


def parse(path):
    """Split a page into its info block (front-matter) and its text."""
    text = path.read_text(encoding="utf-8")
    _, front, body = text.split("---", 2)
    return yaml.safe_load(front), body.strip()


def chunk(body, size=300, overlap=60):
    """Cut long text into overlapping pieces. Short pages stay as one piece."""
    words = body.split()
    if len(words) <= size:
        return [body]
    pieces, start = [], 0
    while start < len(words):
        pieces.append(" ".join(words[start:start + size]))
        start += size - overlap
    return pieces


def main():
    model = SentenceTransformer("all-MiniLM-L6-v2")
    client = chromadb.PersistentClient(path=str(DB_DIR))
    try:
        client.delete_collection("visa_kb")
    except Exception:
        pass
    col = client.create_collection("visa_kb", metadata={"hnsw:space": "cosine"})

    ids, docs, metas = [], [], []
    for path in sorted(KB_DIR.glob("kb-*.md")):
        meta, body = parse(path)
        for i, piece in enumerate(chunk(body)):
            ids.append(f"{meta['id']}#{i}")
            docs.append(f"{meta['title']}. {piece}")
            metas.append({
                "id": str(meta["id"]),
                "title": str(meta["title"]),
                "country": str(meta["country"]),
                "passport": str(meta["passport"]),
            })

    embeddings = model.encode(docs).tolist()
    col.add(ids=ids, documents=docs, embeddings=embeddings, metadatas=metas)
    print(f"Indexed {len(docs)} pieces from {len(set(m['id'] for m in metas))} pages.")


if __name__ == "__main__":
    main()