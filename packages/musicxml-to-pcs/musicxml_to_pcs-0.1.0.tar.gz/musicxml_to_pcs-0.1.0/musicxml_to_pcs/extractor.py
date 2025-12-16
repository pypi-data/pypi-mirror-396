"""
Core extraction logic for pitch class sets from MusicXML.
"""

from dataclasses import dataclass, field, asdict
from typing import List, Optional, Dict, Any
from collections import Counter
import json
import csv

from music21 import converter, harmony, note, chord as m21chord


@dataclass
class HarmonicSegment:
    """A segment of music under a single chord symbol."""
    
    measure: int
    beat: float
    chord_symbol: str
    chord_root: int
    chord_kind: str
    pitch_classes: List[int]
    interval_vector: List[int]
    forte_class: str
    prime_form: List[int]
    note_count: int
    notes: List[str] = field(default_factory=list)
    
    @property
    def interval_vector_string(self) -> str:
        """Interval vector as string, e.g., '(343230)'."""
        return "(" + "".join(str(x) for x in self.interval_vector) + ")"
    
    @property
    def pitch_class_set_string(self) -> str:
        """Pitch class set as string, e.g., '{0,1,2,3,5,10}'."""
        return "{" + ",".join(str(pc) for pc in self.pitch_classes) + "}"
    
    @property
    def prime_form_string(self) -> str:
        """Prime form as string, e.g., '<0,2,3,4,5,7>'."""
        return "<" + ",".join(str(x) for x in self.prime_form) + ">"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


