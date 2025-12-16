"""
Command-line interface for pcs-extract.
"""

import argparse
import sys

from .extractor import PCSExtractor


def main():
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(
        prog='musicxml-to-pcs',
        description='Extract pitch class sets from MusicXML files segmented by chord symbols'
    )
    
    parser.add_argument(
        'filepath',
        help='Path to MusicXML file'
    )
    
    parser.add_argument(
        '--json',
        metavar='FILE',
        help='Export results to JSON file'
    )
    
    parser.add_argument(
        '--csv',
        metavar='FILE',
        help='Export results to CSV file'
    )
    
    parser.add_argument(
        '--limit',
        type=int,
        default=20,
        help='Limit console output to N segments (default: 20, use 0 for all)'
    )
    
    parser.add_argument(
        '--include-notes',
        action='store_true',
        help='Include individual note names in output'
    )
    
    parser.add_argument(
        '--summary-only',
        action='store_true',
        help='Only print summary statistics'
    )
    
    parser.add_argument(
        '--part',
        type=int,
        default=0,
        help='Part index to analyze (default: 0)'
    )
    
    parser.add_argument(
        '--relative-to',
        choices=['chord_root', 'key'],
        default=None,
        help='Calculate pitch classes relative to chord root or key (default: absolute, C=0)'
    )
    
    parser.add_argument(
        '--key-root',
        type=int,
        metavar='PC',
        help='Pitch class of key root when using --relative-to=key (e.g., 10 for Bb, 0 for C)'
    )
    
    parser.add_argument(
        '--min-cardinality',
        type=int,
        default=1,
        metavar='N',
        help='Minimum pitch classes per segment (default: 1, use 2 to skip single notes, 3 to skip dyads)'
    )
    
    args = parser.parse_args()
    
    try:
        extractor = PCSExtractor(args.filepath)
        segments = extractor.extract(
            include_notes=args.include_notes,
            part_index=args.part,
            relative_to=args.relative_to,
            key_root=args.key_root,
            min_cardinality=args.min_cardinality
        )
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except FileNotFoundError:
        print(f"Error: File not found: {args.filepath}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error parsing file: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Handle exports
    if args.json:
        extractor.to_json(args.json)
        print(f"Exported to {args.json}")
    
    if args.csv:
        extractor.to_csv(args.csv)
        print(f"Exported to {args.csv}")
    
    # Console output
    if args.summary_only:
        summary = extractor.summary()
        print(f"\n=== Summary: {args.filepath} ===")
        print(f"Total segments: {summary['total_segments']}")
        print(f"Unique Forte classes: {summary['unique_forte_classes']}")
        print(f"Unique interval vectors: {summary['unique_interval_vectors']}")
        print(f"Unique chords: {summary['unique_chords']}")
        print(f"\nTop 10 Forte classes:")
        for fc, count in summary['top_forte_classes']:
            print(f"  {fc:10s}: {count:3d}")
        print(f"\nTop 10 interval vectors:")
        for iv, count in summary['top_interval_vectors']:
            print(f"  {iv}: {count:3d}")
    elif not args.json and not args.csv:
        # Print segments if no export specified
        limit = None if args.limit == 0 else args.limit
        extractor.print_segments(limit=limit)
        
        print("\n--- Summary ---")
        summary = extractor.summary()
        print(f"Unique Forte classes: {summary['unique_forte_classes']}")
        print(f"Top 5 Forte classes: {summary['top_forte_classes'][:5]}")


if __name__ == '__main__':
    main()
