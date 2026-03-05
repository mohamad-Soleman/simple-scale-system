"""
Parse weight from scale serial lines.
Expected format: WGT:0 1.988P 0.000  → weight = 1.988 kg
"""
import logging

logger = logging.getLogger(__name__)


def parse_weight_line(line: str) -> float | None:
    """
    Parse weight (kg) from a line like "WGT:0 1.988P 0.000".
    Returns None if line is invalid.
    """
    parts = line.split()
    if len(parts) < 2:
        return None
    token = parts[1].strip().rstrip("P")
    try:
        return float(token)
    except ValueError:
        return None
