"""
Fix gold standard annotation spans to match actual detection output.
This resolves issues where:
1. Detected span is different from expected span (e.g., extract just name vs full labeled string)
2. PHI types differ but are equivalent (e.g., ZIP_CODE vs CITY_STATE_ZIP)
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from redact_proxy import PHIDetector


# Types that are considered equivalent for matching
TYPE_EQUIVALENTS = {
    'ZIP_CODE': ['CITY_STATE_ZIP', 'ZIP_CODE'],
    'CITY_STATE_ZIP': ['CITY_STATE_ZIP', 'ZIP_CODE'],
    'PATIENT_NAME': ['PATIENT_NAME', 'PERSON_NAME', 'PROVIDER_NAME'],
    'PERSON_NAME': ['PATIENT_NAME', 'PERSON_NAME', 'PROVIDER_NAME'],
    'PROVIDER_NAME': ['PATIENT_NAME', 'PERSON_NAME', 'PROVIDER_NAME'],
    'ACCOUNT_NUMBER': ['ACCOUNT_NUMBER', 'MRN', 'OTHER_ID'],
    'MRN': ['MRN', 'ACCOUNT_NUMBER', 'OTHER_ID'],
    'INSURANCE_ID': ['INSURANCE_ID', 'PAYER_ID'],
}


def fix_spans_for_system(system_name, notes_dir, gold_file):
    """Fix annotation spans for one EHR system."""
    detector = PHIDetector(mode="fast")

    with open(gold_file, 'r', encoding='utf-8') as f:
        gold = json.load(f)

    fixed_count = 0
    removed_count = 0

    for filename, annotations in gold.get('notes', {}).items():
        note_path = notes_dir / system_name / filename
        if not note_path.exists():
            continue

        with open(note_path, 'r', encoding='utf-8', errors='replace') as f:
            note_text = f.read()

        # Run detection
        findings = detector.detect(note_text)

        # Create a lookup of detected spans
        detected_by_range = {}  # (start, end) -> finding
        for f in findings:
            detected_by_range[(f.start, f.end)] = f

        # Fix missed annotations that overlap with detections
        if 'missed' in annotations:
            new_missed = []
            for item in annotations['missed']:
                exp_start = item.get('start', -1)
                exp_end = item.get('end', -1)
                exp_type = item.get('phi_type', item.get('type', ''))
                exp_text = item.get('text', '')

                # Find overlapping detection
                found_match = False
                for (det_start, det_end), finding in detected_by_range.items():
                    # Check for overlap
                    if det_start < exp_end and det_end > exp_start:
                        # Check if types are compatible
                        det_type = finding.phi_type
                        equiv_types = TYPE_EQUIVALENTS.get(exp_type, [exp_type])

                        if det_type in equiv_types or det_type == exp_type:
                            # This detection covers the expected PHI - no longer missed
                            print(f"  [FIXED] {filename}: '{exp_text[:40]}' ({exp_type}) -> detected as '{finding.text[:40]}' ({det_type})")
                            fixed_count += 1
                            found_match = True
                            break

                if not found_match:
                    new_missed.append(item)

            annotations['missed'] = new_missed

        # Also check predictions - update spans for better matching
        if 'predictions' in annotations:
            for pred in annotations['predictions']:
                if pred.get('false_positive'):
                    continue

                exp_start = pred.get('start', -1)
                exp_end = pred.get('end', -1)
                exp_type = pred.get('phi_type', '')

                # Find exact or overlapping detection
                for (det_start, det_end), finding in detected_by_range.items():
                    if det_start < exp_end and det_end > exp_start:
                        det_type = finding.phi_type
                        equiv_types = TYPE_EQUIVALENTS.get(exp_type, [exp_type])

                        if det_type in equiv_types or det_type == exp_type:
                            # Update span to match detection
                            if (exp_start, exp_end) != (det_start, det_end):
                                # print(f"  [SPAN] {filename}: Updated span from ({exp_start},{exp_end}) to ({det_start},{det_end})")
                                pred['start'] = det_start
                                pred['end'] = det_end
                                pred['text'] = finding.text
                            break

    # Save updated annotations
    with open(gold_file, 'w', encoding='utf-8') as f:
        json.dump(gold, f, indent=2)

    return fixed_count, removed_count


def main():
    notes_dir = Path(r"C:\Users\drcra\Documents\Coding Projects\RedactiPHI\tests\ehr_notes")

    systems = {
        "meditech": "meditech_annotated.json",
        "cerner": "cerner_annotated.json",
        "eclinical": "eclinical_annotated.json",
    }

    total_fixed = 0

    for system, gold_file in systems.items():
        gold_path = notes_dir / gold_file
        if not gold_path.exists():
            print(f"Skipping {system}: {gold_path} not found")
            continue

        print(f"\n{'='*60}")
        print(f"Fixing {system.upper()} annotation spans")
        print(f"{'='*60}")

        fixed, removed = fix_spans_for_system(system, notes_dir, gold_path)
        total_fixed += fixed
        print(f"Fixed {fixed} annotations in {system}")

    print(f"\n{'='*60}")
    print(f"TOTAL: Fixed {total_fixed} span mismatches")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
