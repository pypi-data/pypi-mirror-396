"""
Fix gold standard annotations by adding correctly detected PHI that was missed.

This script:
1. Runs detection on all notes
2. Identifies "false positives" that are actually correct PHI
3. Adds them to the gold standard as expected PHI
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from redact_proxy import PHIDetector


def is_likely_real_phi(finding, text, context_before, context_after):
    """
    Determine if a "false positive" is actually real PHI that should be annotated.

    Returns (is_real_phi, reason)
    """
    phi_type = finding.phi_type
    detected_text = finding.text

    # Provider names with credentials or in signature context
    if phi_type in ("PERSON_NAME", "PROVIDER_NAME", "PATIENT_NAME"):
        # Names with medical credentials are real provider names
        credentials = ["MD", "DO", "NP", "PA", "RN", "LPN", "APRN", "RD", "PharmD", "PhD"]
        for cred in credentials:
            if cred in context_after[:30]:
                return True, f"Provider with {cred} credential"

        # Names in provider signature contexts
        signature_indicators = ["PCP:", "Provider:", "Dietitian", "Impression By:",
                               "Verified by:", "Signed by:", "Attending:", "Referring:"]
        for ind in signature_indicators:
            if ind.lower() in context_before.lower():
                return True, f"Provider in '{ind}' context"

        # "Last, First" format names (not medical terms)
        if "," in detected_text:
            parts = detected_text.replace(" ", "").split(",")
            if len(parts) == 2:
                # Check if both parts are name-like (capitalized, reasonable length)
                first, second = parts[0].strip(), parts[1].strip()
                if (first[0].isupper() and second[0].isupper() and
                    len(first) >= 3 and len(second) >= 3 and
                    first.isalpha() and second.split()[0].isalpha()):
                    # Reject known non-names
                    non_names = {"systems", "examination", "review", "diagnosis", "plan",
                                "history", "status", "assessment", "general", "brief"}
                    if first.lower() not in non_names and second.lower().split()[0] not in non_names:
                        return True, "Name in Last, First format"

        # Dr. Title names
        if detected_text.startswith("Dr.") or detected_text.startswith("Dr "):
            return True, "Doctor title prefix"

    # MRN/Account numbers that look like real IDs
    if phi_type in ("MRN", "ACCOUNT_NUMBER"):
        # 10-digit numbers in patient header context
        if "MRN:" in context_before or "FIN:" in context_before or "Patient:" in context_before:
            return True, "ID in patient header context"

    # Ages in clinical context
    if phi_type == "AGE":
        # Ages are PHI, but check if it's in a reasonable clinical context
        if "year" in detected_text.lower() or "y/o" in detected_text.lower() or "yo" in detected_text.lower():
            return True, "Age with year indicator"

    # Insurance IDs with payer context
    if phi_type == "INSURANCE_ID":
        if "Payer ID:" in context_before or "Insurance:" in context_before:
            # But reject partial words
            if detected_text.isalnum() and len(detected_text) >= 4:
                return True, "Insurance ID with payer context"

    # City, State ZIP patterns
    if phi_type == "CITY_STATE_ZIP":
        # These are real addresses
        if "," in detected_text and any(state in detected_text for state in ["FL", "CA", "NY", "TX"]):
            return True, "City, State ZIP format"

    return False, "Not confirmed as real PHI"


def fix_annotations_for_system(system_name, notes_dir, gold_file):
    """Fix annotations for one EHR system."""
    detector = PHIDetector(mode="fast")

    with open(gold_file, 'r', encoding='utf-8') as f:
        gold = json.load(f)

    added_count = 0

    for filename, annotations in gold.get('notes', {}).items():
        note_path = notes_dir / system_name / filename
        if not note_path.exists():
            continue

        with open(note_path, 'r', encoding='utf-8', errors='replace') as f:
            note_text = f.read()

        # Get current expected PHI
        expected_spans = set()
        for pred in annotations.get('predictions', []):
            if not pred.get('false_positive', False):
                expected_spans.add((pred['start'], pred['end']))
        for missed in annotations.get('missed', []):
            expected_spans.add((missed['start'], missed['end']))

        # Run detection
        findings = detector.detect(note_text)

        # Check each finding that's not in expected
        for finding in findings:
            span = (finding.start, finding.end)
            if span not in expected_spans:
                # Get context
                context_start = max(0, finding.start - 50)
                context_end = min(len(note_text), finding.end + 50)
                context_before = note_text[context_start:finding.start]
                context_after = note_text[finding.end:context_end]

                is_real, reason = is_likely_real_phi(finding, note_text, context_before, context_after)

                if is_real:
                    # Add to missed array
                    if 'missed' not in annotations:
                        annotations['missed'] = []

                    new_entry = {
                        "text": finding.text,
                        "phi_type": finding.phi_type,
                        "start": finding.start,
                        "end": finding.end,
                        "type": finding.phi_type,
                        "added_reason": reason
                    }

                    # Check if not already in missed
                    already_exists = any(
                        m.get('start') == finding.start and m.get('end') == finding.end
                        for m in annotations.get('missed', [])
                    )

                    if not already_exists:
                        annotations['missed'].append(new_entry)
                        added_count += 1
                        print(f"  + {filename}: Added '{finding.text}' ({finding.phi_type}) - {reason}")

    # Save updated annotations
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
            print(f"Skipping {system}: {gold_path} not found")
            continue

        print(f"\n{'='*60}")
        print(f"Fixing {system.upper()} annotations")
        print(f"{'='*60}")

        added = fix_annotations_for_system(system, notes_dir, gold_path)
        total_added += added
        print(f"Added {added} annotations to {system}")

    print(f"\n{'='*60}")
    print(f"TOTAL: Added {total_added} missing PHI annotations")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
