import pytest
from arabic_translator_tester import is_arabic_translation_successful, translate_arabic

def test_valid_arabic():
    assert is_arabic_translation_successful("مرحبا") == True

def test_translate_hello():
    result = translate_arabic("مرحبا بالعالم")
    assert "world" in result.lower()
