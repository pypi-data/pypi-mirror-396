"""Tests for PHI detector."""

import pytest
from redact_proxy import PHIDetector


class TestPHIDetector:
    """Test PHI detection functionality."""

    def test_detect_name_with_title(self):
        """Test detection of names with titles."""
        detector = PHIDetector(mode="fast")
        findings = detector.detect("Dr. John Smith is the attending physician.")

        assert len(findings) >= 1
        name_findings = [f for f in findings if f.phi_type == "NAME"]
        assert len(name_findings) >= 1
        assert any("John Smith" in f.text for f in name_findings)

    def test_detect_ssn(self):
        """Test detection of SSN."""
        detector = PHIDetector(mode="fast")
        findings = detector.detect("SSN: 123-45-6789")

        assert len(findings) >= 1
        ssn_findings = [f for f in findings if f.phi_type == "SSN"]
        assert len(ssn_findings) >= 1

    def test_detect_date(self):
        """Test detection of dates."""
        detector = PHIDetector(mode="fast")
        findings = detector.detect("DOB: 01/15/1980")

        assert len(findings) >= 1
        date_findings = [f for f in findings if f.phi_type in ("DATE", "DOB")]
        assert len(date_findings) >= 1

    def test_detect_phone(self):
        """Test detection of phone numbers."""
        detector = PHIDetector(mode="fast")
        findings = detector.detect("Phone: (555) 123-4567")

        assert len(findings) >= 1
        phone_findings = [f for f in findings if f.phi_type == "PHONE"]
        assert len(phone_findings) >= 1

    def test_detect_email(self):
        """Test detection of email addresses."""
        detector = PHIDetector(mode="fast")
        findings = detector.detect("Email: john.smith@hospital.com")

        assert len(findings) >= 1
        email_findings = [f for f in findings if f.phi_type == "EMAIL"]
        assert len(email_findings) >= 1

    def test_detect_age(self):
        """Test detection of ages."""
        detector = PHIDetector(mode="fast")
        findings = detector.detect("The patient is a 65 year old male.")

        assert len(findings) >= 1
        age_findings = [f for f in findings if f.phi_type == "AGE"]
        assert len(age_findings) >= 1

    def test_detect_address(self):
        """Test detection of addresses."""
        detector = PHIDetector(mode="fast")
        findings = detector.detect("Lives at 123 Main Street")

        assert len(findings) >= 1
        addr_findings = [f for f in findings if f.phi_type == "ADDRESS"]
        assert len(addr_findings) >= 1

    def test_redact_simple(self):
        """Test basic redaction."""
        detector = PHIDetector(mode="fast")
        text = "Patient: John Smith, DOB 01/15/1980"
        redacted, findings = detector.redact(text)

        assert "[NAME]" in redacted or "[DOB]" in redacted or "[DATE]" in redacted
        assert "John Smith" not in redacted

    def test_redact_custom_placeholder(self):
        """Test redaction with custom placeholder."""
        detector = PHIDetector(mode="fast")
        text = "Dr. Jane Doe is the physician"
        redacted, findings = detector.redact(text, placeholder="<REDACTED:{phi_type}>")

        assert "<REDACTED:NAME>" in redacted
        assert "Jane Doe" not in redacted

    def test_detect_complex_note(self):
        """Test detection in a complex clinical note."""
        detector = PHIDetector(mode="fast")
        note = """
        Patient: John Smith
        DOB: 01/15/1980
        MRN: E1234567
        SSN: 123-45-6789

        Chief Complaint: 65 year old male presents with chest pain.
        Contact: Phone (555) 123-4567, Email john.smith@email.com
        Address: 123 Main Street, Boston, MA 02101
        """

        findings = detector.detect(note)

        # Should find multiple PHI types
        phi_types = {f.phi_type for f in findings}
        assert len(phi_types) >= 3  # At least 3 different PHI types

    def test_no_phi(self):
        """Test text with no PHI."""
        detector = PHIDetector(mode="fast")
        text = "The patient has diabetes and hypertension."
        findings = detector.detect(text)

        # Should find no PHI (or very few false positives)
        assert len(findings) <= 1

    def test_invalid_mode(self):
        """Test that invalid mode raises error."""
        with pytest.raises(ValueError):
            PHIDetector(mode="invalid")


class TestDetectorModes:
    """Test different detection modes."""

    def test_fast_mode(self):
        """Test fast mode works."""
        detector = PHIDetector(mode="fast")
        findings = detector.detect("Dr. John Smith")
        assert len(findings) >= 1

    def test_balanced_mode_import_error(self):
        """Test balanced mode gracefully handles missing presidio."""
        detector = PHIDetector(mode="balanced")
        # This should work even if presidio isn't installed
        # (it will fall back to patterns only with a warning)
        try:
            findings = detector.detect("Dr. John Smith")
            assert len(findings) >= 1
        except ImportError:
            # Expected if presidio not installed
            pass

    def test_accurate_mode_import_error(self):
        """Test accurate mode gracefully handles missing transformers."""
        detector = PHIDetector(mode="accurate")
        try:
            findings = detector.detect("Dr. John Smith")
            assert len(findings) >= 1
        except ImportError:
            # Expected if transformers not installed
            pass
