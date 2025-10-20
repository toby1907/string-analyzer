from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import List, Optional, Dict
from . import models, schemas

class StringAnalysisCRUD:
    @staticmethod
    def get_analysis_by_value(db: Session, value: str):
        return db.query(models.StringAnalysis).filter(models.StringAnalysis.value == value).first()
    
    @staticmethod
    def get_analysis_by_hash(db: Session, sha256_hash: str):
        return db.query(models.StringAnalysis).filter(models.StringAnalysis.sha256_hash == sha256_hash).first()
    
    @staticmethod
    def create_analysis(db: Session, value: str, properties: Dict):
        analysis_id = properties["sha256_hash"]
        db_analysis = models.StringAnalysis(
            id=analysis_id,
            value=value,
            length=properties["length"],
            is_palindrome=properties["is_palindrome"],
            unique_characters=properties["unique_characters"],
            word_count=properties["word_count"],
            sha256_hash=properties["sha256_hash"],
            character_frequency_map=properties["character_frequency_map"]
        )
        db.add(db_analysis)
        db.commit()
        db.refresh(db_analysis)
        return db_analysis
    
    @staticmethod
    def get_all_analyses(
        db: Session,
        skip: int = 0,
        limit: int = 100,
        is_palindrome: Optional[bool] = None,
        min_length: Optional[int] = None,
        max_length: Optional[int] = None,
        word_count: Optional[int] = None,
        contains_character: Optional[str] = None
    ):
        query = db.query(models.StringAnalysis)
        
        if is_palindrome is not None:
            query = query.filter(models.StringAnalysis.is_palindrome == is_palindrome)
        
        if min_length is not None:
            query = query.filter(models.StringAnalysis.length >= min_length)
            
        if max_length is not None:
            query = query.filter(models.StringAnalysis.length <= max_length)
            
        if word_count is not None:
            query = query.filter(models.StringAnalysis.word_count == word_count)
            
        if contains_character is not None and len(contains_character) == 1:
            query = query.filter(
                models.StringAnalysis.character_frequency_map[contains_character].astext.cast(Integer) > 0
            )
        
        total_count = query.count()
        analyses = query.offset(skip).limit(limit).all()
        
        return analyses, total_count
    
    @staticmethod
    def delete_analysis(db: Session, value: str):
        analysis = db.query(models.StringAnalysis).filter(models.StringAnalysis.value == value).first()
        if analysis:
            db.delete(analysis)
            db.commit()
            return True
        return False