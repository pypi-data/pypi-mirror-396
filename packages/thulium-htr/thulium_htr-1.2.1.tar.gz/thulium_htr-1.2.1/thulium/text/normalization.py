# Copyright 2025 Thulium Authors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Text normalization utilities for Thulium HTR.

This module provides script-specific text normalization functions to
standardize recognized text output and ground truth labels.

Functions:
    normalize_text: Main normalization function with script-specific handling
    normalize_unicode: Unicode canonicalization (NFC/NFD)
    normalize_whitespace: Standardize whitespace and line breaks
    normalize_punctuation: Standardize punctuation marks

Script-specific normalizers:
    normalize_latin: Latin script normalization
    normalize_arabic: Arabic script normalization with diacritics handling
    normalize_cyrillic: Cyrillic script normalization
    normalize_cjk: CJK script normalization
"""

import unicodedata
import re
from typing import Optional, Dict, Callable
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class NormalizationConfig:
    """Configuration for text normalization.
    
    Attributes:
        unicode_form: Unicode normalization form ('NFC', 'NFD', 'NFKC', 'NFKD').
        lowercase: Convert to lowercase.
        strip_diacritics: Remove diacritical marks.
        normalize_whitespace: Standardize whitespace.
        normalize_punctuation: Standardize punctuation marks.
        remove_control_chars: Remove control characters.
        script_specific: Apply script-specific normalization.
    """
    unicode_form: str = "NFC"
    lowercase: bool = False
    strip_diacritics: bool = False
    normalize_whitespace: bool = True
    normalize_punctuation: bool = True
    remove_control_chars: bool = True
    script_specific: bool = True


def normalize_text(
    text: str,
    language: str = "en",
    config: Optional[NormalizationConfig] = None
) -> str:
    """
    Normalize text with language-specific handling.
    
    This function applies a series of normalization steps appropriate
    for the specified language, including Unicode canonicalization,
    whitespace handling, and script-specific transformations.
    
    Args:
        text: Input text to normalize.
        language: ISO 639-1 language code.
        config: Optional normalization configuration.
        
    Returns:
        Normalized text string.
        
    Example:
        >>> normalize_text("Hello  World", language="en")
        "Hello World"
        >>> normalize_text("cafe\u0301", language="fr")  # e + combining acute
        "cafe"  # NFC normalized
    """
    if not text:
        return ""
    
    config = config or NormalizationConfig()
    
    # Step 1: Unicode canonicalization
    text = normalize_unicode(text, form=config.unicode_form)
    
    # Step 2: Remove control characters
    if config.remove_control_chars:
        text = remove_control_characters(text)
    
    # Step 3: Normalize whitespace
    if config.normalize_whitespace:
        text = normalize_whitespace(text)
    
    # Step 4: Script-specific normalization
    if config.script_specific:
        script = _detect_script(language)
        normalizer = _get_script_normalizer(script)
        if normalizer:
            text = normalizer(text, language)
    
    # Step 5: Case normalization
    if config.lowercase:
        text = text.lower()
    
    # Step 6: Strip diacritics if requested
    if config.strip_diacritics:
        text = strip_diacritics(text)
    
    # Step 7: Normalize punctuation
    if config.normalize_punctuation:
        text = normalize_punctuation(text)
    
    return text


def normalize_unicode(text: str, form: str = "NFC") -> str:
    """
    Apply Unicode normalization.
    
    Forms:
        NFC: Canonical decomposition followed by canonical composition.
        NFD: Canonical decomposition.
        NFKC: Compatibility decomposition followed by canonical composition.
        NFKD: Compatibility decomposition.
    
    Args:
        text: Input text.
        form: Normalization form ('NFC', 'NFD', 'NFKC', 'NFKD').
        
    Returns:
        Unicode-normalized text.
    """
    if form not in ("NFC", "NFD", "NFKC", "NFKD"):
        logger.warning(f"Invalid Unicode form '{form}', using NFC")
        form = "NFC"
    return unicodedata.normalize(form, text)


def normalize_whitespace(text: str) -> str:
    """
    Normalize whitespace characters.
    
    - Collapses multiple spaces to single space
    - Converts various Unicode spaces to regular space
    - Strips leading and trailing whitespace
    - Normalizes line breaks
    
    Args:
        text: Input text.
        
    Returns:
        Text with normalized whitespace.
    """
    # Replace various Unicode whitespace with regular space
    whitespace_chars = [
        '\u00A0',  # Non-breaking space
        '\u2000',  # En quad
        '\u2001',  # Em quad
        '\u2002',  # En space
        '\u2003',  # Em space
        '\u2004',  # Three-per-em space
        '\u2005',  # Four-per-em space
        '\u2006',  # Six-per-em space
        '\u2007',  # Figure space
        '\u2008',  # Punctuation space
        '\u2009',  # Thin space
        '\u200A',  # Hair space
        '\u202F',  # Narrow no-break space
        '\u205F',  # Medium mathematical space
        '\u3000',  # Ideographic space
    ]
    
    for ws in whitespace_chars:
        text = text.replace(ws, ' ')
    
    # Normalize line breaks
    text = text.replace('\r\n', '\n').replace('\r', '\n')
    
    # Collapse multiple spaces
    text = re.sub(r' +', ' ', text)
    
    # Collapse multiple newlines
    text = re.sub(r'\n+', '\n', text)
    
    return text.strip()


def normalize_punctuation(text: str) -> str:
    """
    Normalize punctuation marks to standard ASCII equivalents.
    
    Converts typographic quotes, dashes, and other marks to
    their ASCII equivalents for consistency.
    
    Args:
        text: Input text.
        
    Returns:
        Text with normalized punctuation.
    """
    replacements = {
        # Quotes
        '\u2018': "'",   # Left single quotation mark
        '\u2019': "'",   # Right single quotation mark
        '\u201A': "'",   # Single low-9 quotation mark
        '\u201B': "'",   # Single high-reversed-9 quotation mark
        '\u201C': '"',   # Left double quotation mark
        '\u201D': '"',   # Right double quotation mark
        '\u201E': '"',   # Double low-9 quotation mark
        '\u201F': '"',   # Double high-reversed-9 quotation mark
        '\u00AB': '"',   # Left-pointing double angle quotation mark
        '\u00BB': '"',   # Right-pointing double angle quotation mark
        
        # Dashes
        '\u2010': '-',   # Hyphen
        '\u2011': '-',   # Non-breaking hyphen
        '\u2012': '-',   # Figure dash
        '\u2013': '-',   # En dash
        '\u2014': '-',   # Em dash
        '\u2015': '-',   # Horizontal bar
        
        # Ellipsis
        '\u2026': '...',  # Horizontal ellipsis
        
        # Other
        '\u00B7': '.',   # Middle dot
        '\u2022': '*',   # Bullet
    }
    
    for old, new in replacements.items():
        text = text.replace(old, new)
    
    return text


def remove_control_characters(text: str) -> str:
    """
    Remove control characters from text.
    
    Removes invisible control characters that may interfere with
    text processing while preserving common formatting like newlines.
    
    Args:
        text: Input text.
        
    Returns:
        Text with control characters removed.
    """
    # Keep common whitespace: space, tab, newline
    allowed = {'\n', '\t', ' '}
    return ''.join(
        char for char in text
        if char in allowed or unicodedata.category(char) not in ('Cc', 'Cf')
    )


def strip_diacritics(text: str) -> str:
    """
    Remove diacritical marks from text.
    
    Decomposes characters and removes combining diacritical marks,
    leaving only base characters.
    
    Args:
        text: Input text.
        
    Returns:
        Text without diacritical marks.
        
    Example:
        >>> strip_diacritics("cafe")
        "cafe"
    """
    # NFD decomposes characters
    nfd = unicodedata.normalize('NFD', text)
    # Remove combining marks (category Mn)
    return ''.join(char for char in nfd if unicodedata.category(char) != 'Mn')


# Script-specific normalizers

def normalize_latin(text: str, language: str = "en") -> str:
    """Normalize Latin script text."""
    # Language-specific handling
    if language == "de":
        # German: Handle eszett
        pass  # Keep as-is; eszett is valid
    elif language == "tr":
        # Turkish: Handle dotted/dotless i
        text = text.replace('I', 'I')  # Keep uppercase I distinct
    
    return text


def normalize_arabic(text: str, language: str = "ar") -> str:
    """
    Normalize Arabic script text.
    
    - Removes tatweel (kashida)
    - Normalizes alef variants
    - Optionally removes tashkeel (diacritics)
    """
    # Remove tatweel (Arabic elongation character)
    text = text.replace('\u0640', '')
    
    # Normalize alef variants to plain alef
    alef_variants = {
        '\u0622': '\u0627',  # Alef with madda above -> Alef
        '\u0623': '\u0627',  # Alef with hamza above -> Alef
        '\u0625': '\u0627',  # Alef with hamza below -> Alef
        '\u0671': '\u0627',  # Alef wasla -> Alef
    }
    for old, new in alef_variants.items():
        text = text.replace(old, new)
    
    # Remove tashkeel (Arabic diacritics)
    tashkeel = [
        '\u064B',  # Fathatan
        '\u064C',  # Dammatan
        '\u064D',  # Kasratan
        '\u064E',  # Fatha
        '\u064F',  # Damma
        '\u0650',  # Kasra
        '\u0651',  # Shadda
        '\u0652',  # Sukun
    ]
    for mark in tashkeel:
        text = text.replace(mark, '')
    
    return text


def normalize_cyrillic(text: str, language: str = "ru") -> str:
    """Normalize Cyrillic script text."""
    if language == "ru":
        # Russian: Normalize yo (optional)
        # Some texts use е instead of ё
        pass  # Keep distinct by default
    return text


def normalize_cjk(text: str, language: str = "zh") -> str:
    """
    Normalize CJK script text.
    
    - Converts full-width ASCII to half-width
    - Normalizes Chinese punctuation
    """
    # Full-width to half-width ASCII conversion
    result = []
    for char in text:
        code = ord(char)
        # Full-width ASCII range: 0xFF01-0xFF5E -> 0x0021-0x007E
        if 0xFF01 <= code <= 0xFF5E:
            result.append(chr(code - 0xFEE0))
        # Full-width space -> half-width space
        elif code == 0x3000:
            result.append(' ')
        else:
            result.append(char)
    
    return ''.join(result)


# Helper functions

def _detect_script(language: str) -> str:
    """Detect script type from language code."""
    script_map = {
        # Latin scripts
        'en': 'latin', 'de': 'latin', 'fr': 'latin', 'es': 'latin',
        'it': 'latin', 'pt': 'latin', 'nl': 'latin', 'sv': 'latin',
        'no': 'latin', 'da': 'latin', 'fi': 'latin', 'pl': 'latin',
        'cs': 'latin', 'hu': 'latin', 'ro': 'latin', 'tr': 'latin',
        'az': 'latin', 'lt': 'latin', 'lv': 'latin', 'et': 'latin',
        
        # Cyrillic scripts
        'ru': 'cyrillic', 'uk': 'cyrillic', 'bg': 'cyrillic',
        'sr': 'cyrillic', 'mk': 'cyrillic', 'be': 'cyrillic',
        
        # Arabic scripts
        'ar': 'arabic', 'fa': 'arabic', 'ur': 'arabic',
        
        # CJK scripts
        'zh': 'cjk', 'ja': 'cjk', 'ko': 'cjk',
        
        # Caucasus scripts
        'ka': 'georgian', 'hy': 'armenian',
    }
    return script_map.get(language, 'latin')


def _get_script_normalizer(script: str) -> Optional[Callable]:
    """Get normalizer function for script type."""
    normalizers = {
        'latin': normalize_latin,
        'arabic': normalize_arabic,
        'cyrillic': normalize_cyrillic,
        'cjk': normalize_cjk,
    }
    return normalizers.get(script)


# Module exports
__all__ = [
    'normalize_text',
    'normalize_unicode',
    'normalize_whitespace',
    'normalize_punctuation',
    'remove_control_characters',
    'strip_diacritics',
    'normalize_latin',
    'normalize_arabic',
    'normalize_cyrillic',
    'normalize_cjk',
    'NormalizationConfig',
]
