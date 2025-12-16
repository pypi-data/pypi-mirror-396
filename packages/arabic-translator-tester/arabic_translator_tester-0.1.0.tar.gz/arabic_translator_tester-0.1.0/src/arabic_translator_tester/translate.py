"""Translation logic using Argos Translate."""

import argostranslate.package
import argostranslate.translate

def ensure_arabic_english():
    """Ensure Arabic->English package is installed."""
    argostranslate.package.update_package_index()
    available_packages = argostranslate.package.get_available_packages()
    package_to_install = next(
        (p for p in available_packages 
         if p.from_code == "ar" and p.to_code == "en"), None)
    if package_to_install:
        argostranslate.package.install_from_path(package_to_install.download())

def test_arabic_translation(text: str) -> bool:
    """Test if Arabic text translates successfully."""
    ensure_arabic_english()
    try:
        result = argostranslate.translate.translate(text, "ar", "en")
        return bool(result.strip()) and len(result) > 3
    except Exception:
        return False

def translate_arabic(text: str) -> str:
    """Translate Arabic text to English."""
    ensure_arabic_english()
    return argostranslate.translate.translate(text, "ar", "en")
