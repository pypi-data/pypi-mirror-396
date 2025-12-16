"""
Add missing street address annotations to gold standard.
These are real addresses that should be detected.
"""

import json
import re
from pathlib import Path

def add_address_annotations(gold_file, notes_dir, system):
    """Add missing street address annotations."""
    with open(gold_file, 'r', encoding='utf-8') as f:
        gold = json.load(f)

    added_count = 0

    # Street address pattern to find
    address_pattern = re.compile(
        r'\b(\d+\s+[A-Z][A-Za-z]+(?:\s+[A-Z][A-Za-z]+)*\s+'
        r'(?:Street|St|Avenue|Ave|Boulevard|Blvd|Drive|Dr|Road|Rd|'
        r'Lane|Ln|Way|Court|Ct|Circle|Cir|Place|Pl|Parkway|Pkwy|'
        r'Highway|Hwy|Trail|Trl|Terrace|Ter))\.?',
        re.IGNORECASE
    )

    for filename, annotations in gold.get('notes', {}).items():
        note_path = notes_dir / system / filename
        if not note_path.exists():
            continue

        with open(note_path, 'r', encoding='utf-8', errors='replace') as f:
            note_text = f.read()

        # Get current expected spans
        expected_spans = set()
        for pred in annotations.get('predictions', []):
            if not pred.get('false_positive', False):
                expected_spans.add((pred['start'], pred['end']))
        for missed in annotations.get('missed', []):
            expected_spans.add((missed['start'], missed['end']))

        # Find addresses
        for match in address_pattern.finditer(note_text):
            span = (match.start(), match.end())
            if span not in expected_spans:
                # Check if this overlaps with an existing annotation
                overlaps = False
                for es, ee in expected_spans:
                    if match.start() < ee and match.end() > es:
                        overlaps = True
                        break

                if not overlaps:
                    if 'missed' not in annotations:
                        annotations['missed'] = []

                    new_entry = {
                        "text": match.group(),
                        "phi_type": "STREET_ADDRESS",
                        "start": match.start(),
                        "end": match.end(),
                        "type": "STREET_ADDRESS",
                        "added_reason": "Real street address"
                    }
                    annotations['missed'].append(new_entry)
                    expected_spans.add(span)
                    added_count += 1
                    print(f"  + {filename}: Added '{match.group()}' (STREET_ADDRESS)")

    with open(gold_file, 'w', encoding='utf-8') as f:
        json.dump(gold, f, indent=2)

    return added_count


def main():
    notes_dir = Path(r"C:\Users\drcra\Documents\Coding Projects\RedactiPHI\tests\ehr_notes")

    systems = {
        "meditech": "meditech_annotated.json",
        "cerner": "cerner_annotated.json",
        "eclinical": "eclinical_annotated.json",
    }

    total_added = 0

    for system, gold_file in systems.items():
        gold_path = notes_dir / gold_file
        if not gold_path.exists():
            continue

        print(f"\nAdding addresses to {system}:")
        added = add_address_annotations(gold_path, notes_dir, system)
        total_added += added

    print(f"\nTotal added: {total_added} street address annotations")


if __name__ == "__main__":
    main()
