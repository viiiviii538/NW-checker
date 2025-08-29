from dataclasses import dataclass
from typing import Iterable

# Mapping of severity levels to numeric scores
_SEVERITY_SCORES = {
    "info": 0,
    "low": 1,
    "medium": 5,
    "high": 10,
    "critical": 20,
}


def compute_score(severity: str) -> int:
    """Return the numeric score for a given severity level."""
    return _SEVERITY_SCORES.get(severity.lower(), 0)


@dataclass
class ScanResult:
    """Common result container returned by scan modules."""

    category: str
    message: str
    score: int
    severity: str

    @classmethod
    def from_severity(cls, category: str, message: str, severity: str) -> "ScanResult":
        """Create a :class:`ScanResult` computing the score from *severity*."""
        return cls(
            category=category,
            message=message,
            severity=severity,
            score=compute_score(severity),
        )


def compute_total(results: Iterable[ScanResult]) -> int:
    """Aggregate total score from an iterable of :class:`ScanResult`."""
    return sum(r.score for r in results)
