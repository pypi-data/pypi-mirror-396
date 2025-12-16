#!/usr/bin/env python3
"""Arabic to English translation tester using Argos Translate."""

from .translate import ensure_arabic_english, is_arabic_translation_successful, translate_arabic
import sys

def main():
    """CLI entrypoint for arabic-test command."""
    if len(sys.argv) < 2:
        print("Usage: arabic-test 'Arabic text'")
        sys.exit(1)
    
    text = sys.argv[1]
    result = translate_arabic(text)
    is_valid = is_arabic_translation_successful(text)
    print(f"Translation: {result}")
    print(f"Valid: {is_valid}")

if __name__ == "__main__":
    main()
