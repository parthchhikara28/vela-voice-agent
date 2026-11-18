import sys
from pathlib import Path
import chromadb
from sentence_transformers import SentenceTransformer

DB_DIR = Path(__file__).parent.parent.parent / "chroma_db"

question = " ".join(sys.argv[1:]) or "how long does a Schengen visa take for an Indian passport"

model = SentenceTransformer("all-MiniLM-L6-v2")
col = chromadb.PersistentClient(path=str(DB_DIR)).get_collection("visa_kb")
result = col.query(query_embeddings=model.encode([question]).tolist(), n_results=4)

print(f"\nQuestion: {question}\n")
for rank, (meta, dist) in enumerate(zip(result["metadatas"][0], result["distances"][0]), 1):
    print(f"{rank}. {meta['id']}  score={1 - dist:.2f}  {meta['title']}")