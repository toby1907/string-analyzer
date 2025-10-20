from fastapi import FastAPI, Depends, HTTPException, status, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import Optional, List

from . import models, schemas, crud, analyzers, natural_language
from .database import engine, get_db

# Create database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="String Analyzer Service",
    description="A powerful REST API for analyzing string properties",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "String Analyzer Service is running!"}

@app.post("/strings", response_model=schemas.StringAnalysisResponse, status_code=status.HTTP_201_CREATED)
def create_analyze_string(
    string_data: schemas.StringAnalysisCreate,
    db: Session = Depends(get_db)
):
    """Create and analyze a new string"""
    # Check if string already exists
    existing = crud.StringAnalysisCRUD.get_analysis_by_value(db, string_data.value)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="String already exists in the system"
        )
    
    # Analyze string
    properties = analyzers.StringAnalyzer.analyze_string(string_data.value)
    
    # Create analysis record
    analysis = crud.StringAnalysisCRUD.create_analysis(db, string_data.value, properties)
    
    return {
        "id": analysis.id,
        "value": analysis.value,
        "properties": {
            "length": analysis.length,
            "is_palindrome": analysis.is_palindrome,
            "unique_characters": analysis.unique_characters,
            "word_count": analysis.word_count,
            "sha256_hash": analysis.sha256_hash,
            "character_frequency_map": analysis.character_frequency_map
        },
        "created_at": analysis.created_at
    }


@app.get("/strings/filter-by-natural-language", response_model=schemas.NaturalLanguageResponse)
def filter_by_natural_language(
    query: str = Query(..., description="Natural language query string"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """Filter strings using natural language queries"""
    try:
        print(f"🎯 Received natural language query: '{query}'")
        
        filters = natural_language.NaturalLanguageParser.parse_query(query)
        
        print(f"🔍 Parsed filters: {filters}")
        
        if not natural_language.NaturalLanguageParser.validate_filters(filters):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Query parsed but resulted in conflicting filters"
            )
        
        # Check if we have any strings in the database at all
        total_strings = db.query(models.StringAnalysis).count()
        print(f"📊 Total strings in database: {total_strings}")
        
        if total_strings == 0:
            return {
                "data": [],
                "count": 0,
                "interpreted_query": {
                    "original": query,
                    "parsed_filters": filters,
                    "note": "No strings in database"
                }
            }
        
        analyses, total_count = crud.StringAnalysisCRUD.get_all_analyses(
            db=db,
            skip=skip,
            limit=limit,
            **filters
        )
        
        print(f"✅ Query executed. Found {total_count} matching strings")
        
        response_data = {
            "data": [
                {
                    "id": analysis.id,
                    "value": analysis.value,
                    "properties": {
                        "length": analysis.length,
                        "is_palindrome": analysis.is_palindrome,
                        "unique_characters": analysis.unique_characters,
                        "word_count": analysis.word_count,
                        "sha256_hash": analysis.sha256_hash,
                        "character_frequency_map": analysis.character_frequency_map
                    },
                    "created_at": analysis.created_at
                }
                for analysis in analyses
            ],
            "count": total_count,
            "interpreted_query": {
                "original": query,
                "parsed_filters": filters
            }
        }
        
        print(f"🎉 Returning {len(response_data['data'])} results")
        return response_data
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        print(f"❌ ERROR DETAILS:")
        print(f"   Error type: {type(e).__name__}")
        print(f"   Error message: {str(e)}")
        import traceback
        print(f"   Stack trace:")
        traceback.print_exc()
        
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unable to parse natural language query: {str(e)}"
        )
        
@app.get("/strings/{string_value}", response_model=schemas.StringAnalysisResponse)
def get_string(string_value: str, db: Session = Depends(get_db)):
    """Get analysis for a specific string"""
    analysis = crud.StringAnalysisCRUD.get_analysis_by_value(db, string_value)
    if not analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="String does not exist in the system"
        )
    
    return {
        "id": analysis.id,
        "value": analysis.value,
        "properties": {
            "length": analysis.length,
            "is_palindrome": analysis.is_palindrome,
            "unique_characters": analysis.unique_characters,
            "word_count": analysis.word_count,
            "sha256_hash": analysis.sha256_hash,
            "character_frequency_map": analysis.character_frequency_map
        },
        "created_at": analysis.created_at
    }

@app.get("/strings", response_model=schemas.StringListResponse)
def get_all_strings(
    is_palindrome: Optional[bool] = Query(None, description="Filter by palindrome status"),
    min_length: Optional[int] = Query(None, ge=0, description="Minimum string length"),
    max_length: Optional[int] = Query(None, ge=0, description="Maximum string length"),
    word_count: Optional[int] = Query(None, ge=0, description="Exact word count"),
    contains_character: Optional[str] = Query(None, min_length=1, max_length=1, description="Single character to search for"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """Get all strings with optional filtering"""
    # Validate min_length and max_length
    if min_length is not None and max_length is not None and min_length > max_length:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="min_length cannot be greater than max_length"
        )
    
    analyses, total_count = crud.StringAnalysisCRUD.get_all_analyses(
        db=db,
        skip=skip,
        limit=limit,
        is_palindrome=is_palindrome,
        min_length=min_length,
        max_length=max_length,
        word_count=word_count,
        contains_character=contains_character
    )
    
    filters_applied = {}
    if is_palindrome is not None:
        filters_applied['is_palindrome'] = is_palindrome
    if min_length is not None:
        filters_applied['min_length'] = min_length
    if max_length is not None:
        filters_applied['max_length'] = max_length
    if word_count is not None:
        filters_applied['word_count'] = word_count
    if contains_character is not None:
        filters_applied['contains_character'] = contains_character
    
    return {
        "data": [
            {
                "id": analysis.id,
                "value": analysis.value,
                "properties": {
                    "length": analysis.length,
                    "is_palindrome": analysis.is_palindrome,
                    "unique_characters": analysis.unique_characters,
                    "word_count": analysis.word_count,
                    "sha256_hash": analysis.sha256_hash,
                    "character_frequency_map": analysis.character_frequency_map
                },
                "created_at": analysis.created_at
            }
            for analysis in analyses
        ],
        "count": total_count,
        "filters_applied": filters_applied
    }


           
@app.delete("/strings/{string_value}", status_code=status.HTTP_204_NO_CONTENT)
def delete_string(string_value: str, db: Session = Depends(get_db)):
    """Delete a string analysis"""
    if not crud.StringAnalysisCRUD.delete_analysis(db, string_value):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="String does not exist in the system"
        )
    
    return None

@app.get("/health")
def health_check():
    return {"status": "healthy"}