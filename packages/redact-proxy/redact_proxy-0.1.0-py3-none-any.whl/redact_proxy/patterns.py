"""
Pattern-based PHI detection engine.

Covers all 18 HIPAA Safe Harbor identifiers plus clinical extensions.
"""

import re
from dataclasses import dataclass
from typing import Callable, List, Optional, Pattern

from .models import Finding
from .wordlists import is_likely_name, FIRST_NAMES_UNAMBIG, LAST_NAMES_UNAMBIG


@dataclass
class PatternDefinition:
    """A pattern with optional context validator."""
    pattern: Pattern
    phi_type: str
    confidence: float = 0.85
    validator: Optional[Callable[[str, re.Match], bool]] = None
    description: str = ""


class PatternEngine:
    """
    Regex-based PHI detection for structured identifiers.

    Usage:
        engine = PatternEngine()
        findings = engine.detect("Patient John Smith, DOB 01/15/1980, SSN 123-45-6789")
    """

    def __init__(self):
        self.patterns: List[PatternDefinition] = self._build_patterns()

    def detect(self, text: str) -> List[Finding]:
        """
        Detect PHI in text using pattern matching.

        Args:
            text: Clinical text to analyze

        Returns:
            List of Finding objects with detected PHI
        """
        all_findings = []

        for pattern_def in self.patterns:
            for match in pattern_def.pattern.finditer(text):
                if pattern_def.validator is not None:
                    if not pattern_def.validator(text, match):
                        continue

                # For patterns with labeled prefixes, extract just the value part
                # This applies to patterns where the full match includes a label prefix
                # like "PATIENT:", "Phone:", "ROOM/BED:", "UNIT #:", "ACCOUNT#:", etc.
                # and we want to extract only the PHI value, not the label.
                extract_group = False
                if pattern_def.phi_type == "PATIENT_NAME" and "patient label" in pattern_def.description:
                    extract_group = True
                elif pattern_def.phi_type in ("PHONE", "FAX") and "with label" in pattern_def.description:
                    extract_group = True
                elif pattern_def.phi_type == "PROVIDER_NAME" and "clinical context" in pattern_def.description:
                    extract_group = True
                # Dietitian and Impression By signatures - extract just the name
                elif pattern_def.phi_type == "PROVIDER_NAME" and "signature" in pattern_def.description:
                    extract_group = True
                # Username patterns with labels - extract just the username
                elif pattern_def.phi_type == "USERNAME" and ("signature" in pattern_def.description or "Labeled" in pattern_def.description):
                    extract_group = True
                # ROOM_BED patterns have labeled prefixes like "ROOM/BED:", "UNIT #:"
                elif pattern_def.phi_type == "ROOM_BED":
                    extract_group = True
                # ACCOUNT_NUMBER, MRN, INSURANCE_ID patterns have labeled prefixes
                elif pattern_def.phi_type in ("ACCOUNT_NUMBER", "MRN", "INSURANCE_ID"):
                    extract_group = True

                if extract_group:
                    # Get the first non-None capturing group (the actual value)
                    value_text = None
                    value_start = None
                    value_end = None
                    for i in range(1, match.lastindex + 1 if match.lastindex else 1):
                        if match.group(i):
                            value_text = match.group(i).strip()
                            value_start = match.start(i)
                            value_end = match.start(i) + len(value_text)
                            break

                    if value_text:
                        all_findings.append(Finding(
                            text=value_text,
                            phi_type=pattern_def.phi_type,
                            start=value_start,
                            end=value_end,
                            confidence=pattern_def.confidence,
                            source="patterns"
                        ))
                else:
                    all_findings.append(Finding(
                        text=match.group(),
                        phi_type=pattern_def.phi_type,
                        start=match.start(),
                        end=match.end(),
                        confidence=pattern_def.confidence,
                        source="patterns"
                    ))

        # Deduplicate overlapping findings - prefer longer/higher confidence
        return self._deduplicate_findings(all_findings)

    def _deduplicate_findings(self, findings: List[Finding]) -> List[Finding]:
        """
        Remove overlapping findings, keeping the best one for each span.

        Prefers: longer matches, higher confidence, more specific types.
        """
        if not findings:
            return []

        # Sort by start position, then by length (descending), then confidence (descending)
        sorted_findings = sorted(
            findings,
            key=lambda f: (f.start, -(f.end - f.start), -f.confidence)
        )

        result = []
        for finding in sorted_findings:
            # Check if this finding overlaps with any we've already kept
            overlaps = False
            for kept in result:
                # Check if spans overlap
                if finding.start < kept.end and finding.end > kept.start:
                    overlaps = True
                    break

            if not overlaps:
                result.append(finding)

        return result

    def _build_patterns(self) -> List[PatternDefinition]:
        """Build all pattern definitions."""
        patterns = []
        patterns.extend(self._name_patterns())
        patterns.extend(self._date_patterns())
        patterns.extend(self._age_patterns())
        patterns.extend(self._ssn_patterns())
        patterns.extend(self._mrn_patterns())
        patterns.extend(self._medicare_patterns())
        patterns.extend(self._phone_patterns())
        patterns.extend(self._email_patterns())
        patterns.extend(self._address_patterns())
        patterns.extend(self._professional_id_patterns())
        patterns.extend(self._device_vehicle_patterns())
        patterns.extend(self._web_patterns())
        patterns.extend(self._clinical_location_patterns())
        patterns.extend(self._account_patterns())
        patterns.extend(self._username_patterns())
        return patterns

    def _name_patterns(self) -> List[PatternDefinition]:
        """Patterns for detecting names."""
        return [
            PatternDefinition(
                pattern=re.compile(
                    r"\b(Mr|Mrs|Ms|Miss|Dr|Prof|Rev|Sr|Jr)\.?\s+"
                    r"([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\b"
                ),
                phi_type="PERSON_NAME",
                confidence=0.90,
                description="Title followed by name"
            ),
            PatternDefinition(
                pattern=re.compile(
                    r"(?:seen\s+by|evaluated\s+by|examined\s+by|treated\s+by|"
                    r"referred\s+by|attending:|referring:|consulting:|admitting:)\s*"
                    r"(?:Dr\.?\s+)?([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)",
                    re.IGNORECASE
                ),
                phi_type="PROVIDER_NAME",
                confidence=0.90,
                validator=self._validate_not_clinical_department,
                description="Provider name with clinical context"
            ),
            PatternDefinition(
                pattern=re.compile(
                    r"\b([A-Z][a-z]+(?:\s+[A-Z]\.?)?\s+[A-Z][a-z]+)\s*,?\s*"
                    r"(MD|DO|NP|PA|RN|LPN|APRN|PhD|PharmD)\b"
                ),
                phi_type="PROVIDER_NAME",
                confidence=0.88,
                description="Name followed by medical credentials"
            ),
            # Provider name with space before comma: "Ian Simpson , PAC"
            PatternDefinition(
                pattern=re.compile(
                    r"\b([A-Z][a-z]+\s+[A-Z][a-z]+)\s+,\s*"
                    r"(PAC|PA-C|PA|NP|RN|MD|DO)\b"
                ),
                phi_type="PROVIDER_NAME",
                confidence=0.88,
                description="Provider with spaced comma"
            ),
            # Dietitian signature: "Dietitian name: Annette T Maher, RD"
            PatternDefinition(
                pattern=re.compile(
                    r"(?:Dietitian|Dietician|Nutritionist)\s+name\s*:\s*"
                    r"([A-Z][a-z]+(?:\s+[A-Z]\.?)?\s+[A-Z][a-z]+)",
                    re.IGNORECASE
                ),
                phi_type="PROVIDER_NAME",
                confidence=0.92,
                description="Dietitian signature"
            ),
            # Impression By: "Impression By: PHLABSA - Lalvatore Labruzzo MD"
            PatternDefinition(
                pattern=re.compile(
                    r"(?:Impression|Interpreted|Read|Reviewed|Verified)\s+By\s*:\s*"
                    r"(?:[A-Z]+\s*-\s*)?"  # Optional code prefix like "PHLABSA - "
                    r"([A-Z][a-z]+(?:\s+[A-Z]\.?)?\s+[A-Z][a-z]+)",
                    re.IGNORECASE
                ),
                phi_type="PROVIDER_NAME",
                confidence=0.92,
                description="Impression/reading provider signature"
            ),
            # "Performed By:" pattern
            PatternDefinition(
                pattern=re.compile(
                    r"(?:Performed|Signed|Authenticated|Completed)\s+By\s*:\s*"
                    r"([A-Z][a-z]+(?:\s+[A-Z]\.?)?\s+[A-Z][a-z]+)",
                    re.IGNORECASE
                ),
                phi_type="PROVIDER_NAME",
                confidence=0.90,
                description="Procedure provider signature"
            ),
            PatternDefinition(
                pattern=re.compile(
                    # Match names after "patient:", "pt:", "name:", "patient name:"
                    # Use [ \t]* instead of \s* to stay on same line
                    # Capturing group 1 or 2 contains only the name
                    # Captures up to 3 name parts: First [Middle] [Last]
                    r"(?:patient|pt)[ \t]*[:#][ \t]*"
                    r"([A-Z][a-zA-Z]+(?:[ \t]+[A-Z][a-zA-Z]+){0,2})"
                    r"|"
                    r"(?:patient[ \t]+)?name[ \t]*[:#][ \t]*"
                    r"([A-Z][a-zA-Z]+(?:[ \t]+[A-Z][a-zA-Z]+){0,2})",
                    re.IGNORECASE
                ),
                phi_type="PATIENT_NAME",
                confidence=0.92,
                description="Name with patient label",
                validator=None  # Name extraction handled in detect method
            ),
            PatternDefinition(
                pattern=re.compile(r"\b([A-Z][a-z]+)\s*,\s*([A-Z][a-z]+)\b"),
                phi_type="PERSON_NAME",
                confidence=0.82,
                validator=self._validate_name_not_location,
                description="Last, First name format"
            ),
            # Uppercase name format: "FANCIL, CAROLE L" or "MASHRAGI, TEREZA W"
            PatternDefinition(
                pattern=re.compile(
                    r"\b([A-Z]{2,15})\s*,\s*([A-Z]{2,15})(?:\s+[A-Z])?\b"
                ),
                phi_type="PATIENT_NAME",
                confidence=0.88,
                validator=self._validate_uppercase_name,
                description="Uppercase LAST, FIRST name format"
            ),
            # Mixed case name: "RITCHOTTE, Heather E" or "BROWN, ELIZABETH"
            PatternDefinition(
                pattern=re.compile(
                    r"\b([A-Z]{2,15})\s*,\s*([A-Z][a-z]+)(?:\s+[A-Z])?\b"
                ),
                phi_type="PATIENT_NAME",
                confidence=0.88,
                validator=self._validate_uppercase_name,
                description="Mixed case LAST, First name format"
            ),
            PatternDefinition(
                pattern=re.compile(
                    # IMPORTANT: \b at start prevents matching "son" within "Johnson" or "Thompson"
                    r"\b(?:mother|father|mom|dad|son|daughter|wife|husband|spouse|"
                    r"brother|sister|sibling|aunt|uncle|grandmother|grandfather|"
                    r"grandson|granddaughter|partner|guardian)\s+"
                    # Skip "of X" constructs like "mother of two" - not names
                    r"(?!of\s+)"
                    # Require actual name patterns, not status words
                    r"(?:(?:is\s+|was\s+)?named?\s+)?"
                    r"([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)"
                    # Exclude status/descriptor words
                    r"(?!\s*(?:deceased|living|alive|dead|age|aged|years|old|with|has|had))",
                    re.IGNORECASE
                ),
                phi_type="FAMILY_MEMBER_NAME",
                confidence=0.88,
                validator=self._validate_family_member_name,
                description="Family member name"
            ),
        ]

    # Common lab test components and medical terms that appear in "Word, Word" format
    LAB_AND_MEDICAL_TERMS = frozenset({
        # Lab components
        "abs", "absolute", "total", "serum", "plasma", "urine", "blood",
        "direct", "indirect", "free", "bound", "ionized", "random", "fasting",
        "auto", "manual", "calculated", "measured", "estimated", "panel",
        # Lab test names that look like names in "X, Y" format
        "dimer", "quantitative", "qualitative", "electrolytic", "caloric",
        "consultant", "follow", "instructions", "discharge", "routines",
        # Lab test names (first word)
        "neutrophil", "lymphocyte", "monocyte", "eosinophil", "basophil",
        "hemoglobin", "hematocrit", "platelet", "glucose", "sodium", "potassium",
        "chloride", "bicarbonate", "calcium", "magnesium", "phosphorus", "phosphate",
        "creatinine", "bilirubin", "albumin", "globulin", "protein", "ammonia",
        "lipase", "amylase", "troponin", "bnp", "procalcitonin", "lactate",
        "fibrinogen", "ferritin", "transferrin", "iron", "tibc", "folate",
        "vitamin", "homocysteine", "methylmalonic", "reticulocyte",
        # Anatomy/procedures
        "artery", "vein", "muscle", "nerve", "bone", "tissue", "skin",
        "pharynx", "larynx", "esophagus", "stomach", "colon", "rectum",
        "kidney", "liver", "spleen", "pancreas", "gallbladder", "bladder",
        "percutaneous", "endoscopic", "laparoscopic", "external", "internal",
        "anterior", "posterior", "lateral", "medial", "proximal", "distal",
        "substitute", "replacement", "repair", "removal", "excision", "insertion",
        # Clinical terms
        "alert", "oriented", "responsive", "cooperative", "ambulatory",
        "normocephalic", "atraumatic", "symmetric", "regular", "irregular",
        "soft", "tender", "distended", "rigid", "guarded", "rebound",
        "negative", "positive", "normal", "abnormal", "elevated", "decreased",
        "acute", "chronic", "stable", "unstable", "improved", "worsened",
        "continuous", "intermittent", "episodic", "recurrent", "persistent",
        "documented", "reviewed", "discussed", "explained", "recommended",
        # Questionnaire/form words
        "yes", "how", "what", "when", "where", "why", "which", "other",
        "none", "unknown", "plan", "date", "time", "type", "index",
        # Family history
        "mother", "father", "parent", "sibling", "brother", "sister",
        "son", "daughter", "child", "spouse", "husband", "wife",
        "grandmother", "grandfather", "grandparent", "aunt", "uncle", "cousin",
        # Social determinants screening
        "housing", "food", "transportation", "utility", "safety", "interpersonal",
        "insecurity", "instability", "difficulties", "needs",
        # Vital signs / measurements
        "weight", "height", "temperature", "pressure", "rate", "output", "input",
        "actual", "ideal", "adjusted", "corrected",
        # Three or more letter words that are clearly not names
        "one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten",
        "moves", "moves", "notes", "shows", "takes", "gives", "needs", "uses",
        # Medical procedures / billing codes (CPT descriptions)
        "immunization", "pneumococcal", "vaccination", "injection", "inj",
        "approach", "mammary", "cataract", "bilateral", "unilateral",
        "open", "closed", "new", "established", "initial", "subsequent",
        "diagnostic", "therapeutic", "screening", "preventive",
        "right", "left", "upper", "lower", "leg", "arm", "hand", "foot",
        "heart", "lung", "breast", "eye", "ear", "nose", "throat",
        # Physical exam terms
        "warm", "dry", "cool", "moist", "intact", "supple", "non",
        "clear", "dull", "flat", "resonant", "tympanic",
        "brisk", "sluggish", "reactive", "unreactive", "equal",
        "present", "absent", "diminished", "increased",
        # Discharge/disposition
        "discharge", "medical", "disposition", "transfer", "admit",
        "patient", "regarding", "concerning", "related",
        # Substances/drugs of abuse
        "amphetamines", "cocaine", "ecstasy", "hallucinogens",
        "heroin", "inhalants", "solvents", "marijuana", "cannabis",
        "opioids", "benzodiazepines", "barbiturates", "methamphetamine",
        # Tobacco/alcohol
        "cigarettes", "former", "current", "never", "pack", "packs",
        "liquor", "beer", "wine", "alcohol", "drinks", "social",
        # Lack/absence terms
        "no", "lack", "without", "denies", "denied",
        # Oncology staging
        "stage", "grade", "primary", "metastatic", "localized", "regional",
        # More body parts
        "chest", "abdomen", "pelvis", "extremity", "extremities",
        "cervical", "thoracic", "lumbar", "sacral",
        # Timing/frequency
        "once", "twice", "daily", "weekly", "monthly", "prn", "routine",
        # Common clinical adjectives
        "mild", "moderate", "severe", "minimal", "marked", "significant",
        # Anatomy terms that appear in procedure descriptions
        "cecum", "duodenum", "jejunum", "ileum", "appendix", "rectum",
        "via", "subcut", "subcutaneous", "supp", "suppository",
        "scale", "bedscale", "vital", "vitals",
        # PT/OT/rehabilitation terms
        "cane", "shower", "walker", "wheelchair", "grab", "bar", "bars",
        "driving", "housework", "laundry", "meal", "meals", "preparation",
        "equipment", "anticipated", "surrogate", "living", "will",
        "sitting", "standing", "walking", "transferring", "gait", "balance",
        "prevention", "fall", "falls", "risk", "safety",
        "therapy", "services", "education", "demonstration", "explanation",
        "comorbidities", "personal", "history", "problems",
        "units", "high", "low", "kyphosis", "accentuated", "lordosis",
        "edema", "endurance", "rom", "strength", "flexibility",
        # Medication terms
        "cefepime", "flagyl", "metronidazole", "vancomycin", "zosyn",
        "tube", "chew", "oral", "iv", "im", "sq",
        # Symptoms
        "fever", "chills", "nausea", "vomiting", "diarrhea", "constipation",
        "pain", "ache", "swelling", "redness", "warmth",
        # Affect/mental status
        "appropriate", "calm", "anxious", "agitated", "cooperative",
        # Directions/positions
        "to", "from", "at", "in", "on", "per", "via",
        # Clinical/document terms
        "clinical", "rectal", "vaginal", "oral", "topical",
        # Common diagnoses/conditions that appear in "Condition, Condition" lists
        "hypertension", "diabetes", "anxiety", "depression", "migraines",
        "headache", "dizziness", "smoking", "tobacco", "disorder",
        "status", "suicidal", "generalized", "meningioma",
        "thoracentesis", "bronchoscopy", "pneumonia", "copd", "chf",
        "cad", "ckd", "esrd", "htn", "dm", "cva", "tia", "dvt", "pe",
        "afib", "hfref", "hfpef", "gerd", "ibs", "osa", "bph",
        "injury", "hypovolemic", "lethargy", "difficulty", "fracture",
        "infection", "sepsis", "failure", "insufficiency", "deficiency",
        # Brief/document section headers
        "brief", "hospital", "course",
    })

    def _validate_name_not_location(self, text: str, match: re.Match) -> bool:
        """Validate that 'Last, First' is not a location or medical term.

        Uses a combination of:
        1. Blocklist for known medical terms
        2. Positive matching against known name lists
        """
        first = match.group(1).lower() if match.lastindex >= 1 else ""
        second = match.group(2).lower() if match.lastindex >= 2 else ""

        # Check for US state abbreviations (City, State)
        states = {"al", "ak", "az", "ar", "ca", "co", "ct", "de", "fl", "ga",
                  "hi", "id", "il", "in", "ia", "ks", "ky", "la", "me", "md",
                  "ma", "mi", "mn", "ms", "mo", "mt", "ne", "nv", "nh", "nj",
                  "nm", "ny", "nc", "nd", "oh", "ok", "or", "pa", "ri", "sc",
                  "sd", "tn", "tx", "ut", "vt", "va", "wa", "wv", "wi", "wy"}
        if second in states:
            return False

        # Reject if either word is a known medical term
        if first in self.LAB_AND_MEDICAL_TERMS:
            return False
        if second in self.LAB_AND_MEDICAL_TERMS:
            return False

        # POSITIVE matching: at least one word should look like a name
        # "Last, First" format: first word is last name, second is first name
        first_is_name = is_likely_name(first)
        second_is_name = is_likely_name(second)

        # If second word (the "first name" part) matches known first names, high confidence
        if second in FIRST_NAMES_UNAMBIG:
            return True

        # If first word (the "last name" part) matches known last names, accept if second also looks like name
        if first in LAST_NAMES_UNAMBIG and second_is_name:
            return True

        # If neither word looks like a known name, likely not a name
        # Unless the words look name-like (capitalized, reasonable length)
        if not first_is_name and not second_is_name:
            # Check if words could be unusual names (proper length, no obvious medical patterns)
            # Reject if second word is short (<=3 chars) and not a known name - likely abbreviation
            if len(second) <= 3:
                return False
            # Reject if looks like medication/compound names (ends in common suffixes)
            med_suffixes = ('emia', 'itis', 'osis', 'tion', 'ment', 'ine', 'ide', 'ate', 'one', 'cin')
            if first.endswith(med_suffixes) or second.endswith(med_suffixes):
                return False

        return True

    # Clinical departments that should not be treated as provider names
    CLINICAL_DEPARTMENTS = frozenset({
        "physical therapy", "occupational therapy", "speech therapy",
        "respiratory therapy", "physical therapist", "occupational therapist",
        "speech therapist", "respiratory therapist",
        "radiology", "cardiology", "neurology", "oncology", "pharmacy",
        "nursing", "laboratory", "pathology", "surgery", "medicine",
        "psychiatry", "psychology", "nutrition", "dietary", "social work",
        "case management", "wound care", "pain management",
        "emergency", "icu", "ccu", "nicu", "picu", "pacu",
        "internal medicine", "family medicine", "pediatrics", "geriatrics",
        "social services", "chaplain services", "interpreter services",
        # Short specialty abbreviations commonly used in consult notes
        "ortho", "neuro", "cardio", "pulm", "nephro", "endo", "rheum",
        "gi", "id", "ep", "ir", "vascular surgery", "general surgery",
        "thoracic surgery", "plastic surgery", "oral surgery",
        "hematology", "heme/onc", "hem/onc", "palliative", "hospice",
        "pt", "ot", "st", "rt", "sw", "cm",  # PT/OT/ST/RT/SW/CM abbreviations
    })

    # Pronouns and common words that should not be treated as provider names
    PROVIDER_NON_NAME_WORDS = frozenset({
        'me', 'my', 'myself', 'us', 'we', 'our', 'ours', 'ourselves',
        'him', 'her', 'them', 'they', 'their', 'theirs',
        'the', 'this', 'that', 'these', 'those',
        'staff', 'team', 'nursing', 'nurse', 'physician', 'provider',
        'resident', 'fellow', 'attending', 'intern',
        'pain', 'medication', 'medications', 'per', 'protocol',
    })

    def _validate_not_clinical_department(self, text: str, match: re.Match) -> bool:
        """Validate that matched name is not a clinical department or pronoun."""
        # Get the captured name part (group 1)
        name_part = match.group(1).lower() if match.lastindex >= 1 else match.group().lower()

        # Reject clinical departments
        if name_part in self.CLINICAL_DEPARTMENTS:
            return False

        # Reject pronouns and common non-name words
        first_word = name_part.split()[0] if name_part else ""
        if first_word in self.PROVIDER_NON_NAME_WORDS:
            return False

        return True

    # Words that follow family relationships but are NOT names
    FAMILY_NON_NAME_WORDS = frozenset({
        # Status words
        'deceased', 'living', 'alive', 'dead', 'age', 'aged', 'unknown',
        'denies', 'reports', 'states', 'claims', 'says', 'noted',
        # Section headers / form words
        'for', 'and', 'or', 'with', 'has', 'had', 'is', 'was', 'are', 'were',
        'contrast', 'injection', 'exam', 'study', 'consultation', 'consult',
        'hospitalization', 'visit', 'appointment', 'procedure', 'surgery',
        # Clinical terms
        'history', 'hx', 'medical', 'surgical', 'family', 'social',
        'performed', 'drives', 'lives', 'works', 'retired', 'married',
        'divorced', 'widowed', 'single', 'separated',
        # Location/living words
        'in', 'at', 'home', 'alone', 'together', 'nearby', 'away',
        'situation', 'text', 'free',
        # Action words
        'who', 'which', 'that', 'sitting', 'standing', 'walking',
        # Age related
        'lived', 'to', 'until', 'navy', 'army', 'military', 'natural',
        # Discussion words
        'about', 'regarding', 'concerning', 'discussed', 'informed',
        'notified', 'called', 'contacted', 'updated', 'possible',
        # Generic family relationship words (not names)
        'mother', 'father', 'brother', 'sister', 'spouse', 'have', 'been',
    })

    def _validate_family_member_name(self, text: str, match: re.Match) -> bool:
        """Validate that the captured name after family relationship word is an actual name."""
        name_part = match.group(1).lower() if match.lastindex >= 1 else ""

        # Reject if the "name" is a common non-name word
        first_word = name_part.split()[0] if name_part else ""
        if first_word in self.FAMILY_NON_NAME_WORDS:
            return False

        # Reject if the whole match is in non-name words
        if name_part in self.FAMILY_NON_NAME_WORDS:
            return False

        # Also check second word if present
        words = name_part.split()
        if len(words) > 1 and words[1] in self.FAMILY_NON_NAME_WORDS:
            return False

        return True

    # Words that are NOT names when in uppercase "WORD, WORD" format
    UPPERCASE_NON_NAMES = frozenset({
        # Medical/clinical terms
        "diagnosis", "assessment", "plan", "history", "exam", "examination",
        "results", "labs", "imaging", "vitals", "medications", "allergies",
        "chief", "complaint", "progress", "note", "summary", "report",
        "admission", "discharge", "transfer", "consult", "consultation",
        # Section headers
        "subjective", "objective", "impression", "recommendation",
        "physical", "review", "systems", "social", "family",
        # Common abbreviations that appear uppercase
        "stat", "prn", "bid", "tid", "qid", "daily", "weekly",
    })

    def _validate_uppercase_name(self, text: str, match: re.Match) -> bool:
        """Validate that uppercase LAST, FIRST is a real name, not a section header."""
        first = match.group(1).lower() if match.lastindex >= 1 else ""
        second = match.group(2).lower() if match.lastindex >= 2 else ""

        # Reject known non-name words
        if first in self.UPPERCASE_NON_NAMES or second in self.UPPERCASE_NON_NAMES:
            return False

        # Reject if either word is a common medical term from the main blocklist
        if first in self.LAB_AND_MEDICAL_TERMS or second in self.LAB_AND_MEDICAL_TERMS:
            return False

        # Names should be reasonable length (3-15 chars each)
        if len(first) < 3 or len(second) < 3:
            return False

        # STRICT: Require nearby patient context - don't guess
        start = max(0, match.start() - 80)
        context = text[start:match.start()].lower()

        # Must have patient label nearby
        patient_indicators = ['patient:', 'patient ', 'name:']
        if any(ind in context for ind in patient_indicators):
            return True

        # Accept if followed immediately by MRN or DOB
        end = min(len(text), match.end() + 40)
        after = text[match.end():end].lower()
        if 'mrn:' in after or 'mrn ' in after:
            return True
        if 'dob:' in after or 'dob ' in after:
            return True
        # Account number context (eClinical format)
        if 'acc no' in after or 'account' in after:
            return True

        # Default: reject without clear context
        return False

    def _date_patterns(self) -> List[PatternDefinition]:
        """Patterns for detecting dates."""
        return [
            PatternDefinition(
                pattern=re.compile(r"\b(\d{4})[-/](\d{1,2})[-/](\d{1,2})\b"),
                phi_type="DATE",
                confidence=0.95,
                description="ISO date format"
            ),
            PatternDefinition(
                # Bracketed date format common in synthetic data (Synthea/cnotesum)
                # Matches: [2845-7-10], [2023-12-25], [1990-1-1]
                pattern=re.compile(r"\[(\d{4})-(\d{1,2})-(\d{1,2})\]"),
                phi_type="DATE",
                confidence=0.95,
                description="Bracketed date format [YYYY-M-DD]"
            ),
            PatternDefinition(
                # Require consistent separators to avoid matching pain scales like "2-4/10"
                pattern=re.compile(r"\b(\d{1,2})([-/])(\d{1,2})\2(\d{2,4})\b"),
                phi_type="DATE",
                confidence=0.90,
                validator=self._validate_us_date,
                description="US date format"
            ),
            PatternDefinition(
                # Short dates MM/DD without year (common in clinical notes)
                # Requires context: preceded by date-like words or in date-heavy areas
                pattern=re.compile(r"\b(\d{1,2})/(\d{1,2})\b"),
                phi_type="DATE",
                confidence=0.75,
                validator=self._validate_short_date,
                description="Short date MM/DD"
            ),
            PatternDefinition(
                pattern=re.compile(
                    r"\b(January|February|March|April|May|June|July|August|"
                    r"September|October|November|December|"
                    r"Jan|Feb|Mar|Apr|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec)\.?\s+"
                    r"(\d{1,2})(?:st|nd|rd|th)?\s*,?\s*(\d{2,4})\b",
                    re.IGNORECASE
                ),
                phi_type="DATE",
                confidence=0.95,
                description="Written month date"
            ),
            PatternDefinition(
                pattern=re.compile(
                    r"(?:DOB|D\.O\.B\.?|Date\s+of\s+Birth|Birth\s*date|Born)\s*"
                    r"[:#]?\s*(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})",
                    re.IGNORECASE
                ),
                phi_type="DOB",
                confidence=0.98,
                description="DOB with label"
            ),
            PatternDefinition(
                pattern=re.compile(
                    r"(?:DOB|D\.O\.B\.?|Date\s+of\s+Birth|Birth\s*date|Born)\s*"
                    r"[:#]?\s*((?:January|February|March|April|May|June|July|August|"
                    r"September|October|November|December|"
                    r"Jan|Feb|Mar|Apr|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec)\.?\s+"
                    r"\d{1,2}(?:st|nd|rd|th)?\s*,?\s*\d{2,4})",
                    re.IGNORECASE
                ),
                phi_type="DOB",
                confidence=0.98,
                description="DOB with written month"
            ),
            # Year-only dates in medical history context: "(2019)", "(2021)", "in 2019"
            PatternDefinition(
                pattern=re.compile(
                    r"(?:\(|in\s+|since\s+|from\s+)"
                    r"((?:19|20)\d{2})"
                    r"(?:\)|,|\s|$)",
                    re.IGNORECASE
                ),
                phi_type="DATE",
                confidence=0.82,
                validator=self._validate_year_date,
                description="Year-only date in context"
            ),
        ]

    def _validate_us_date(self, text: str, match: re.Match) -> bool:
        """Validate US date format to avoid false positives."""
        try:
            month = int(match.group(1))
            # Group 2 is separator, group 3 is day, group 4 is year
            day = int(match.group(3))
            year_str = match.group(4)
            year = int(year_str)
            if year < 100:
                year = 2000 + year if year < 50 else 1900 + year
            if not (1 <= month <= 12):
                return False
            if not (1 <= day <= 31):
                return False
            if not (1900 <= year <= 2100):
                return False
            return True
        except (ValueError, IndexError):
            return False

    def _validate_year_date(self, text: str, match: re.Match) -> bool:
        """Validate year-only dates in medical history context."""
        year = int(match.group(1))

        # Reasonable medical history years (1950-2030)
        if not (1950 <= year <= 2030):
            return False

        # Check context - should be in medical history, not a reference number
        start = max(0, match.start() - 80)
        end = min(len(text), match.end() + 40)
        context = text[start:end].lower()

        # Reject if looks like a reference/code context
        code_indicators = ['ref', 'code', 'icd', 'cpt', 'version', 'v.', 'edition']
        if any(ind in context for ind in code_indicators):
            return False

        # Accept if in medical history context
        history_indicators = ['s/p', 'status post', 'history', 'diagnosed', 'surgery',
                            'procedure', 'admitted', 'hospitalized', 'onset', 'since',
                            'cabg', 'mvr', 'avr', 'stent', 'ablation', 'cardioversion']
        if any(ind in context for ind in history_indicators):
            return True

        # Accept if in parentheses (common medical history format)
        matched_text = match.group()
        if '(' in matched_text or ')' in text[match.end():match.end()+2]:
            return True

        return False

    def _validate_short_date(self, text: str, match: re.Match) -> bool:
        """
        Validate short MM/DD dates to avoid blood pressure and other FPs.

        Short dates are tricky because:
        - 11/5 could be November 5th (date) or 11:05 time
        - 120/80 is blood pressure, not a date
        - 4/10 could be April 10th or a fraction/score
        """
        try:
            month = int(match.group(1))
            day = int(match.group(2))

            # Must be valid month (1-12) and day (1-31)
            if not (1 <= month <= 12 and 1 <= day <= 31):
                return False

            # Check context to disambiguate
            start = match.start()
            end = match.end()

            # Get surrounding context (50 chars before and after)
            context_start = max(0, start - 50)
            context_end = min(len(text), end + 50)
            context = text[context_start:context_end].lower()

            # Reject if preceded by BP/blood pressure indicators
            bp_indicators = ['bp', 'b/p', 'blood pressure', 'sbp', 'dbp', 'map']
            pre_context = text[context_start:start].lower()
            if any(ind in pre_context for ind in bp_indicators):
                return False

            # Reject if followed by mmHg or similar
            post_context = text[end:context_end].lower()
            if 'mmhg' in post_context or 'mm hg' in post_context:
                return False

            # Reject clinical grades/scores (4/5, 3/6, etc.)
            # Context indicators: "grade", "strength", "motor", "power", "/5", "/6"
            grade_indicators = ['grade', 'strength', 'motor', 'power', 'weakness', 'paresis', 'hemiparesis']
            if any(ind in pre_context for ind in grade_indicators):
                return False
            # Also check if denominator is 5 or 6 (common clinical scales)
            if day in (5, 6) and month <= day:  # X/5 or X/6 where X <= denominator
                return False

            # Accept if preceded by date-related words
            date_indicators = [
                'date', 'on ', 'since', 'from', 'until', 'through', 'as of',
                'dated', 'effective', 'admit', 'discharge', 'd/c', 'seen',
                'scheduled', 'appointment', 'follow', 'f/u', 'returned',
                'presented', 'admitted', 'consult', 'procedure',
            ]
            if any(ind in pre_context for ind in date_indicators):
                return True

            # Accept if it looks like a timestamp context (dates with times)
            # Handles: HH:MM, HHMM (military time like 0517), or times with am/pm
            time_pattern = re.compile(
                r'^\s*'  # Allow leading whitespace
                r'('
                r'\d{1,2}:\d{2}'  # HH:MM format
                r'|'
                r'\d{4}'  # Military time HHMM (e.g., 0517, 1430)
                r'|'
                r'\d{1,2}\s*(am|pm)'  # Simple am/pm times
                r')',
                re.IGNORECASE
            )
            if time_pattern.search(post_context[:20]):
                return True

            # Accept if there's a "Date" column header nearby (table context)
            # Look for Date/time, Date:, etc. within 200 chars before
            extended_pre = text[max(0, start - 200):start].lower()
            if 'date/time' in extended_pre or 'date\t' in extended_pre or 'date ' in context:
                return True

            # Accept if there are other dates nearby (date-heavy section)
            other_dates = re.findall(r'\d{1,2}/\d{1,2}/\d{2,4}', context)
            if len(other_dates) >= 1:
                return True

            # Default: accept if in first half of note (more likely header/dates)
            # or reject if we're unsure
            if start < len(text) * 0.3:
                return True

            return False

        except (ValueError, IndexError):
            return False

    def _age_patterns(self) -> List[PatternDefinition]:
        """Patterns for detecting ages."""
        return [
            PatternDefinition(
                # "44 y/o", "44 yo", "44 year old", "44 years old", "44 yr old"
                pattern=re.compile(
                    r"\b(\d{1,3})\s*[-]?\s*"
                    r"(y/?o|yo|year[s]?\s*old|yr[s]?\s*old|year[s]?\s+of\s+age)\b",
                    re.IGNORECASE
                ),
                phi_type="AGE",
                confidence=0.95,
                description="Age in years"
            ),
            PatternDefinition(
                # "44 year old male", "65 yo female", "32 y/o M"
                pattern=re.compile(
                    r"\b(\d{1,3})\s*[-]?\s*"
                    r"(y/?o|yo|year[s]?\s*old|yr[s]?\s*old)\s+"
                    r"(?:male|female|man|woman|gentleman|lady|m|f)\b",
                    re.IGNORECASE
                ),
                phi_type="AGE",
                confidence=0.95,
                description="Age with gender"
            ),
            PatternDefinition(
                # Hyphenated format: "71-year-old", "65-yr-old"
                pattern=re.compile(
                    r"\b(\d{1,3})-(year|yr)-old\b",
                    re.IGNORECASE
                ),
                phi_type="AGE",
                confidence=0.95,
                description="Age hyphenated format"
            ),
            PatternDefinition(
                # "age 44", "aged 65", "at age 32"
                pattern=re.compile(
                    r"\b(?:age[d]?|at\s+age)\s*[:#]?\s*(\d{1,3})\b",
                    re.IGNORECASE
                ),
                phi_type="AGE",
                confidence=0.95,
                validator=self._validate_age_context,
                description="Age with label"
            ),
            PatternDefinition(
                # "18 mo", "6 month old", "3 months old"
                pattern=re.compile(
                    r"\b(\d{1,2})\s*[-]?\s*(m/?o|month[s]?\s*old)\b",
                    re.IGNORECASE
                ),
                phi_type="AGE",
                confidence=0.95,
                validator=self._validate_not_lab_value,
                description="Age in months"
            ),
            PatternDefinition(
                # "This 44-year-old", "a 65 year-old"
                pattern=re.compile(
                    r"\b(?:this|a|the)\s+(\d{1,3})[\s-]*(year|yr)[\s-]*old\b",
                    re.IGNORECASE
                ),
                phi_type="AGE",
                confidence=0.95,
                description="Age with article"
            ),
            # OBI-inspired: Fused age patterns - catches typos like "Plan88yo", "Assessment65yoM"
            PatternDefinition(
                pattern=re.compile(
                    r"(?<=[a-zA-Z])(\d{1,3})"
                    r"(y/?o|yo|yr|y\.o|y/o)"
                    r"(?:[mMfF](?:ale)?)?(?:\W|$)",
                    re.IGNORECASE
                ),
                phi_type="AGE",
                confidence=0.90,
                description="Fused age (OBI pattern)"
            ),
            # OBI-inspired: Gender prefix with age - "M45", "F32"
            PatternDefinition(
                pattern=re.compile(
                    r"\b([MFmf])(\d{2,3})(?:\W|$)"
                ),
                phi_type="AGE",
                confidence=0.85,
                validator=self._validate_gender_age,
                description="Gender prefix age"
            ),
        ]

    def _validate_gender_age(self, text: str, match: re.Match) -> bool:
        """Validate that M45/F32 is a gender+age, not a code or medication."""
        age = int(match.group(2))
        # Age should be reasonable (1-120)
        if not (1 <= age <= 120):
            return False
        # Check surrounding context - reject if looks like a code
        start = max(0, match.start() - 20)
        end = min(len(text), match.end() + 20)
        context = text[start:end].lower()
        # Reject if looks like ICD/CPT codes (e.g., "M54.5", "F32.1", "M62.")
        # The pattern may consume the period in (?:\W|$), so check the full match
        full_match = match.group()
        if '.' in full_match:
            return False
        # Also check character immediately after the digits
        digit_end = match.start() + 1 + len(match.group(2))  # M + digits
        if digit_end < len(text) and text[digit_end] == '.':
            return False
        # Reject if in code-like context
        code_indicators = ['icd', 'cpt', 'code', 'diagnosis', 'dx:']
        if any(ind in context for ind in code_indicators):
            return False
        return True

    def _validate_phone_context(self, text: str, match: re.Match) -> bool:
        """Validate that a 10-digit number is likely a phone, not an ID/MRN."""
        phone = match.group()

        # Check surrounding context
        start = max(0, match.start() - 30)
        end = min(len(text), match.end() + 30)
        context = text[start:end].lower()

        # Positive indicators - likely a phone
        phone_indicators = ['phone', 'tel', 'call', 'cell', 'mobile', 'contact', 'fax', 'reach']
        if any(ind in context for ind in phone_indicators):
            return True

        # Negative indicators - likely an ID/MRN
        # Surrounded by / or | delimiters (common in EHR lists)
        before_char = text[match.start()-1] if match.start() > 0 else ''
        after_char = text[match.end()] if match.end() < len(text) else ''
        if before_char in '/|' or after_char in '/|':
            return False

        # If no formatting (just 10 digits), require phone context
        if phone.isdigit() and len(phone) == 10:
            # No dashes/dots/parens = probably not a phone number
            return False

        return True

    def _validate_age_context(self, text: str, match: re.Match) -> bool:
        """Validate that 'age X' is a patient age, not stage/grade number."""
        age = int(match.group(1) if match.group(1) else match.group(0).split()[-1])
        # Very low numbers (1-5) after "age" are often stages, not ages
        # Unless followed by patient context words
        if age <= 5:
            # Check for patient context
            after = text[match.end():match.end()+30].lower()
            patient_words = ["male", "female", "patient", "woman", "man", "child", "infant"]
            return any(w in after for w in patient_words)
        return True

    def _validate_not_lab_value(self, text: str, match: re.Match) -> bool:
        """Validate that 'X mo' is an age, not a lab value like mosm/kg."""
        end = match.end()
        after = text[end:end+10].lower()
        # Check for lab value indicators
        if after.startswith("sm") or after.startswith("l/"):  # mosm, mol/L
            return False
        return True

    def _ssn_patterns(self) -> List[PatternDefinition]:
        """Patterns for detecting Social Security Numbers."""
        return [
            PatternDefinition(
                pattern=re.compile(
                    r"(?:SSN|SS#?|Social\s*Security(?:\s*(?:Number|No\.?|#))?)\s*"
                    r"[:#]?\s*(\d{3}[-\s]?\d{2}[-\s]?\d{4})",
                    re.IGNORECASE
                ),
                phi_type="SSN",
                confidence=0.98,
                description="SSN with label"
            ),
            PatternDefinition(
                pattern=re.compile(r"\b(\d{3})[-](\d{2})[-](\d{4})\b"),
                phi_type="SSN",
                confidence=0.85,
                validator=self._validate_ssn_format,
                description="SSN format"
            ),
        ]

    def _validate_ssn_format(self, text: str, match: re.Match) -> bool:
        """Validate SSN format and context."""
        area = int(match.group(1))
        group = int(match.group(2))
        serial = int(match.group(3))
        if area == 0 or area == 666 or area >= 900:
            return False
        if group == 0:
            return False
        if serial == 0:
            return False
        start = max(0, match.start() - 50)
        end = min(len(text), match.end() + 20)
        context = text[start:end].lower()
        ssn_terms = ["ssn", "social", "security", "ss#", "ss #", "ss:", "ssn:"]
        return any(term in context for term in ssn_terms)

    def _mrn_patterns(self) -> List[PatternDefinition]:
        """Patterns for detecting Medical Record Numbers."""
        return [
            PatternDefinition(
                pattern=re.compile(
                    r"(?:MRN|MR#?|Med(?:ical)?\s*Rec(?:ord)?(?:\s*(?:Number|No\.?|#))?|"
                    r"Patient\s*ID|Chart\s*(?:Number|No\.?|#)?)\s*"
                    r"[:#]?\s*([A-Z0-9]{5,15})",
                    re.IGNORECASE
                ),
                phi_type="MRN",
                confidence=0.95,
                validator=lambda text, match: any(c.isdigit() for c in match.group(1)),
                description="MRN with label"
            ),
            # eClinical Account Number format: "Account Number: 61852"
            PatternDefinition(
                pattern=re.compile(
                    r"Account\s*Number\s*[:#]?\s*(\d{4,8})\b",
                    re.IGNORECASE
                ),
                phi_type="MRN",
                confidence=0.92,
                description="Account number label"
            ),
            PatternDefinition(
                pattern=re.compile(r"\b([EZ]\d{7,10})\b"),
                phi_type="MRN",
                confidence=0.90,
                description="Epic MRN format"
            ),
            # Generic ID format: Letter prefix + 7-10 digits (N000252302, A12345678)
            # Common in Meditech, Cerner, and other EHR systems
            PatternDefinition(
                pattern=re.compile(r"\b([A-Z]\d{7,10})\b"),
                phi_type="MRN",
                confidence=0.88,
                validator=self._validate_letter_digit_mrn,
                description="Letter prefix MRN format"
            ),
            # Standalone #: followed by alphanumeric ID (catches "PATIENT: Name #: N000252302")
            PatternDefinition(
                pattern=re.compile(r"#:\s*([A-Z0-9]{6,15})\b", re.IGNORECASE),
                phi_type="ACCOUNT_NUMBER",
                confidence=0.90,
                validator=lambda text, match: any(c.isdigit() for c in match.group(1)),
                description="Hash-colon ID format"
            ),
            # OBI-inspired: Pager/beeper ID pattern - catches "p4986231", "x12345"
            PatternDefinition(
                pattern=re.compile(
                    r"(?:pager|beeper|ext\.?|extension)\s*[:#]?\s*"
                    r"([pPxXbB]?\d{4,}|\d+[-]\d+)",
                    re.IGNORECASE
                ),
                phi_type="OTHER_PHI",
                confidence=0.88,
                description="Pager/extension number"
            ),
            # OBI-inspired: Standalone pager prefix pattern
            PatternDefinition(
                pattern=re.compile(r"\b([pPxX])(\d{5,})\b"),
                phi_type="OTHER_PHI",
                confidence=0.82,
                validator=self._validate_pager_not_medication,
                description="Pager ID prefix"
            ),
        ]

    def _validate_pager_not_medication(self, text: str, match: re.Match) -> bool:
        """Validate that pXXXX is a pager ID, not a medication dosage."""
        # Check surrounding context for medication indicators
        start = max(0, match.start() - 30)
        end = min(len(text), match.end() + 20)
        context = text[start:end].lower()
        # Reject if looks like prescription dosage context
        med_indicators = ['mg', 'mcg', 'ml', 'units', 'tabs', 'caps', 'prn', 'bid', 'tid', 'qid']
        if any(ind in context for ind in med_indicators):
            return False
        return True

    def _validate_letter_digit_mrn(self, text: str, match: re.Match) -> bool:
        """
        Validate that a letter+digits pattern is likely an MRN, not a code or abbreviation.

        Accepts patterns like N000252302, A12345678 when they appear in ID-like contexts.
        Rejects medical codes like T1234567, V12345678, ICD codes, etc.
        """
        matched = match.group(1)
        letter = matched[0].upper()

        # Reject known medical code prefixes
        # T, V, W, X, Y, Z are commonly used for ICD-10 codes
        # S is used for injury codes
        # Skip E and Z which are Epic MRN formats (handled separately)
        if letter in {'T', 'V', 'W', 'X', 'Y', 'S'}:
            return False

        # Check context for ID-like indicators
        start = max(0, match.start() - 50)
        end = min(len(text), match.end() + 30)
        context = text[start:end].lower()

        # Positive indicators - likely an MRN/account number
        id_indicators = ['patient', 'mrn', 'record', 'chart', 'acct', 'account', '#:', 'id:']
        if any(ind in context for ind in id_indicators):
            return True

        # Reject if in diagnosis/procedure code context
        code_indicators = ['icd', 'cpt', 'hcpcs', 'diagnosis', 'dx:', 'procedure']
        if any(ind in context for ind in code_indicators):
            return False

        # Accept if it starts with N, M, P, R, A, C (common MRN prefixes)
        if letter in {'N', 'M', 'P', 'R', 'A', 'C'}:
            return True

        return False

    def _validate_long_numeric_id(self, text: str, match: re.Match) -> bool:
        """
        Validate that a 10-15 digit number is likely an ID, not a measurement or phone.

        Accepts student IDs, employee IDs, and similar long numeric identifiers.
        Rejects phone numbers (already matched by phone patterns), dates, and
        numbers in measurement contexts.
        """
        number = match.group(1)
        start = max(0, match.start() - 40)
        end = min(len(text), match.end() + 40)
        context = text[start:end].lower()

        # Reject if it looks like a phone number format (already caught by phone patterns)
        # Check for common phone indicators
        phone_indicators = ['phone', 'tel', 'call', 'cell', 'mobile', 'fax', 'contact']
        if any(ind in context for ind in phone_indicators):
            return False

        # Reject if preceded by common measurement or financial contexts
        measurement_indicators = ['$', 'usd', 'eur', 'gbp', 'total', 'amount', 'balance',
                                  'cost', 'price', 'fee', 'charge', 'payment']
        if any(ind in context for ind in measurement_indicators):
            return False

        # Reject if looks like a date (has slashes/dashes in number position)
        # e.g., don't match "20231215" as a date - but these would be <10 digits anyway

        # Accept if preceded by ID-related context
        id_indicators = ['id', 'number', 'no.', '#', 'student', 'employee', 'badge',
                        'member', 'account', 'record', 'identifier']
        if any(ind in context for ind in id_indicators):
            return True

        # For general long numbers without context, accept with lower confidence
        # The confidence is already 0.75 so we let them through
        return True

    def _medicare_patterns(self) -> List[PatternDefinition]:
        """Patterns for detecting Medicare/Medicaid identifiers."""
        return [
            PatternDefinition(
                pattern=re.compile(
                    r"\b([1-9][AC-HJKMNP-RT-Y][AC-HJKMNP-RT-Y0-9]\d"
                    r"[AC-HJKMNP-RT-Y][AC-HJKMNP-RT-Y0-9]\d"
                    r"[AC-HJKMNP-RT-Y]{2}\d{2})\b"
                ),
                phi_type="MEDICARE_ID",
                confidence=0.92,
                description="Medicare MBI format"
            ),
            PatternDefinition(
                pattern=re.compile(
                    r"(?:Medicare|Medicaid|MBI|HICN)\s*"
                    r"(?:(?:ID|Number|No\.?|#)\s*)?[:#]?\s*"
                    r"([A-Z0-9]{10,12})",
                    re.IGNORECASE
                ),
                phi_type="MEDICARE_ID",
                confidence=0.95,
                description="Medicare/Medicaid with label"
            ),
        ]

    def _phone_patterns(self) -> List[PatternDefinition]:
        """Patterns for detecting phone and fax numbers."""
        return [
            PatternDefinition(
                pattern=re.compile(
                    r"(?:phone|telephone|tel|cell|mobile|fax|pager)\s*"
                    r"(?:(?:number|no\.?|#)\s*)?[:#]?\s*"
                    r"((?:\+?1[-.\s]?)?(?:\(?\d{3}\)?[-.\s]?)?\d{3}[-.\s]?\d{4})",
                    re.IGNORECASE
                ),
                phi_type="PHONE",
                confidence=0.95,
                description="Phone with label"
            ),
            PatternDefinition(
                pattern=re.compile(
                    r"\b(?:\+?1[-.\s]?)?"
                    r"(?:\(?\d{3}\)?[-.\s]?)"
                    r"\d{3}[-.\s]?\d{4}\b"
                ),
                phi_type="PHONE",
                confidence=0.88,
                validator=self._validate_phone_context,
                description="US phone number"
            ),
            PatternDefinition(
                pattern=re.compile(
                    r"(?:fax|facsimile)\s*(?:(?:number|no\.?|#)\s*)?[:#]?\s*"
                    r"((?:\+?1[-.\s]?)?(?:\(?\d{3}\)?[-.\s]?)?\d{3}[-.\s]?\d{4})",
                    re.IGNORECASE
                ),
                phi_type="FAX",
                confidence=0.95,
                description="Fax with label"
            ),
        ]

    def _email_patterns(self) -> List[PatternDefinition]:
        """Patterns for detecting email addresses."""
        return [
            PatternDefinition(
                pattern=re.compile(
                    r"\b([A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,})\b"
                ),
                phi_type="EMAIL",
                confidence=0.95,
                description="Email address"
            ),
        ]

    def _address_patterns(self) -> List[PatternDefinition]:
        """Patterns for detecting addresses."""
        return [
            PatternDefinition(
                pattern=re.compile(
                    r"\b(\d+\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s+"
                    r"(?:Street|St|Avenue|Ave|Boulevard|Blvd|Drive|Dr|Road|Rd|"
                    r"Lane|Ln|Way|Court|Ct|Circle|Cir|Place|Pl|Parkway|Pkwy|"
                    r"Highway|Hwy|Trail|Trl|Terrace|Ter))\.?\b",
                    re.IGNORECASE
                ),
                phi_type="STREET_ADDRESS",
                confidence=0.92,
                validator=self._validate_street_address,
                description="Street address"
            ),
            PatternDefinition(
                pattern=re.compile(
                    r"\b(P\.?O\.?\s*Box\s*\d+)\b",
                    re.IGNORECASE
                ),
                phi_type="STREET_ADDRESS",
                confidence=0.95,
                description="PO Box"
            ),
            PatternDefinition(
                # Handles: "Boston, MA 02101", "CLEARWATER, FL-33756-4401", "New York, NY 10001-1234"
                pattern=re.compile(
                    r"\b([A-Z][A-Za-z]+(?:\s+[A-Z][A-Za-z]+)?)\s*,\s*"
                    r"([A-Z]{2})[-\s]+(\d{5}(?:-\d{4})?)\b"
                ),
                phi_type="CITY_STATE_ZIP",
                confidence=0.95,
                description="City, State ZIP"
            ),
        ]

    def _professional_id_patterns(self) -> List[PatternDefinition]:
        """Patterns for detecting professional licenses and IDs."""
        return [
            PatternDefinition(
                pattern=re.compile(
                    r"(?:NPI|National\s*Provider(?:\s*Identifier)?)\s*"
                    r"[:#]?\s*(\d{10})\b",
                    re.IGNORECASE
                ),
                phi_type="NPI",
                confidence=0.95,
                description="NPI"
            ),
            PatternDefinition(
                pattern=re.compile(
                    r"(?:DEA|Drug\s*Enforcement)\s*"
                    r"(?:(?:Number|No\.?|#)\s*)?[:#]?\s*"
                    r"([A-Z]{2}\d{7})\b",
                    re.IGNORECASE
                ),
                phi_type="DEA_NUMBER",
                confidence=0.95,
                description="DEA number"
            ),
        ]

    def _device_vehicle_patterns(self) -> List[PatternDefinition]:
        """Patterns for detecting device and vehicle identifiers."""
        return [
            PatternDefinition(
                pattern=re.compile(
                    r"(?:UDI|Unique\s*Device\s*Identifier|Device\s*ID)\s*"
                    r"[:#]?\s*([A-Z0-9\-]{10,})\b",
                    re.IGNORECASE
                ),
                phi_type="DEVICE_ID",
                confidence=0.90,
                description="Device identifier"
            ),
            PatternDefinition(
                pattern=re.compile(
                    r"(?:VIN|Vehicle\s*Identification)\s*"
                    r"[:#]?\s*([A-HJ-NPR-Z0-9]{17})\b",
                    re.IGNORECASE
                ),
                phi_type="VEHICLE_ID",
                confidence=0.95,
                description="VIN"
            ),
        ]

    def _web_patterns(self) -> List[PatternDefinition]:
        """Patterns for detecting URLs and IP addresses."""
        return [
            PatternDefinition(
                pattern=re.compile(r"\b(https?://[^\s<>\"]+)\b"),
                phi_type="URL",
                confidence=0.95,
                description="URL with protocol"
            ),
            PatternDefinition(
                pattern=re.compile(
                    r"\b((?:25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)"
                    r"(?:\.(?:25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3})\b"
                ),
                phi_type="IP_ADDRESS",
                confidence=0.90,
                description="IPv4 address"
            ),
        ]

    def _clinical_location_patterns(self) -> List[PatternDefinition]:
        """Patterns for detecting clinical locations."""
        return [
            PatternDefinition(
                pattern=re.compile(
                    # Room/bed with explicit separator or number
                    r"\b(?:Room|Rm)\s*[:#]\s*([A-Z]?\d{1,4}[A-Z]?)\b"
                    r"|\b(?:Bed)\s*[:#]\s*(\d{1,3}[A-Z]?)\b"
                    r"|\bUnit\s+(\d{1,2}[A-Z]?)\b"
                    # EHR header format: ROOM/BED: SM.416-1
                    r"|\b(?:ROOM/BED|ROOM-BED)\s*:\s*([A-Z]{1,3}\.?\d{1,4}(?:-\d{1,2})?)\b"
                    # UNIT #: M000888636 (unit identifier)
                    r"|\bUNIT\s*[#:]?\s*:?\s*([A-Z]?\d{6,12})\b",
                    re.IGNORECASE
                ),
                phi_type="ROOM_BED",
                confidence=0.88,
                # Exclude common phrases like "bedtime", "room air", "bedroom"
                validator=lambda text, match: not any(x in text.lower() for x in [
                    'bedtime', 'bedroom', 'room air', 'room temperature'
                ]),
                description="Room/Bed number"
            ),
            PatternDefinition(
                # Use [ \t]+ instead of \s+ to prevent matching across newlines
                pattern=re.compile(
                    r"\b([A-Z][a-z]+(?:[ \t]+[A-Z][a-z]+)*[ \t]+"
                    r"(?:Hospital|Medical[ \t]*Center|Clinic|"
                    r"Health[ \t]*(?:Center|System)|"
                    r"Regional|Memorial|General|Community))\b"
                ),
                phi_type="FACILITY",
                confidence=0.85,
                validator=self._validate_facility_name,
                description="Facility name"
            ),
        ]

    def _validate_facility_name(self, text: str, match: re.Match) -> bool:
        """Validate that matched text is a real facility name, not a section header."""
        matched_text = match.group().lower()
        # Reject common section headers that look like facility names
        false_facility_phrases = [
            "brief hospital",  # "Brief Hospital Course"
            "current hospital",  # Generic
            "outside hospital",  # "outside hospital records"
            "prior hospital",
            "previous hospital",
        ]
        return matched_text not in false_facility_phrases

    def _validate_street_address(self, text: str, match: re.Match) -> bool:
        """Validate that matched text is a real address, not a clinical measurement."""
        matched = match.group()

        # Get surrounding context
        start = max(0, match.start() - 50)
        end = min(len(text), match.end() + 50)
        context = text[start:end].lower()

        # Reject if starts with measurement indicators (e.g., "4 cm")
        measurement_pattern = re.compile(r'^\d+\s*(cm|mm|ml|mg|kg|lb|inch|in|ft|meter)', re.IGNORECASE)
        if measurement_pattern.match(matched):
            return False

        # Reject if contains newlines - real addresses don't span lines like "4\n\nPlan"
        if '\n' in matched:
            return False

        # Reject if in clinical measurement context
        measurement_indicators = ['measuring', 'measured', 'cm ', 'mm ', 'size', 'diameter', 'length', 'mass']
        if any(ind in context for ind in measurement_indicators):
            return False

        # Reject if followed by clinical section headers
        section_indicators = ['plan', 'assessment', 'seen and examined', 'alert to', 'admit', 'consult']
        after = text[match.end():end].lower()
        if any(ind in after[:20] for ind in section_indicators):
            return False

        # Reject if matched text contains clinical terms (not address parts)
        clinical_terms = ['toe', 'dose', 'antibiotic', 'consult', 'planning', 'diagnosis', 'extremity']
        if any(term in matched.lower() for term in clinical_terms):
            return False

        return True

    def _account_patterns(self) -> List[PatternDefinition]:
        """Patterns for detecting account and other identifiers."""
        return [
            PatternDefinition(
                pattern=re.compile(
                    # Require explicit separator for account numbers
                    r"(?:Account|Acct?|Visit|Encounter|FIN|Case|Episode)\s*"
                    r"(?:Number|No\.?|#|ID)?\s*[:#]\s*"
                    r"([A-Z0-9]{6,15})\b",
                    re.IGNORECASE
                ),
                phi_type="ACCOUNT_NUMBER",
                confidence=0.90,
                # Exclude words that look like account numbers
                validator=lambda text, match: match.group(1).lower() not in {
                    'ant', 'ants', 'ability', 'able', 'ing', 'ment', 'ation'
                } and not text.lower().startswith('accounta'),
                description="Account number"
            ),
            # Standalone long numeric IDs (10-15 digits) - student IDs, employee IDs, etc.
            # These are commonly used as personal identifiers and should be flagged
            PatternDefinition(
                pattern=re.compile(r"\b(\d{10,15})\b"),
                phi_type="OTHER_ID",
                confidence=0.75,
                validator=self._validate_long_numeric_id,
                description="Long numeric ID (10-15 digits)"
            ),
            PatternDefinition(
                # Added word boundaries to prevent matching "No" from words like "Nonischemic"
                pattern=re.compile(
                    r"(?:Insurance|Policy|Member|Subscriber|Group)\s*"
                    r"(?:(?:Number\b|No\.?\b|#|ID\b)\s*)?[:#]?\s*"
                    r"([A-Z0-9]{6,20})\b",
                    re.IGNORECASE
                ),
                phi_type="INSURANCE_ID",
                confidence=0.88,
                description="Insurance ID"
            ),
            PatternDefinition(
                # Payer ID - common in insurance contexts, can be 5+ digits
                # Require ID/No/# after Payer/Payor to avoid matching "Plan: Diagnosis"
                # Added \b after ID/No to prevent matching "No" from words like "Nonischemic"
                pattern=re.compile(
                    r"(?:Payer|Payor)\s*(?:ID\b|#|No\.?\b)\s*[:#]?\s*"
                    r"([A-Z0-9]{4,15})\b",
                    re.IGNORECASE
                ),
                phi_type="INSURANCE_ID",
                confidence=0.90,
                description="Payer ID"
            ),
            PatternDefinition(
                # Plan ID - only match if followed by ID/# and alphanumeric code
                # Added \b after ID/No to prevent matching "No" from "Nonischemic"
                pattern=re.compile(
                    r"Plan\s*(?:ID\b|#|No\.?\b)\s*[:#]?\s*"
                    r"([A-Z0-9]{4,15})\b",
                    re.IGNORECASE
                ),
                phi_type="INSURANCE_ID",
                confidence=0.88,
                description="Plan ID"
            ),
        ]

    def _username_patterns(self) -> List[PatternDefinition]:
        """Patterns for detecting usernames and user IDs."""
        return [
            # Labeled username: "Username: jsmith", "User ID: john.doe"
            PatternDefinition(
                pattern=re.compile(
                    r"(?:Username|User\s*ID|User\s*Name|Login|Login\s*ID)\s*[:#]?\s*"
                    r"([A-Za-z][A-Za-z0-9._-]{2,20})\b",
                    re.IGNORECASE
                ),
                phi_type="USERNAME",
                confidence=0.92,
                description="Labeled username"
            ),
            # EHR system user codes (like PHLABSA, PHBARBR1) - typically 6-10 uppercase letters/numbers
            # These appear in "Impression By: PHLABSA - Name" patterns
            # Require PH prefix (common in EHR systems) to be more specific
            PatternDefinition(
                pattern=re.compile(
                    r"(?:Impression|Interpreted|Read)\s+By\s*:\s*"
                    r"(PH[A-Z0-9]{4,8})\s*-"
                ),
                phi_type="USERNAME",
                confidence=0.90,
                description="EHR user code signature"  # "signature" enables group extraction
            ),
            # Authored by / Created by patterns
            PatternDefinition(
                pattern=re.compile(
                    r"(?:Authored|Created|Modified|Updated|Entered)\s+[Bb]y\s*:\s*"
                    r"([A-Za-z][A-Za-z0-9._-]{2,20})\b",
                    re.IGNORECASE
                ),
                phi_type="USERNAME",
                confidence=0.88,
                description="Author username"
            ),
            # Generic ID patterns - catch 5-12 char alphanumeric strings after ID-like labels
            # Covers: "User ID: ABC123", "Login: jsmith01", "ID: X12345678"
            PatternDefinition(
                pattern=re.compile(
                    r"(?:User\s*ID|Login\s*ID|Login|Account\s*ID|Staff\s*ID|"
                    r"Employee\s*ID|Badge\s*ID|System\s*ID|Session\s*ID)\s*[:#]?\s*"
                    r"([A-Za-z0-9._-]{5,12})\b",
                    re.IGNORECASE
                ),
                phi_type="USERNAME",
                confidence=0.88,
                description="Generic ID label"
            ),
            # Operator/technician ID patterns - require explicit separator
            PatternDefinition(
                pattern=re.compile(
                    r"(?:Operator|Technician|Tech\b|Clerk)\s+"
                    r"(?:ID|Code|#)?\s*[:#]\s*"
                    r"([A-Za-z0-9]{4,10})\b",
                    re.IGNORECASE
                ),
                phi_type="USERNAME",
                confidence=0.85,
                description="Operator ID"
            ),
        ]
