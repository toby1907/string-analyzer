from sqlalchemy import Column, String, Boolean, Integer, JSON, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
import uuid

Base = declarative_base()

class StringAnalysis(Base):
    __tablename__ = "string_analyses"
    
    id = Column(String, primary_key=True, index=True)
    value = Column(String, unique=True, index=True, nullable=False)
    length = Column(Integer, nullable=False)
    is_palindrome = Column(Boolean, nullable=False)
    unique_characters = Column(Integer, nullable=False)
    word_count = Column(Integer, nullable=False)
    sha256_hash = Column(String, unique=True, nullable=False)
    character_frequency_map = Column(JSON, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())