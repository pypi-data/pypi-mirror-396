"""
musicxml-to-pcs: Pitch Class Set Extraction from MusicXML
=========================================================

Extract pitch class sets and interval vectors from MusicXML files,
automatically segmented by chord symbols.

Example usage:
    >>> from musicxml_to_pcs import PCSExtractor
    >>> extractor = PCSExtractor('Anthropology.xml')
    >>> segments = extractor.extract()
    >>> for seg in segments[:5]:
    ...     print(f"{seg.chord_symbol}: {seg.forte_class}")
"""

from .extractor import PCSExtractor, HarmonicSegment

__version__ = "0.1.0"
__author__ = "Mike Rubini"
__email__ = "mike@flatnine.co"

__all__ = ["PCSExtractor", "HarmonicSegment"]
