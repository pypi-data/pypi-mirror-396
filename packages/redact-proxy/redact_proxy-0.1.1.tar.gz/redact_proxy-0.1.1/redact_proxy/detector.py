"""
PHI Detector with configurable detection modes.

Modes:
- fast: Regex patterns only (~1-5ms)
- balanced: Patterns + Presidio NER (~20-50ms)
- accurate: Patterns + Presidio + Transformer (~100-500ms)
"""

import re
from typing import List, Dict, Optional, Tuple

from .models import Finding
from .patterns import PatternEngine


class PHIDetector:
    """
    Configurable PHI detection engine.

    Usage:
        detector = PHIDetector(mode="fast")
        clean_text, findings = detector.redact("Patient John Smith, DOB 01/15/1980")
    """

    MODES = ("fast", "balanced", "accurate")

    def __init__(self, mode: str = "fast"):
        """
        Initialize detector with specified mode.

        Args:
            mode: Detection mode - "fast", "balanced", or "accurate"
        """
        if mode not in self.MODES:
            raise ValueError(f"Mode must be one of {self.MODES}, got '{mode}'")

        self.mode = mode
        self._pattern_engine = PatternEngine()
        self._presidio_analyzer = None
        self._transformer = None

    def detect(self, text: str) -> List[Finding]:
        """
        Detect PHI in text.

        Args:
            text: Text to analyze

        Returns:
            List of Finding objects with detected PHI
        """
        if self.mode == "fast":
            return self._detect_fast(text)
        elif self.mode == "balanced":
            return self._detect_balanced(text)
        else:  # accurate
            return self._detect_accurate(text)

    def redact(self, text: str, placeholder: str = "[{phi_type}]") -> Tuple[str, List[Finding]]:
        """
        Detect and redact PHI from text.

        Args:
            text: Text to redact
            placeholder: Format string for replacement. Use {phi_type} for the PHI type.

        Returns:
            Tuple of (redacted_text, findings)
        """
        findings = self.detect(text)

        # Sort by position (reverse) to replace from end to start
        sorted_findings = sorted(findings, key=lambda f: f.start, reverse=True)

        result = text
        for finding in sorted_findings:
            replacement = placeholder.format(phi_type=finding.phi_type)
            result = result[:finding.start] + replacement + result[finding.end:]

        return result, findings

    def _detect_fast(self, text: str) -> List[Finding]:
        """Fast detection using patterns only."""
        return self._pattern_engine.detect(text)

    def _detect_balanced(self, text: str) -> List[Finding]:
        """Balanced detection using patterns + Presidio."""
        findings = self._pattern_engine.detect(text)

        # Add Presidio findings
        presidio_findings = self._detect_presidio(text)
        findings.extend(presidio_findings)

        return self._deduplicate(findings)

    def _detect_accurate(self, text: str) -> List[Finding]:
        """Accurate detection using patterns + Presidio + transformer."""
        findings = self._pattern_engine.detect(text)

        # Add Presidio findings
        presidio_findings = self._detect_presidio(text)
        findings.extend(presidio_findings)

        # Add transformer findings
        transformer_findings = self._detect_transformer(text)
        findings.extend(transformer_findings)

        return self._deduplicate(findings)

    def _detect_presidio(self, text: str) -> List[Finding]:
        """Detect PHI using Presidio."""
        if self._presidio_analyzer is None:
            try:
                from presidio_analyzer import AnalyzerEngine
                self._presidio_analyzer = AnalyzerEngine()
            except ImportError:
                raise ImportError(
                    "Presidio not installed. Install with: pip install redactiphi-sdk[balanced]"
                )

        results = self._presidio_analyzer.analyze(
            text=text,
            language="en",
            entities=[
                "PERSON", "PHONE_NUMBER", "EMAIL_ADDRESS", "LOCATION",
                "DATE_TIME", "US_SSN", "US_DRIVER_LICENSE", "MEDICAL_LICENSE"
            ]
        )

        findings = []
        for result in results:
            # Map Presidio types to our types
            phi_type_map = {
                "PERSON": "NAME",
                "PHONE_NUMBER": "PHONE",
                "EMAIL_ADDRESS": "EMAIL",
                "LOCATION": "ADDRESS",
                "DATE_TIME": "DATE",
                "US_SSN": "SSN",
                "US_DRIVER_LICENSE": "LICENSE",
                "MEDICAL_LICENSE": "LICENSE",
            }
            phi_type = phi_type_map.get(result.entity_type, result.entity_type)

            findings.append(Finding(
                text=text[result.start:result.end],
                phi_type=phi_type,
                start=result.start,
                end=result.end,
                confidence=result.score,
                source="presidio"
            ))

        return findings

    def _detect_transformer(self, text: str) -> List[Finding]:
        """Detect PHI using transformer model (OBI2B2 or similar)."""
        if self._transformer is None:
            try:
                from transformers import pipeline
                # Use a clinical NER model - can be swapped for OBI2B2
                self._transformer = pipeline(
                    "ner",
                    model="obi/deid_roberta_i2b2",
                    aggregation_strategy="simple"
                )
            except ImportError:
                raise ImportError(
                    "Transformers not installed. Install with: pip install redactiphi-sdk[accurate]"
                )
            except Exception as e:
                # Model might not be available - fall back gracefully
                print(f"Warning: Could not load transformer model: {e}")
                return []

        try:
            results = self._transformer(text)
        except Exception:
            return []

        findings = []
        for result in results:
            # Map transformer entity types to our types
            entity_type = result.get("entity_group", result.get("entity", "UNKNOWN"))
            phi_type_map = {
                "PATIENT": "NAME",
                "DOCTOR": "NAME",
                "STAFF": "NAME",
                "AGE": "AGE",
                "DATE": "DATE",
                "PHONE": "PHONE",
                "ID": "MRN",
                "HOSPITAL": "FACILITY",
                "LOCATION": "ADDRESS",
                "STREET": "ADDRESS",
                "CITY": "ADDRESS",
                "STATE": "ADDRESS",
                "ZIP": "ADDRESS",
                "COUNTRY": "ADDRESS",
            }
            phi_type = phi_type_map.get(entity_type.upper(), entity_type.upper())

            findings.append(Finding(
                text=result["word"],
                phi_type=phi_type,
                start=result["start"],
                end=result["end"],
                confidence=result["score"],
                source="transformer"
            ))

        return findings

    def _deduplicate(self, findings: List[Finding]) -> List[Finding]:
        """Remove overlapping findings, keeping the best one."""
        if not findings:
            return []

        # Sort by start, then by length (desc), then by confidence (desc)
        sorted_findings = sorted(
            findings,
            key=lambda f: (f.start, -(f.end - f.start), -f.confidence)
        )

        result = []
        for finding in sorted_findings:
            overlaps = False
            for kept in result:
                if finding.start < kept.end and finding.end > kept.start:
                    overlaps = True
                    break
            if not overlaps:
                result.append(finding)

        return result
