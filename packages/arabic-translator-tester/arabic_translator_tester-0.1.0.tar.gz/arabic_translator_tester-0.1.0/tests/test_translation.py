import pytest
from arabic_translator_tester import test_arabic_translation, translate_arabic

def test_valid_arabic():
    assert test_arabic_translation("مرحبا") == True

def test_translate_hello():
    result = translate_arabic("مرحبا بالعالم")
    assert "hello" in result.lower()
