"""
RepSense AI - Angle Calculator Module
Biomechanical joint angle computation using vector mathematics.
"""

import numpy as np
from typing import Tuple


def calculate_angle(
    point_a: Tuple[float, float],
    point_b: Tuple[float, float],
    point_c: Tuple[float, float],
) -> float:
    """
    Calculate the angle at point_b formed by vectors b->a and b->c.

    Uses the dot product formula:
        cos(θ) = (BA · BC) / (|BA| * |BC|)

    Args:
        point_a: First point (x, y)
        point_b: Vertex point (x, y) — angle measured here
        point_c: Third point (x, y)

    Returns:
        Angle in degrees (0–180)
    """
    a = np.array(point_a, dtype=float)
    b = np.array(point_b, dtype=float)
    c = np.array(point_c, dtype=float)

    ba = a - b
    bc = c - b

    norm_ba = np.linalg.norm(ba)
    norm_bc = np.linalg.norm(bc)

    if norm_ba == 0 or norm_bc == 0:
        return 0.0

    cosine_angle = np.dot(ba, bc) / (norm_ba * norm_bc)
    cosine_angle = np.clip(cosine_angle, -1.0, 1.0)
    angle = np.degrees(np.arccos(cosine_angle))
    return round(float(angle), 2)


def calculate_spine_angle(
    shoulder: Tuple[float, float],
    hip: Tuple[float, float],
    ankle: Tuple[float, float],
) -> float:
    """
    Calculate the alignment angle of the spine/body during push-up.
    Perfect plank = ~180 degrees (straight line).
    """
    return calculate_angle(shoulder, hip, ankle)


def calculate_body_alignment_deviation(
    shoulder: Tuple[float, float],
    hip: Tuple[float, float],
    ankle: Tuple[float, float],
) -> float:
    """
    Returns the deviation from perfect body alignment (180 degrees).
    Lower is better. > 20 degrees is poor form.
    """
    angle = calculate_spine_angle(shoulder, hip, ankle)
    return abs(180.0 - angle)


def smooth_angle(current: float, previous: float, alpha: float = 0.7) -> float:
    """
    Exponential moving average smoothing for angle values.
    alpha: smoothing factor (higher = more responsive, less smooth)
    """
    return alpha * current + (1 - alpha) * previous


class AngleBuffer:
    """
    Maintains a rolling buffer of angle readings for noise reduction.
    """

    def __init__(self, buffer_size: int = 5):
        self.buffer_size = buffer_size
        self._buffer = []

    def add(self, angle: float) -> float:
        """Add new angle and return smoothed value."""
        self._buffer.append(angle)
        if len(self._buffer) > self.buffer_size:
            self._buffer.pop(0)
        return self.get_smoothed()

    def get_smoothed(self) -> float:
        """Return median of buffer (robust to outliers)."""
        if not self._buffer:
            return 0.0
        return float(np.median(self._buffer))

    def reset(self):
        self._buffer.clear()