class PCSExtractor:
    """
    Extract pitch class sets from MusicXML files segmented by chord changes.
    
    This class parses MusicXML files containing chord symbols and melody,
    segments the melody by chord changes, and computes pitch class set
    analysis for each segment including interval vectors and Forte classes.
    
    Attributes:
        filepath: Path to the MusicXML file
        score: Parsed music21 score object
        segments: List of extracted HarmonicSegment objects
    
    Example:
        >>> extractor = PCSExtractor('Anthropology.xml')
        >>> segments = extractor.extract()
        >>> for seg in segments[:5]:
        ...     print(f"{seg.chord_symbol}: {seg.forte_class} {seg.interval_vector_string}")
        F7: 1-1 (000000)
        B-: 6-8 (343230)
        Cm: 1-1 (000000)
        F7: 2-2 (010000)
        Dm: 2-1 (100000)
    """
    
    # Map chord kinds to simpler categories
    CHORD_KIND_MAP = {
        'major': 'maj',
        'minor': 'min',
        'dominant': 'dom',
        'dominant-seventh': 'dom7',
        'diminished': 'dim',
        'augmented': 'aug',
        'half-diminished': 'hdim',
        'major-seventh': 'maj7',
        'minor-seventh': 'min7',
        'diminished-seventh': 'dim7',
        'major-minor': 'mM7',
        'suspended-fourth': 'sus4',
        'suspended-second': 'sus2',
    }
    
    def __init__(self, filepath: str):
        """
        Initialize the extractor with a MusicXML file.
        
        Args:
            filepath: Path to MusicXML file
        """
        self.filepath = filepath
        self.score = None
        self.segments: List[HarmonicSegment] = []
        self._relative_to = None
        self._key_root = None
        self._min_cardinality = 1
        
    def parse(self) -> 'PCSExtractor':
        """
        Parse the MusicXML file.
        
        Returns:
            Self for method chaining
        """
        self.score = converter.parse(self.filepath)
        return self
    
    def extract(
        self, 
        include_notes: bool = False, 
        part_index: int = 0,
        relative_to: str = None,
        key_root: int = None,
        min_cardinality: int = 1
    ) -> List[HarmonicSegment]:
        """
        Extract pitch class sets for each chord segment.
        
        Args:
            include_notes: If True, include individual note names in output
            part_index: Index of the part to analyze (default: 0, first part)
            relative_to: How to calculate pitch classes:
                - None: Absolute (C=0, default)
                - 'chord_root': Relative to each chord's root (root=0)
                - 'key': Relative to the key/tonic (tonic=0)
            key_root: Pitch class of the key root (required if relative_to='key')
                      e.g., 10 for Bb, 0 for C, 7 for G
            min_cardinality: Minimum number of unique pitch classes to include
                             a segment (default: 1, use 2 to skip single notes,
                             3 to skip dyads, etc.)
            
        Returns:
            List of HarmonicSegment objects
        """
        if relative_to == 'key' and key_root is None:
            raise ValueError("key_root must be specified when relative_to='key'")
        
        if self.score is None:
            self.parse()
        
        self._relative_to = relative_to
        self._key_root = key_root
        self._min_cardinality = min_cardinality
            
        part = self.score.parts[part_index]
        measures = list(part.getElementsByClass('Measure'))
        
        # Build chord and note event lists
        chord_events = self._build_chord_events(measures)
        note_events = self._build_note_events(measures)
        
        # Segment notes by chords
        self.segments = self._segment_by_chords(chord_events, note_events, include_notes)
        
        return self.segments
    
    def _build_chord_events(self, measures) -> List[Dict]:
        """Build a sorted list of chord events with global offsets."""
        chord_events = []
        
        for m in measures:
            measure_offset = m.offset
            for cs in m.getElementsByClass(harmony.ChordSymbol):
                global_offset = measure_offset + cs.offset
                
                # Get chord root as pitch class
                root_pc = cs.root().pitchClass if cs.root() else 0
                
                # Get chord kind
                kind = cs.chordKind or 'major'
                kind_simple = self.CHORD_KIND_MAP.get(kind, kind)
                
                chord_events.append({
                    'offset': global_offset,
                    'measure': m.number,
                    'local_offset': cs.offset,
                    'chord': cs,
                    'root_pc': root_pc,
                    'kind': kind_simple
                })
        
        chord_events.sort(key=lambda x: x['offset'])
        return chord_events
    
    def _build_note_events(self, measures) -> List[Dict]:
        """Build a sorted list of note events with global offsets."""
        note_events = []
        
        for m in measures:
            measure_offset = m.offset
            for n in m.getElementsByClass(note.Note):
                global_offset = measure_offset + n.offset
                note_events.append({
                    'offset': global_offset,
                    'measure': m.number,
                    'note': n
                })
        
        note_events.sort(key=lambda x: x['offset'])
        return note_events
    
    def _segment_by_chords(
        self, 
        chord_events: List[Dict], 
        note_events: List[Dict],
        include_notes: bool
    ) -> List[HarmonicSegment]:
        """Assign notes to chord segments and compute pitch class sets."""
        segments = []
        
        for i, ce in enumerate(chord_events):
            start_offset = ce['offset']
            end_offset = chord_events[i + 1]['offset'] if i + 1 < len(chord_events) else float('inf')
            
            # Find notes in this range
            segment_notes = [
                ne['note'] for ne in note_events 
                if start_offset <= ne['offset'] < end_offset
            ]
            
            if not segment_notes:
                continue
            
            # Get absolute pitch classes
            absolute_pcs = [n.pitch.pitchClass for n in segment_notes]
            
            # Apply relative transformation if specified
            if self._relative_to == 'chord_root':
                reference = ce['root_pc']
                pitch_classes = sorted(set((pc - reference) % 12 for pc in absolute_pcs))
            elif self._relative_to == 'key':
                reference = self._key_root
                pitch_classes = sorted(set((pc - reference) % 12 for pc in absolute_pcs))
            else:
                pitch_classes = sorted(set(absolute_pcs))
            
            # Skip if below minimum cardinality
            if len(pitch_classes) < self._min_cardinality:
                continue
            
            # Compute interval vector and Forte class
            if len(pitch_classes) >= 2:
                temp_chord = m21chord.Chord(pitch_classes)
                interval_vector = temp_chord.intervalVector
                forte_class = temp_chord.forteClass
                prime_form = temp_chord.primeForm
            else:
                interval_vector = [0, 0, 0, 0, 0, 0]
                forte_class = "1-1" if len(pitch_classes) == 1 else "0-0"
                prime_form = pitch_classes
            
            segment = HarmonicSegment(
                measure=ce['measure'],
                beat=ce['local_offset'],
                chord_symbol=ce['chord'].figure,
                chord_root=ce['root_pc'],
                chord_kind=ce['kind'],
                pitch_classes=pitch_classes,
                interval_vector=interval_vector,
                forte_class=forte_class,
                prime_form=prime_form,
                note_count=len(segment_notes),
                notes=[n.nameWithOctave for n in segment_notes] if include_notes else []
            )
            segments.append(segment)
        
        return segments
    
    def to_json(self, filepath: Optional[str] = None, indent: int = 2) -> str:
        """
        Export segments to JSON format.
        
        Args:
            filepath: If provided, write to file
            indent: JSON indentation level
            
        Returns:
            JSON string
        """
        data = {
            'source_file': self.filepath,
            'total_segments': len(self.segments),
            'segments': [seg.to_dict() for seg in self.segments]
        }
        
        json_str = json.dumps(data, indent=indent)
        
        if filepath:
            with open(filepath, 'w') as f:
                f.write(json_str)
                
        return json_str
    
    def to_csv(self, filepath: str) -> None:
        """
        Export segments to CSV format.
        
        Args:
            filepath: Output file path
            
        Raises:
            ValueError: If no segments have been extracted
        """
        if not self.segments:
            raise ValueError("No segments to export. Run extract() first.")
            
        fieldnames = [
            'measure', 'beat', 'chord_symbol', 'chord_root', 'chord_kind',
            'pitch_classes', 'interval_vector', 'forte_class', 'prime_form', 'note_count'
        ]
        
        with open(filepath, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            
            for seg in self.segments:
                row = {
                    'measure': seg.measure,
                    'beat': seg.beat,
                    'chord_symbol': seg.chord_symbol,
                    'chord_root': seg.chord_root,
                    'chord_kind': seg.chord_kind,
                    'pitch_classes': seg.pitch_class_set_string,
                    'interval_vector': seg.interval_vector_string,
                    'forte_class': seg.forte_class,
                    'prime_form': seg.prime_form_string,
                    'note_count': seg.note_count
                }
                writer.writerow(row)
    
    def summary(self) -> Dict[str, Any]:
        """
        Generate summary statistics.
        
        Returns:
            Dictionary containing summary statistics including counts
            of unique Forte classes, interval vectors, and chords,
            plus top-10 lists of each.
        """
        if not self.segments:
            return {}
            
        forte_counts = Counter(seg.forte_class for seg in self.segments)
        iv_counts = Counter(seg.interval_vector_string for seg in self.segments)
        chord_counts = Counter(seg.chord_symbol for seg in self.segments)
        
        return {
            'total_segments': len(self.segments),
            'unique_forte_classes': len(forte_counts),
            'unique_interval_vectors': len(iv_counts),
            'unique_chords': len(chord_counts),
            'top_forte_classes': forte_counts.most_common(10),
            'top_interval_vectors': iv_counts.most_common(10),
            'top_chords': chord_counts.most_common(10)
        }
    
    def print_segments(self, limit: Optional[int] = None) -> None:
        """
        Pretty print segments to console.
        
        Args:
            limit: Maximum number of segments to print (None for all)
        """
        segments_to_print = self.segments[:limit] if limit else self.segments
        
        print(f"\n{'='*100}")
        print(f"PCS Analysis: {self.filepath}")
        print(f"Total segments: {len(self.segments)}")
        print(f"{'='*100}\n")
        
        for seg in segments_to_print:
            print(
                f"M{seg.measure:3d} beat {seg.beat:.1f} | "
                f"{seg.chord_symbol:8s} | "
                f"PC: {seg.pitch_class_set_string:20s} | "
                f"IV: {seg.interval_vector_string} | "
                f"Forte: {seg.forte_class:8s} | "
                f"PF: {seg.prime_form_string}"
            )
        
        if limit and len(self.segments) > limit:
            print(f"\n... and {len(self.segments) - limit} more segments")
