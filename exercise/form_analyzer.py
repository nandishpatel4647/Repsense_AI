"""
RepSense AI - Form Analysis Module
Biomechanical evaluation of push-up form and posture quality.
"""

from dataclasses import dataclass, field
from typing import List, Tuple, Optional
from vision.angle_calculator import calculate_angle, calculate_body_alignment_deviation


@dataclass
class FormFeedback:
    message: str
    severity: str  # "good", "warning", "error"
    icon: str


@dataclass
class FormAnalysis:
    score: float                  # 0–100
    feedback: List[FormFeedback]
    body_alignment_deviation: float
    hip_sag: bool
    hip_pike: bool
    depth_ok: bool
    overall_grade: str


# Thresholds
ALIGNMENT_GOOD_THRESHOLD = 15.0     # degrees deviation from 180
ALIGNMENT_WARNING_THRESHOLD = 25.0  # degrees deviation — warning
HIP_SAG_THRESHOLD = 20.0            # hip drops below shoulder-ankle line
HIP_PIKE_THRESHOLD = 30.0           # hip rises above shoulder-ankle line
DEPTH_ELBOW_ANGLE_THRESHOLD = 70.0  # elbow angle for good depth


class FormAnalyzer:
    """
    Analyzes push-up biomechanics and generates real-time feedback.

    Evaluates:
    - Body alignment (spine angle)
    - Hip sag / hip pike
    - Push-up depth
    - Rep consistency over time

    Scoring:
        100 = Perfect form
        80–99 = Good
        60–79 = Fair
        <60 = Poor
    """

    def __init__(self):
        self._score_history: List[float] = []
        self._rep_scores: List[float] = []
        self._max_history = 30

    def analyze(
        self,
        shoulder: Tuple[float, float],
        hip: Tuple[float, float],
        ankle: Tuple[float, float],
        elbow_angle: float,
        stage_label: str,
    ) -> FormAnalysis:
        """
        Run full form analysis for current frame.
        """
        feedback = []
        deductions = 0.0

        # 1. Body alignment
        deviation = calculate_body_alignment_deviation(shoulder, hip, ankle)
        hip_sag = False
        hip_pike = False

        shoulder_ankle_angle = calculate_angle(shoulder, hip, ankle)

        if deviation < ALIGNMENT_GOOD_THRESHOLD:
            feedback.append(FormFeedback("Body alignment: Perfect ✓", "good", "✅"))
        elif deviation < ALIGNMENT_WARNING_THRESHOLD:
            feedback.append(FormFeedback("Maintain a straighter body line", "warning", "⚠️"))
            deductions += 10
        else:
            # Determine sag vs pike
            if hip[1] > max(shoulder[1], ankle[1]):  # y-axis: larger = lower on screen
                hip_sag = True
                feedback.append(FormFeedback("Don't let hips sag — engage core!", "error", "🔴"))
                deductions += 25
            else:
                hip_pike = True
                feedback.append(FormFeedback("Lower your hips — don't pike up!", "error", "🔴"))
                deductions += 20

        # 2. Push-up depth
        depth_ok = elbow_angle <= DEPTH_ELBOW_ANGLE_THRESHOLD
        if "DOWN" in stage_label or "GOING" in stage_label:
            if elbow_angle > DEPTH_ELBOW_ANGLE_THRESHOLD + 20:
                feedback.append(FormFeedback("Go lower — chest near the ground", "warning", "⚠️"))
                deductions += 15
            elif depth_ok:
                feedback.append(FormFeedback("Great depth! ✓", "good", "✅"))

        # 3. If no feedback yet, add positive
        if not feedback:
            feedback.append(FormFeedback("Form looks great! Keep it up!", "good", "✅"))

        # Calculate score
        score = max(0.0, 100.0 - deductions)
        self._score_history.append(score)
        if len(self._score_history) > self._max_history:
            self._score_history.pop(0)

        # Grade
        avg_score = sum(self._score_history) / len(self._score_history)
        grade = self._score_to_grade(avg_score)

        return FormAnalysis(
            score=round(score, 1),
            feedback=feedback,
            body_alignment_deviation=round(deviation, 1),
            hip_sag=hip_sag,
            hip_pike=hip_pike,
            depth_ok=depth_ok,
            overall_grade=grade,
        )

    def record_rep_score(self, score: float):
        """Record form score at the end of a rep."""
        self._rep_scores.append(score)

    def get_average_form_score(self) -> float:
        """Return average form score across all reps."""
        if not self._score_history:
            return 0.0
        return round(sum(self._score_history) / len(self._score_history), 1)

    def get_rep_score_trend(self) -> List[float]:
        return list(self._rep_scores)

    def _score_to_grade(self, score: float) -> str:
        if score >= 90:
            return "A+"
        elif score >= 80:
            return "A"
        elif score >= 70:
            return "B"
        elif score >= 60:
            return "C"
        else:
            return "D"

    def reset(self):
        self._score_history.clear()
        self._rep_scores.clear()
