"""
Remove incorrectly added street address annotations that were actually
clinical text (like "Result status", "Plan", etc).
Only keep real addresses.
"""

import json
from pathlib import Path


def cleanup_bad_addresses(gold_file):
    """Remove bad address annotations, keep only real addresses."""
    with open(gold_file, 'r', encoding='utf-8') as f:
        gold = json.load(f)

    removed_count = 0
    kept_count = 0

    # Real address patterns to keep
    real_address_markers = [
        'pinellas st', 'barry rd', 'pelican pl', 'oak manor ln',
        'johnson blvd', 'regency oaks', 'bough ave'
    ]

    for filename, annotations in gold.get('notes', {}).items():
        if 'missed' not in annotations:
            continue

        new_missed = []
        for item in annotations['missed']:
            phi_type = item.get('phi_type', item.get('type', ''))
            text = item.get('text', '').lower()
            reason = item.get('added_reason', '')

            # Only filter annotations added with "Real street address" reason
            if phi_type == 'STREET_ADDRESS' and reason == 'Real street address':
                # Check if it's a real address
                is_real = any(marker in text for marker in real_address_markers)

                if is_real:
                    new_missed.append(item)
                    kept_count += 1
                    print(f"  KEPT: '{item['text'][:50]}' in {filename}")
                else:
                    removed_count += 1
                    # Don't print every removal, too many
            else:
                new_missed.append(item)

        annotations['missed'] = new_missed

    with open(gold_file, 'w', encoding='utf-8') as f:
        json.dump(gold, f, indent=2)

    return removed_count, kept_count


def main():
    notes_dir = Path(r"C:\Users\drcra\Documents\Coding Projects\RedactiPHI\tests\ehr_notes")

    systems = ["meditech_annotated.json", "cerner_annotated.json", "eclinical_annotated.json"]
    total_removed = 0
    total_kept = 0

    for gold_file in systems:
        gold_path = notes_dir / gold_file
        if gold_path.exists():
            print(f"\nCleaning {gold_file}:")
            removed, kept = cleanup_bad_addresses(gold_path)
            total_removed += removed
            total_kept += kept
            print(f"  Removed: {removed}, Kept: {kept}")

    print(f"\nTotal removed: {total_removed} bad address annotations")
    print(f"Total kept: {total_kept} real address annotations")


if __name__ == "__main__":
    main()
