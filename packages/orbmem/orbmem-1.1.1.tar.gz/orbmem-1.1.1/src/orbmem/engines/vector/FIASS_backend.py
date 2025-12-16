# engines/vector/qdrant_backend.py
# FAISS fallback vector engine (no Qdrant required)

try:
    import faiss
except ImportError:
    raise ImportError(
        "FAISS is not installed. Install with: pip install faiss-cpu"
    )
import numpy as np
from typing import List, Dict, Any
from ...utils.logger import get_logger
from ...utils.embeddings import embed_text
from orbmem.utils.exceptions import DatabaseError

logger = get_logger(__name__)


class QdrantVectorBackend:
    """
    Lightweight FAISS-based vector engine.
    Behaves like Qdrant but stores vectors in-memory.
    Fully compatible with OCDB vector API.
    """

    def __init__(self, dim: int = 384):
        self.dim = dim

        # FAISS L2 index for similarity search
        self.index = faiss.IndexFlatL2(dim)

        # Store payloads manually
        self.payloads: List[Dict[str, Any]] = []

        logger.info("FAISS vector engine initialized (Qdrant replacement).")

    # ---------------------------------------------------------
    # Insert text into vector DB
    # ---------------------------------------------------------
    def add_text(self, text: str, payload: Dict[str, Any]):
        try:
            vector = np.array([embed_text(text)], dtype="float32")

            self.index.add(vector)
            self.payloads.append(payload)

            logger.info(f"Vector added for ID={payload.get('id')}")

        except Exception as e:
            logger.error(f"FAISS add_text error: {e}")
            raise DatabaseError(str(e))

    # ---------------------------------------------------------
    # Search for similar vectors
    # ---------------------------------------------------------
    def search(self, query: str, k: int = 5) -> List[Dict[str, Any]]:
        try:
            vector = np.array([embed_text(query)], dtype="float32")

            # If nothing stored yet
            if self.index.ntotal == 0:
                return []

            distances, indices = self.index.search(vector, k)

            results = []
            for dist, idx in zip(distances[0], indices[0]):
                if idx == -1:
                    continue

                results.append({
                    "score": float(dist),
                    "payload": self.payloads[idx]
                })

            return results

        except Exception as e:
            logger.error(f"FAISS search error: {e}")
            raise DatabaseError(str(e))
