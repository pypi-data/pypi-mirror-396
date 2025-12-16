"""
Fix gold standard annotation errors where medication times/dosages
were incorrectly marked as FACILITY.
"""

import json
from pathlib import Path


def fix_facility_errors(gold_file):
    """Remove incorrectly annotated medication times from FACILITY."""
    with open(gold_file, 'r', encoding='utf-8') as f:
        gold = json.load(f)

    removed_count = 0

    for filename, annotations in gold.get('notes', {}).items():
        # Check missed array for incorrect FACILITY annotations
        if 'missed' in annotations:
            new_missed = []
            for item in annotations['missed']:
                text = item.get('text', '')
                phi_type = item.get('phi_type', item.get('type', ''))

                # Remove medication times incorrectly labeled as FACILITY
                # These are times like "1800", "600", "0600,1800" etc.
                if phi_type == 'FACILITY':
                    # Check if it's actually a time/dosage pattern
                    stripped = text.strip()
                    # Medication times: 1800, 600, 0600, 1200, etc.
                    if stripped.isdigit() and len(stripped) <= 4:
                        print(f"  - Removed '{text}' (FACILITY) from {filename} - medication time")
                        removed_count += 1
                        continue
                    # Partial facility names like "Northside" that are actually facility parts
                    # Keep these as they may be valid

                new_missed.append(item)

            annotations['missed'] = new_missed

        # Also check predictions
        if 'predictions' in annotations:
            for pred in annotations['predictions']:
                text = pred.get('text', '')
                phi_type = pred.get('phi_type', '')

                # Mark medication times as false positives if they were labeled FACILITY
                if phi_type == 'FACILITY' and not pred.get('false_positive'):
                    stripped = text.strip()
                    if stripped.isdigit() and len(stripped) <= 4:
                        pred['false_positive'] = True
                        print(f"  - Marked '{text}' (FACILITY) as false_positive in {filename}")
                        removed_count += 1

    with open(gold_file, 'w', encoding='utf-8') as f:
        json.dump(gold, f, indent=2)

    return removed_count


def main():
    notes_dir = Path(r"C:\Users\drcra\Documents\Coding Projects\RedactiPHI\tests\ehr_notes")

    systems = ["meditech_annotated.json", "cerner_annotated.json", "eclinical_annotated.json"]
    total_fixed = 0

    for gold_file in systems:
        gold_path = notes_dir / gold_file
        if gold_path.exists():
            print(f"\nFixing {gold_file}:")
            fixed = fix_facility_errors(gold_path)
            total_fixed += fixed

    print(f"\nTotal fixed: {total_fixed} incorrect FACILITY annotations")


if __name__ == "__main__":
    main()
