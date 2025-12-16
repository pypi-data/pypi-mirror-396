#!/usr/bin/env python3
"""
Arabic Translator Tester
Tests Arabic input by translating to English using Argos Translate.
CLI: arabic-test "Arabic text"
"""

__version__ = "0.1.0"
__author__ = "Taha Husain"
__license__ = "MIT"

# Import public API functions
from .translate import (
    ensure_arabic_english,
    test_arabic_translation,
    translate_arabic
)

# CLI entrypoint for `arabic-test` command
import sys
from argparse import ArgumentParser

def main():
    """CLI entrypoint - run with: arabic-test "Arabic text" """
    parser = ArgumentParser(description="Test Arabic text translation")
    parser.add_argument("text", help="Arabic text to test")
    parser.add_argument("--translate-only", action="store_true", 
                       help="Only show translation, no validation")
    
    args = parser.parse_args()
    
    try:
        # Test translation
        result = translate_arabic(args.text)
        is_valid = test_arabic_translation(args.text)
        
        print(f"Translation: {result}")
        if not args.translate_only:
            print(f"Valid Arabic: {is_valid}")
            print(f"Success: {'✅' if is_valid else '❌'}")
            
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
