# models/fingerprints.py

from sqlalchemy import Column, Integer, String, Float, TIMESTAMP
from sqlalchemy.sql import func
from orbmem.db.postgres import Base

class SafetyFingerprint(Base):
    __tablename__ = "safety_fingerprints"

    id = Column(Integer, primary_key=True)
    tag = Column(String, index=True, nullable=False)
    score = Column(Float, nullable=False)
    timestamp = Column(TIMESTAMP(timezone=True), server_default=func.now())
