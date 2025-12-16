# core/ocdb.py

from typing import Any, Optional, List
from .config import load_config
import os

# MEMORY ENGINE – SQLite backend (Postgres replacement)
from orbmem.engines.memory.postgres_backend import PostgresMemoryBackend

# VECTOR ENGINE – Qdrant with FAISS fallback
from orbmem.engines.vector.FIASS_backend import QdrantVectorBackend

# GRAPH ENGINE – Neo4j fallback to NetworkX
from orbmem.engines.graph.neo4j_backend import Neo4jGraphBackend

# SAFETY ENGINE – Auto-select backend
if os.getenv("MONGO_URL"):
    from orbmem.engines.safety.mongo_backend import MongoSafetyBackend as SafetyBackend
else:
    from orbmem.engines.safety.sqlite_safety_backend import SQLiteSafetyBackend as SafetyBackend
from orbmem.engines.safety.timeseries_backend import TimeSeriesSafetyBackend


class OCDB:
    """
    OCDB v1 – Unified cognitive engine for local and cloud-ready environments.

    FEATURES:
        - Memory Engine:
            → Lightweight SQLite backend (default)
            → No Redis, no Postgres
        - Vector Engine:
            → Qdrant client with FAISS fallback (no external server needed)
        - Graph Engine:
            → Neo4j fallback to NetworkX (always available)
        - Safety Engine:
            → Auto: MongoDB backend (if MONGO_URL is set)
            → Or SQLite safety backend (portable for Kaggle/Jupyter/Colab)
        - Timeseries Fingerprinting:
            → Stores severity levels of safety events
    """

    def graph_dump(self):
        return self.graph.export()


    def __init__(self):
        cfg = load_config()

        # -------------------------------
        # MEMORY ENGINE
        # -------------------------------
        self.memory = PostgresMemoryBackend()  # actually SQLite-based

        
        # -------------------------------
        # VECTOR ENGINE
        # -------------------------------
        self.vector = QdrantVectorBackend()

        # -------------------------------
        # GRAPH ENGINE
        # -------------------------------
        self.graph = Neo4jGraphBackend()

        # -------------------------------
        # SAFETY ENGINE (Auto)
        # -------------------------------
        self.safety_event_engine = SafetyBackend()
        self.safety_timeseries = TimeSeriesSafetyBackend()

    # =====================================================
    # MEMORY METHODS
    # =====================================================

    def memory_set(self, key: str, value: dict, session_id: str = None, ttl_seconds: int = None):
        return self.memory.set(key, value, session_id=session_id, ttl_seconds=ttl_seconds)

    def memory_get(self, key: str):
        return self.memory.get(key)

    def memory_keys(self) -> List[str]:
        return self.memory.keys()

    # =====================================================
    # VECTOR METHODS
    # =====================================================

    def vector_search(self, query: str, k: int = 5):
        return self.vector.search(query, k=k)

    # =====================================================
    # GRAPH METHODS
    # =====================================================

    def graph_add(self, node_id: str, content: str, parent: Optional[str] = None):
        return self.graph.add_node(node_id, content, parent)

    def graph_path(self, start: str, end: str):
        return self.graph.get_path(start, end)

    # =====================================================
    # SAFETY METHODS
    # =====================================================

    def safety_scan(self, text: str):
        events = self.safety_event_engine.scan(text)

        for evt in events:
            self.safety_timeseries.add_point(evt.tag, evt.severity)

        return [
            {
                "text": evt.text,
                "tag": evt.tag,
                "severity": evt.severity,
                "correction": evt.correction,
                "details": evt.details,
                "timestamp": evt.timestamp,
            }
            for evt in events
        ]
    # =====================================================
    # GRAPH DUMP
    # =====================================================
    def graph_dump(self):
        """
        Return a full export of the current reasoning graph.
        """
        return self.graph_engine.export()
