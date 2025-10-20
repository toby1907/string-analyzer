import re
from typing import Dict, Optional

class NaturalLanguageParser:
    @staticmethod
    def parse_query(query: str) -> Dict[str, any]:
        """Parse natural language query into filter parameters"""
        query = query.lower().strip()
        filters = {}
        
        # Parse word count
        if re.search(r'\bsingle\s+word\b|\bone\s+word\b', query):
            filters['word_count'] = 1
        elif re.search(r'\btwo\s+words\b|\bdouble\s+word\b', query):
            filters['word_count'] = 2
        elif re.search(r'\bthree\s+words\b|\btriple\s+word\b', query):
            filters['word_count'] = 3
            
        # Parse palindrome
        if re.search(r'\bpalindrom', query):
            filters['is_palindrome'] = True
            
        # Parse length filters
        longer_match = re.search(r'\blonger\s+than\s+(\d+)\s+characters?\b', query)
        if longer_match:
            filters['min_length'] = int(longer_match.group(1)) + 1
            
        shorter_match = re.search(r'\bshorter\s+than\s+(\d+)\s+characters?\b', query)
        if shorter_match:
            filters['max_length'] = int(shorter_match.group(1)) - 1
            
        length_match = re.search(r'\b(\d+)\s+characters?\b', query)
        if length_match and 'min_length' not in filters and 'max_length' not in filters:
            length_val = int(length_match.group(1))
            filters['min_length'] = length_val
            filters['max_length'] = length_val
            
        # Parse character containment
        char_match = re.search(r'\bcontain(s|ing)?\s+(?:the\s+)?(?:letter\s+)?([a-zA-Z])\b', query)
        if char_match:
            filters['contains_character'] = char_match.group(2).lower()
            
        # Parse vowel specifically
        vowel_match = re.search(r'\b(first\s+)?vowel\b', query)
        if vowel_match:
            filters['contains_character'] = 'a'
            
        return filters
    
    @staticmethod
    def validate_filters(filters: Dict) -> bool:
        """Validate that filters don't conflict"""
        if 'min_length' in filters and 'max_length' in filters:
            if filters['min_length'] > filters['max_length']:
                return False
        return True