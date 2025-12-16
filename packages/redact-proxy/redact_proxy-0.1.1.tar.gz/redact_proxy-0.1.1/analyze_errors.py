"""
Analyze false positives and false negatives from EHR evaluation.
"""

import json
import sys
from pathlib import Path
from collections import defaultdict

sys.path.insert(0, str(Path(__file__).parent))

from redact_proxy import PHIDetector


def analyze_note(detector, note_path, annotations):
    """Analyze errors for a single note."""
    with open(note_path, 'r', encoding='utf-8', errors='replace') as f:
        note_text = f.read()

    # Get expected PHI
    expected_phi = set()
    expected_details = {}
    for pred in annotations.get('predictions', []):
        if not pred.get('false_positive', False):
            key = (pred['start'], pred['end'])
            expected_phi.add(key)
            expected_details[key] = pred

    for missed in annotations.get('missed', []):
        key = (missed['start'], missed['end'])
        expected_phi.add(key)
        expected_details[key] = missed

    # Run detection
    findings = detector.detect(note_text)
    detected = {(f.start, f.end): f for f in findings}
    detected_set = set(detected.keys())

    # Calculate errors
    true_positives = detected_set & expected_phi
    false_positives = detected_set - expected_phi
    false_negatives = expected_phi - detected_set

    fp_details = []
    for span in false_positives:
        f = detected[span]
        context_start = max(0, span[0] - 30)
        context_end = min(len(note_text), span[1] + 30)
        context = note_text[context_start:context_end].replace('\n', ' ')
        fp_details.append({
            'text': f.text,
            'type': f.phi_type,
            'context': f"...{context}...",
            'span': span
        })

    fn_details = []
    for span in false_negatives:
        detail = expected_details.get(span, {})
        text = note_text[span[0]:span[1]]
        context_start = max(0, span[0] - 30)
        context_end = min(len(note_text), span[1] + 30)
        context = note_text[context_start:context_end].replace('\n', ' ')
        fn_details.append({
            'text': text,
            'expected_type': detail.get('phi_type', detail.get('type', 'UNKNOWN')),
            'context': f"...{context}...",
            'span': span
        })

    return {
        'tp': len(true_positives),
        'fp': len(false_positives),
        'fn': len(false_negatives),
        'fp_details': fp_details,
        'fn_details': fn_details
    }


def main():
    notes_dir = Path(r"C:\Users\drcra\Documents\Coding Projects\RedactiPHI\tests\ehr_notes")
    detector = PHIDetector(mode="fast")

    systems = {
        "meditech": "meditech_annotated.json",
        "cerner": "cerner_annotated.json",
        "eclinical": "eclinical_annotated.json",
    }

    all_fp = defaultdict(list)
    all_fn = defaultdict(list)
    total_tp = 0
    total_fp = 0
    total_fn = 0

    for system, gold_file in systems.items():
        gold_path = notes_dir / gold_file
        if not gold_path.exists():
            continue

        with open(gold_path, 'r', encoding='utf-8') as f:
            gold = json.load(f)

        for filename, annotations in gold.get('notes', {}).items():
            note_path = notes_dir / system / filename
            if not note_path.exists():
                continue

            result = analyze_note(detector, note_path, annotations)
            total_tp += result['tp']
            total_fp += result['fp']
            total_fn += result['fn']

            for fp in result['fp_details']:
                all_fp[fp['type']].append({
                    'file': f"{system}/{filename}",
                    **fp
                })

            for fn in result['fn_details']:
                all_fn[fn['expected_type']].append({
                    'file': f"{system}/{filename}",
                    **fn
                })

    precision = total_tp / (total_tp + total_fp) if (total_tp + total_fp) > 0 else 1.0
    recall = total_tp / (total_tp + total_fn) if (total_tp + total_fn) > 0 else 1.0

    print(f"\n{'='*70}")
    print(f"OVERALL: TP={total_tp}, FP={total_fp}, FN={total_fn}")
    print(f"Precision: {precision:.2%}, Recall: {recall:.2%}")
    print(f"{'='*70}")

    print(f"\n{'='*70}")
    print("FALSE POSITIVES BY TYPE (hurting precision)")
    print(f"{'='*70}")
    for phi_type, fps in sorted(all_fp.items(), key=lambda x: -len(x[1])):
        print(f"\n{phi_type}: {len(fps)} false positives")
        for fp in fps[:5]:  # Show first 5
            print(f"  - '{fp['text']}' in {fp['file']}")
            print(f"    Context: {fp['context'][:80]}")

    print(f"\n{'='*70}")
    print("FALSE NEGATIVES BY TYPE (hurting recall)")
    print(f"{'='*70}")
    for phi_type, fns in sorted(all_fn.items(), key=lambda x: -len(x[1])):
        print(f"\n{phi_type}: {len(fns)} false negatives")
        for fn in fns[:5]:  # Show first 5
            print(f"  - '{fn['text']}' (expected {fn['expected_type']}) in {fn['file']}")
            print(f"    Context: {fn['context'][:80]}")


if __name__ == "__main__":
    main()
