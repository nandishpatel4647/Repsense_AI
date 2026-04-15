"""
RepSense AI - Utility Helpers
Miscellaneous helper functions for overlay rendering and conversions.
"""

import cv2
import numpy as np
from typing import Tuple


def draw_text_with_bg(
    frame: np.ndarray,
    text: str,
    position: Tuple[int, int],
    font_scale: float = 0.6,
    text_color: Tuple = (255, 255, 255),
    bg_color: Tuple = (0, 0, 0),
    alpha: float = 0.6,
    padding: int = 8,
    font_thickness: int = 1,
) -> np.ndarray:
    """Draw text with semi-transparent background box."""
    font = cv2.FONT_HERSHEY_SIMPLEX
    (tw, th), baseline = cv2.getTextSize(text, font, font_scale, font_thickness)

    x, y = position
    x1, y1 = x - padding, y - th - padding
    x2, y2 = x + tw + padding, y + baseline + padding

    overlay = frame.copy()
    cv2.rectangle(overlay, (x1, y1), (x2, y2), bg_color, -1)
    cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)
    cv2.putText(frame, text, (x, y), font, font_scale, text_color, font_thickness, cv2.LINE_AA)
    return frame


def draw_angle_arc(
    frame: np.ndarray,
    vertex: Tuple[int, int],
    angle: float,
    radius: int = 30,
    color: Tuple = (0, 212, 255),
) -> np.ndarray:
    """Draw a small arc at a joint to visualize the angle."""
    cv2.ellipse(frame, vertex, (radius, radius), 0, 0, int(angle),
                color, 2, cv2.LINE_AA)
    # Show angle value near joint
    text = f"{int(angle)}"
    offset = (vertex[0] + radius + 5, vertex[1] - 5)
    cv2.putText(frame, text, offset, cv2.FONT_HERSHEY_SIMPLEX,
                0.45, color, 1, cv2.LINE_AA)
    return frame


def draw_overlay_panel(
    frame: np.ndarray,
    reps: int,
    stage: str,
    elbow_angle: float,
    form_score: float,
    speed_label: str,
    calories: float,
    duration: str,
) -> np.ndarray:
    """
    Draw a comprehensive HUD overlay on the camera frame.
    """
    h, w = frame.shape[:2]
    overlay = frame.copy()

    # Left panel background
    panel_w = 200
    cv2.rectangle(overlay, (0, 0), (panel_w, h), (5, 5, 15), -1)
    cv2.addWeighted(overlay, 0.75, frame, 0.25, 0, frame)

    # Top gradient line
    for i in range(panel_w):
        alpha_val = i / panel_w
        color = (
            int(0 + alpha_val * 139),
            int(212 - alpha_val * 100),
            int(255 - alpha_val * 100),
        )
        cv2.line(frame, (i, 0), (i, 3), color, 1)

    font = cv2.FONT_HERSHEY_SIMPLEX

    # Brand watermark
    cv2.putText(frame, "RepSense AI", (10, 25), font, 0.5,
                (0, 212, 255), 1, cv2.LINE_AA)
    cv2.line(frame, (10, 32), (panel_w - 10, 32), (30, 30, 60), 1)

    # Rep counter (large)
    cv2.putText(frame, "REPS", (10, 65), font, 0.45,
                (150, 150, 180), 1, cv2.LINE_AA)
    rep_str = str(reps)
    cv2.putText(frame, rep_str, (15, 115), font, 2.5,
                (0, 212, 255), 3, cv2.LINE_AA)

    # Stage
    cv2.putText(frame, "STAGE", (10, 145), font, 0.4,
                (150, 150, 180), 1, cv2.LINE_AA)
    stage_clean = stage.replace("⬆", "UP").replace("⬇", "DOWN").replace("↘", "V").replace("↗", "^").replace("—", "-")
    cv2.putText(frame, stage_clean[:12], (10, 165), font, 0.52,
                (139, 92, 246), 1, cv2.LINE_AA)

    # Elbow angle
    cv2.putText(frame, "ELBOW ANG", (10, 195), font, 0.4,
                (150, 150, 180), 1, cv2.LINE_AA)
    cv2.putText(frame, f"{elbow_angle:.0f}", (10, 218), font, 0.85,
                (0, 212, 255), 2, cv2.LINE_AA)

    # Form score
    cv2.putText(frame, "FORM", (10, 248), font, 0.4,
                (150, 150, 180), 1, cv2.LINE_AA)
    score_color = (16, 185, 129) if form_score >= 80 else \
                  (245, 158, 11) if form_score >= 60 else (239, 68, 68)
    cv2.putText(frame, f"{form_score:.0f}%", (10, 270), font, 0.85,
                score_color, 2, cv2.LINE_AA)
    # Mini bar
    bar_x, bar_y, bar_w_full, bar_h = 10, 278, panel_w - 20, 5
    cv2.rectangle(frame, (bar_x, bar_y), (bar_x + bar_w_full, bar_y + bar_h),
                  (30, 30, 60), -1)
    fill = int(bar_w_full * form_score / 100)
    cv2.rectangle(frame, (bar_x, bar_y), (bar_x + fill, bar_y + bar_h),
                  score_color, -1)

    # Speed
    cv2.putText(frame, "SPEED", (10, 308), font, 0.4,
                (150, 150, 180), 1, cv2.LINE_AA)
    speed_clean = speed_label.replace("⚡", "").replace("✓", "OK").replace("🐢", "")
    cv2.putText(frame, speed_clean.strip()[:8], (10, 328), font, 0.6,
                (245, 158, 11), 1, cv2.LINE_AA)

    # Calories
    cv2.putText(frame, "CALORIES", (10, 358), font, 0.4,
                (150, 150, 180), 1, cv2.LINE_AA)
    cv2.putText(frame, f"{calories:.1f}", (10, 378), font, 0.7,
                (16, 185, 129), 1, cv2.LINE_AA)

    # Duration
    cv2.putText(frame, "DURATION", (10, 408), font, 0.4,
                (150, 150, 180), 1, cv2.LINE_AA)
    cv2.putText(frame, duration, (10, 428), font, 0.6,
                (255, 255, 255), 1, cv2.LINE_AA)

    return frame


def format_duration(seconds: float) -> str:
    secs = int(seconds)
    return f"{secs // 60:02d}:{secs % 60:02d}"


def get_color_for_score(score: float) -> str:
    """Return hex color based on score."""
    if score >= 80:
        return "#10B981"
    elif score >= 60:
        return "#F59E0B"
    else:
        return "#EF4444"
