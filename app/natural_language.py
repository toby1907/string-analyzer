import re
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)

class NaturalLanguageParser:
    @staticmethod
    def parse_query(query: str) -> Dict[str, any]:
        """Parse natural language query into filter parameters"""
        query = query.strip()
        filters = {}
        
        logger.info(f"🔍 Parsing natural language query: '{query}'")
        
        # Check if this is a direct string search (not a natural language command)
        # If it's a single word without natural language keywords, treat as contains search
        if NaturalLanguageParser._is_direct_string_search(query):
            filters['contains_text'] = query
            logger.info(f"📝 Treating as direct string search for: '{query}'")
            return filters
        
        query_lower = query.lower()
        
        # Parse word count with more patterns
        word_count_patterns = [
            (r'\bsingle\s+word\b|\bone\s+word\b', 1),
            (r'\btwo\s+words\b|\bdouble\s+word\b', 2),
            (r'\bthree\s+words\b|\btriple\s+word\b', 3),
            (r'\b(\d+)\s+words?\b', None),  # Capture any number
        ]
        
        for pattern, count in word_count_patterns:
            match = re.search(pattern, query_lower)
            if match:
                if count is not None:
                    filters['word_count'] = count
                else:
                    # For the generic pattern, use the captured number
                    filters['word_count'] = int(match.group(1))
                logger.info(f"📝 Detected word_count: {filters['word_count']}")
                break
        
        # Parse palindrome with more patterns
        palindrome_patterns = [
            r'\bpalindrom',
            r'\bsame\s+forwards\s+and\s+backwards',
            r'\breads\s+same\s+both\s+ways',
        ]
        
        for pattern in palindrome_patterns:
            if re.search(pattern, query_lower):
                filters['is_palindrome'] = True
                logger.info("📝 Detected is_palindrome: True")
                break
        
        # Parse length filters
        longer_match = re.search(r'\blonger\s+than\s+(\d+)\s+characters?\b', query_lower)
        if longer_match:
            filters['min_length'] = int(longer_match.group(1)) + 1
            logger.info(f"📝 Detected min_length: {filters['min_length']}")
        
        shorter_match = re.search(r'\bshorter\s+than\s+(\d+)\s+characters?\b', query_lower)
        if shorter_match:
            filters['max_length'] = int(shorter_match.group(1)) - 1
            logger.info(f"📝 Detected max_length: {filters['max_length']}")
        
        # Exact length match
        length_match = re.search(r'\b(\d+)\s+characters?\b', query_lower)
        if length_match and 'min_length' not in filters and 'max_length' not in filters:
            length_val = int(length_match.group(1))
            filters['min_length'] = length_val
            filters['max_length'] = length_val
            logger.info(f"📝 Detected exact length: {length_val}")
        
        # Parse character containment with more patterns
        char_patterns = [
            r'\bcontain(s|ing)?\s+(?:the\s+)?(?:letter\s+)?([a-zA-Z])\b',
            r'\bwith\s+(?:the\s+)?(?:letter\s+)?([a-zA-Z])\b',
            r'\bhas\s+(?:the\s+)?(?:letter\s+)?([a-zA-Z])\b',
            r'\bincluding\s+(?:the\s+)?(?:letter\s+)?([a-zA-Z])\b',
        ]
        
        for pattern in char_patterns:
            char_match = re.search(pattern, query_lower)
            if char_match:
                # Get the character from the appropriate group
                char = char_match.group(1) if 'with' in pattern or 'has' in pattern or 'including' in pattern else char_match.group(2)
                filters['contains_character'] = char.lower()
                logger.info(f"📝 Detected contains_character: '{filters['contains_character']}'")
                break
        
        # Parse vowel specifically
        vowel_match = re.search(r'\b(first\s+)?vowel\b', query_lower)
        if vowel_match:
            filters['contains_character'] = 'a'
            logger.info("📝 Detected vowel, using contains_character: 'a'")
        
        # Parse text content search
        text_match = re.search(r'\b(?:containing|with|has)\s+(?:the\s+)?(?:text|string)\s+["\']?([^"\']+)["\']?', query_lower)
        if text_match:
            filters['contains_text'] = text_match.group(1)
            logger.info(f"📝 Detected contains_text: '{filters['contains_text']}'")
        
        logger.info(f"🎯 Final filters: {filters}")
        return filters
    
    @staticmethod
    def _is_direct_string_search(query: str) -> bool:
        """Check if the query is a direct string search rather than a natural language command"""
        # If it's a single word and doesn't contain natural language keywords
        natural_language_keywords = [
            'all', 'string', 'strings', 'contain', 'with', 'has', 'longer', 'shorter',
            'word', 'words', 'character', 'characters', 'palindrom', 'vowel', 'letter'
        ]
        
        # Single word without spaces and not a natural language keyword
        if ' ' not in query and query.lower() not in natural_language_keywords:
            return True
        
        return False
    
    @staticmethod
    def validate_filters(filters: Dict) -> bool:
        """Validate that filters don't conflict"""
        if 'min_length' in filters and 'max_length' in filters:
            if filters['min_length'] > filters['max_length']:
                logger.error(f"❌ Filter conflict: min_length {filters['min_length']} > max_length {filters['max_length']}")
                return False
        logger.info("✅ Filters validated successfully")
        return True