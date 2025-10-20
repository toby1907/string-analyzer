from pydantic import BaseModel, Field
from typing import Dict, Optional, Any
from datetime import datetime

class StringProperties(BaseModel):
    length: int
    is_palindrome: bool
    unique_characters: int
    word_count: int
    sha256_hash: str
    character_frequency_map: Dict[str, int]

class StringAnalysisCreate(BaseModel):
    value: str = Field(..., min_length=1, max_length=10000)

class StringAnalysisResponse(BaseModel):
    id: str
    value: str
    properties: StringProperties
    created_at: datetime

class StringListResponse(BaseModel):
    data: list[StringAnalysisResponse]
    count: int
    filters_applied: Dict[str, Any]

class NaturalLanguageQuery(BaseModel):
    query: str = Field(..., min_length=1, max_length=500)

class NaturalLanguageResponse(BaseModel):
    data: list[StringAnalysisResponse]
    count: int
    interpreted_query: Dict[str, Any]