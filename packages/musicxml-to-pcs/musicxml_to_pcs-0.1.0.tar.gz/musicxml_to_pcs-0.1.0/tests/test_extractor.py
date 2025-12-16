"""
Tests for pcs-extract.
"""

import pytest
from music21 import chord as m21chord

from musicxml_to_pcs import PCSExtractor, HarmonicSegment


class TestHarmonicSegment:
    """Tests for HarmonicSegment dataclass."""
    
    def test_interval_vector_string(self):
        seg = HarmonicSegment(
            measure=1,
            beat=0.0,
            chord_symbol="C",
            chord_root=0,
            chord_kind="maj",
            pitch_classes=[0, 4, 7],
            interval_vector=[0, 0, 1, 1, 1, 0],
            forte_class="3-11A",
            prime_form=[0, 3, 7],
            note_count=3
        )
        assert seg.interval_vector_string == "(001110)"
    
    def test_pitch_class_set_string(self):
        seg = HarmonicSegment(
            measure=1,
            beat=0.0,
            chord_symbol="C",
            chord_root=0,
            chord_kind="maj",
            pitch_classes=[0, 4, 7],
            interval_vector=[0, 0, 1, 1, 1, 0],
            forte_class="3-11A",
            prime_form=[0, 3, 7],
            note_count=3
        )
        assert seg.pitch_class_set_string == "{0,4,7}"
    
    def test_prime_form_string(self):
        seg = HarmonicSegment(
            measure=1,
            beat=0.0,
            chord_symbol="C",
            chord_root=0,
            chord_kind="maj",
            pitch_classes=[0, 4, 7],
            interval_vector=[0, 0, 1, 1, 1, 0],
            forte_class="3-11A",
            prime_form=[0, 3, 7],
            note_count=3
        )
        assert seg.prime_form_string == "<0,3,7>"
    
    def test_to_dict(self):
        seg = HarmonicSegment(
            measure=1,
            beat=0.0,
            chord_symbol="C",
            chord_root=0,
            chord_kind="maj",
            pitch_classes=[0, 4, 7],
            interval_vector=[0, 0, 1, 1, 1, 0],
            forte_class="3-11A",
            prime_form=[0, 3, 7],
            note_count=3
        )
        d = seg.to_dict()
        assert d['measure'] == 1
        assert d['chord_symbol'] == "C"
        assert d['pitch_classes'] == [0, 4, 7]


class TestIntervalVectorComputation:
    """Tests for interval vector computation via music21."""
    
    def test_major_triad(self):
        c = m21chord.Chord([0, 4, 7])
        assert c.intervalVector == [0, 0, 1, 1, 1, 0]
        assert c.forteClass == "3-11B"  # Major is B in music21
    
    def test_minor_triad(self):
        c = m21chord.Chord([0, 3, 7])
        assert c.intervalVector == [0, 0, 1, 1, 1, 0]
        assert c.forteClass == "3-11A"  # Minor is A in music21
    
    def test_diminished_triad(self):
        c = m21chord.Chord([0, 3, 6])
        assert c.intervalVector == [0, 0, 2, 0, 0, 1]
        assert c.forteClass == "3-10"
    
    def test_chromatic_cluster(self):
        c = m21chord.Chord([0, 1, 2])
        assert c.intervalVector == [2, 1, 0, 0, 0, 0]
        assert c.forteClass == "3-1"


class TestPCSExtractor:
    """Tests for PCSExtractor class."""
    
    def test_init(self):
        extractor = PCSExtractor('test.xml')
        assert extractor.filepath == 'test.xml'
        assert extractor.score is None
        assert extractor.segments == []
    
    def test_chord_kind_map(self):
        assert PCSExtractor.CHORD_KIND_MAP['major'] == 'maj'
        assert PCSExtractor.CHORD_KIND_MAP['minor'] == 'min'
        assert PCSExtractor.CHORD_KIND_MAP['dominant'] == 'dom'
