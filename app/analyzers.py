import hashlib
import re
from typing import Dict

class StringAnalyzer:
    @staticmethod
    def analyze_string(value: str) -> Dict:
        """Analyze string and compute all required properties"""
        value = value.strip()
        
        # Basic properties
        length = len(value)
        word_count = len(value.split()) if value else 0
        
        # Palindrome check (case-insensitive)
        cleaned = re.sub(r'[^a-zA-Z0-9]', '', value.lower())
        is_palindrome = cleaned == cleaned[::-1] if cleaned else True
        
        # Character frequency and unique characters
        char_freq: Dict[str, int] = {}
        for char in value:
            char_freq[char] = char_freq.get(char, 0) + 1
        unique_characters = len(char_freq)
        
        # SHA256 hash
        sha256_hash = hashlib.sha256(value.encode()).hexdigest()
        
        return {
            "length": length,
            "is_palindrome": is_palindrome,
            "unique_characters": unique_characters,
            "word_count": word_count,
            "sha256_hash": sha256_hash,
            "character_frequency_map": char_freq
        }
    
    @staticmethod
    def generate_id(value: str) -> str:
        """Generate unique ID using SHA256 hash"""
        return hashlib.sha256(value.encode()).hexdigest()