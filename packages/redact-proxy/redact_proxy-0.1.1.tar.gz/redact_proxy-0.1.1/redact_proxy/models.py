"""Shared data models for PHI detection."""

from dataclasses import dataclass, field
from typing import Optional, Set


@dataclass
class Finding:
    """A detected PHI instance."""
    text: str
    phi_type: str
    start: int
    end: int
    confidence: float
    source: str = "patterns"

    def __hash__(self):
        return hash((self.start, self.end, self.phi_type))

    def __eq__(self, other):
        if not isinstance(other, Finding):
            return False
        return (self.start, self.end, self.phi_type) == (other.start, other.end, other.phi_type)
