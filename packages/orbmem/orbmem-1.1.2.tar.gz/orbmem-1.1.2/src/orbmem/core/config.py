# core/config.py

import os
from dataclasses import dataclass
from typing import List, Optional

from dotenv import load_dotenv
from orbmem.utils.exceptions import ConfigError


# ===========================
# DATA CLASSES
# ===========================

@dataclass
class DatabaseConfig:
    postgres_url: str
    redis_url: Optional[str] = None
    mongo_url: Optional[str] = None
    neo4j_url: Optional[str] = None


@dataclass
class APIConfig:
    api_keys: List[str]
    debug: bool = False
    mode: str = "local"   # local | cloud


@dataclass
class OCDBConfig:
    db: DatabaseConfig
    api: APIConfig


# ===========================
# HELPERS
# ===========================

def _get_env(name: str, default: Optional[str] = None, required: bool = False) -> Optional[str]:
    """Fetch env variable with optional requirement."""
    value = os.getenv(name, default)

    # treat empty string as None
    if value is not None:
        value = value.strip()
        if value == "":
            value = None

    if required and not value:
        raise ConfigError(f"Missing required environment variable: {name}")

    return value


# ===========================
# MAIN CONFIG LOADER
# ===========================

def load_config() -> OCDBConfig:
    """
    Load ORBMEM configuration in a clean, portable, cloud-ready way.

    v1 Behavior:
        - SQLite-first defaults (no Postgres, no Redis, no Mongo required)
        - All DB URLs become optional
        - If OCDB_MODE=cloud → POSTGRES_URL & MONGO_URL become required
        - Works in Kaggle/Colab/VScode/Jupyter with zero env setup
    """

    # Reload .env safely (Windows compatible)
    load_dotenv(override=True)

    # ------------------------------------------------------------
    # MODE: local (default) or cloud
    # ------------------------------------------------------------
    mode = _get_env("OCDB_MODE", default="local").lower()
    if mode not in ("local", "cloud"):
        raise ConfigError("OCDB_MODE must be either 'local' or 'cloud'")

    # ------------------------------------------------------------
    # DATABASE CONFIGURATION
    # ------------------------------------------------------------

    # MEMORY ENGINE (SQLite fallback)
    postgres_url = _get_env(
        "POSTGRES_URL",
        required=(mode == "cloud")  # only required in cloud mode
    )

    if not postgres_url:
        # Local mode uses SQLite memory engine
        postgres_url = None

    # REDIS (disabled in v1, optional)
    redis_url = _get_env("REDIS_URL", required=False)

    # MONGO (Safety backend)
    mongo_url = _get_env(
        "MONGO_URL",
        required=(mode == "cloud")  # only required for safety cloud backend
    )

    # GRAPH ENGINE (Neo4j)
    neo4j_url = _get_env("NEO4J_URL", required=False)

    # ------------------------------------------------------------
    # API Keys (only required in cloud mode)
    # ------------------------------------------------------------
    raw_keys = _get_env(
        "OCDB_API_KEYS",
        required=(mode == "cloud")
    )

    api_keys = []
    if raw_keys:
        api_keys = [k.strip() for k in raw_keys.split(",") if k.strip()]

    # ------------------------------------------------------------
    # DEBUG MODE
    # ------------------------------------------------------------
    debug_raw = _get_env("OCDB_DEBUG", default="0")
    debug = debug_raw.lower() in ("1", "true", "yes", "y")

    # ------------------------------------------------------------
    # Build config dataclasses
    # ------------------------------------------------------------
    db_cfg = DatabaseConfig(
        postgres_url=postgres_url,
        redis_url=redis_url,
        mongo_url=mongo_url,
        neo4j_url=neo4j_url,
    )

    api_cfg = APIConfig(
        api_keys=api_keys,
        debug=debug,
        mode=mode,
    )

    # ------------------------------------------------------------
    # Debug output (pretty)
    # ------------------------------------------------------------
    print(f"🔧 OCDB_MODE: {mode}")
    print(f"🗄  Memory engine URL: {postgres_url}")
    print(f"🔐 API Keys loaded: {bool(api_keys)}")
    print(f"🧠 Mongo safety enabled: {bool(mongo_url)}")
    print(f"🔗 Neo4j enabled: {bool(neo4j_url)}")
    print(f"🐬 Redis enabled: {bool(redis_url)}")

    return OCDBConfig(db=db_cfg, api=api_cfg)

