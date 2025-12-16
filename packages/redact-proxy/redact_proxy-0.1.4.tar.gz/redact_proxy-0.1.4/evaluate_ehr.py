"""
Evaluate Redact Proxy against EHR notes with gold annotations.

Usage:
    python evaluate_ehr.py                    # Run on all EHR systems
    python evaluate_ehr.py --system meditech  # Run on specific system
    python evaluate_ehr.py --mode accurate    # Use accurate mode
"""

import json
import os
import sys
import time
from pathlib import Path
from dataclasses import dataclass
from typing import Dict, List, Set, Tuple

# Add parent for imports
sys.path.insert(0, str(Path(__file__).parent))

from redact_proxy import PHIDetector


@dataclass
class EvaluationResult:
    """Results from evaluating one note."""
    filename: str
    true_positives: int
    false_positives: int
    false_negatives: int
    precision: float
    recall: float
    f1: float
    time_ms: float


def load_gold_annotations(gold_path: Path) -> Dict:
    """Load gold standard annotations."""
    with open(gold_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def get_expected_phi(note_annotations: Dict) -> Tuple[Set[Tuple], Set[Tuple]]:
    """
    Extract expected PHI from annotations.

    Returns:
        (true_phi, false_positive_texts) - Sets of (start, end, normalized_type)
    """
    true_phi = set()
    fp_texts = set()

    for pred in note_annotations.get('predictions', []):
        key = (pred['start'], pred['end'])
        if pred.get('false_positive', False):
            fp_texts.add(key)
        else:
            true_phi.add(key)

    # Add missed PHI
    for missed in note_annotations.get('missed', []):
        key = (missed['start'], missed['end'])
        true_phi.add(key)

    return true_phi, fp_texts


def evaluate_note(
    detector: PHIDetector,
    note_text: str,
    note_annotations: Dict
) -> EvaluationResult:
    """Evaluate detector on a single note."""

    # Get expected PHI
    expected_phi, known_fps = get_expected_phi(note_annotations)

    # Run detection
    start_time = time.perf_counter()
    findings = detector.detect(note_text)
    elapsed_ms = (time.perf_counter() - start_time) * 1000

    # Get detected spans
    detected = set()
    for f in findings:
        detected.add((f.start, f.end))

    # Calculate metrics
    # True positives: detected AND in expected (not marked as FP)
    true_positives = detected & expected_phi

    # False positives: detected but NOT in expected (or marked as FP in gold)
    false_positives = detected - expected_phi

    # False negatives: expected but not detected
    false_negatives = expected_phi - detected

    tp = len(true_positives)
    fp = len(false_positives)
    fn = len(false_negatives)

    precision = tp / (tp + fp) if (tp + fp) > 0 else 1.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 1.0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0

    return EvaluationResult(
        filename=note_annotations.get('filename', 'unknown'),
        true_positives=tp,
        false_positives=fp,
        false_negatives=fn,
        precision=precision,
        recall=recall,
        f1=f1,
        time_ms=elapsed_ms
    )


def evaluate_system(
    ehr_system: str,
    notes_dir: Path,
    gold_path: Path,
    mode: str = "fast"
) -> List[EvaluationResult]:
    """Evaluate all notes for an EHR system."""

    print(f"\n{'='*60}")
    print(f"Evaluating {ehr_system.upper()} notes (mode={mode})")
    print(f"{'='*60}")

    # Load gold annotations
    if not gold_path.exists():
        print(f"  Warning: No gold annotations at {gold_path}")
        return []

    gold = load_gold_annotations(gold_path)

    # Create detector
    detector = PHIDetector(mode=mode)

    results = []

    for filename, annotations in gold.get('notes', {}).items():
        note_path = notes_dir / filename

        if not note_path.exists():
            print(f"  Skipping {filename} - file not found")
            continue

        with open(note_path, 'r', encoding='utf-8', errors='replace') as f:
            note_text = f.read()

        annotations['filename'] = filename
        result = evaluate_note(detector, note_text, annotations)
        results.append(result)

        status = "OK" if result.f1 >= 0.9 else "LOW" if result.f1 >= 0.7 else "WARN"
        print(f"  [{status}] {filename}: P={result.precision:.2f} R={result.recall:.2f} F1={result.f1:.2f} ({result.time_ms:.1f}ms)")

    return results


def print_summary(all_results: Dict[str, List[EvaluationResult]], mode: str):
    """Print summary statistics."""

    print(f"\n{'='*60}")
    print(f"SUMMARY - Mode: {mode}")
    print(f"{'='*60}")

    total_tp = 0
    total_fp = 0
    total_fn = 0
    total_time = 0
    total_notes = 0

    for system, results in all_results.items():
        if not results:
            continue

        sys_tp = sum(r.true_positives for r in results)
        sys_fp = sum(r.false_positives for r in results)
        sys_fn = sum(r.false_negatives for r in results)
        sys_time = sum(r.time_ms for r in results)

        sys_precision = sys_tp / (sys_tp + sys_fp) if (sys_tp + sys_fp) > 0 else 1.0
        sys_recall = sys_tp / (sys_tp + sys_fn) if (sys_tp + sys_fn) > 0 else 1.0
        sys_f1 = 2 * sys_precision * sys_recall / (sys_precision + sys_recall) if (sys_precision + sys_recall) > 0 else 0.0

        print(f"\n{system.upper()}:")
        print(f"  Notes: {len(results)}")
        print(f"  TP: {sys_tp}, FP: {sys_fp}, FN: {sys_fn}")
        print(f"  Precision: {sys_precision:.2%}")
        print(f"  Recall: {sys_recall:.2%}")
        print(f"  F1: {sys_f1:.2%}")
        print(f"  Avg time: {sys_time/len(results):.1f}ms per note")

        total_tp += sys_tp
        total_fp += sys_fp
        total_fn += sys_fn
        total_time += sys_time
        total_notes += len(results)

    if total_notes > 0:
        overall_precision = total_tp / (total_tp + total_fp) if (total_tp + total_fp) > 0 else 1.0
        overall_recall = total_tp / (total_tp + total_fn) if (total_tp + total_fn) > 0 else 1.0
        overall_f1 = 2 * overall_precision * overall_recall / (overall_precision + overall_recall) if (overall_precision + overall_recall) > 0 else 0.0

        print(f"\n{'='*60}")
        print(f"OVERALL ({total_notes} notes):")
        print(f"  Precision: {overall_precision:.2%}")
        print(f"  Recall: {overall_recall:.2%}")
        print(f"  F1: {overall_f1:.2%}")
        print(f"  Total time: {total_time:.0f}ms ({total_time/total_notes:.1f}ms avg)")
        print(f"{'='*60}")


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Evaluate Redact Proxy on EHR notes")
    parser.add_argument("--system", choices=["meditech", "cerner", "eclinical", "all"],
                       default="all", help="EHR system to evaluate")
    parser.add_argument("--mode", choices=["fast", "balanced", "accurate"],
                       default="fast", help="Detection mode")
    parser.add_argument("--notes-dir", type=Path,
                       default=Path(r"C:\Users\drcra\Documents\Coding Projects\RedactiPHI\tests\ehr_notes"),
                       help="Path to EHR notes directory")

    args = parser.parse_args()

    systems = {
        "meditech": ("meditech", "meditech_annotated.json"),
        "cerner": ("cerner", "cerner_annotated.json"),
        "eclinical": ("eclinical", "eclinical_annotated.json"),
    }

    if args.system == "all":
        to_evaluate = list(systems.keys())
    else:
        to_evaluate = [args.system]

    all_results = {}

    for system in to_evaluate:
        folder, gold_file = systems[system]
        notes_dir = args.notes_dir / folder
        gold_path = args.notes_dir / gold_file

        results = evaluate_system(system, notes_dir, gold_path, args.mode)
        all_results[system] = results

    print_summary(all_results, args.mode)


if __name__ == "__main__":
    main()
