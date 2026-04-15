"""
RepSense AI - Workout Metrics Module
Tracks, calculates, and summarizes all workout performance data.
"""

import time
from dataclasses import dataclass, field
from typing import List, Optional, Dict
from exercise.pushup_counter import RepSpeed


CALORIES_PER_REP = 0.4  # Approximate calories burned per push-up


@dataclass
class WorkoutSnapshot:
    """Point-in-time workout data."""
    timestamp: float
    rep_count: int
    form_score: float
    elbow_angle: float
    stage: str
    rep_speed: str


@dataclass
class WorkoutSession:
    """Complete workout session summary."""
    start_time: float = field(default_factory=time.time)
    end_time: Optional[float] = None
    total_reps: int = 0
    avg_form_score: float = 0.0
    avg_rep_speed: float = 0.0
    calories_burned: float = 0.0
    rep_times: List[float] = field(default_factory=list)
    form_scores: List[float] = field(default_factory=list)
    snapshots: List[WorkoutSnapshot] = field(default_factory=list)

    @property
    def duration_seconds(self) -> float:
        end = self.end_time or time.time()
        return end - self.start_time

    @property
    def duration_formatted(self) -> str:
        secs = int(self.duration_seconds)
        return f"{secs // 60:02d}:{secs % 60:02d}"


class MetricsTracker:
    """
    Central tracker for all workout metrics during a session.
    """

    def __init__(self):
        self.session = WorkoutSession()
        self._last_snapshot_time: float = 0.0
        self._snapshot_interval: float = 1.0  # seconds

    def update(
        self,
        rep_count: int,
        form_score: float,
        elbow_angle: float,
        stage_label: str,
        rep_times: List[float],
        form_scores: List[float],
    ):
        now = time.time()

        # Update session data
        self.session.total_reps = rep_count
        self.session.rep_times = list(rep_times)
        self.session.form_scores = list(form_scores)
        self.session.calories_burned = round(rep_count * CALORIES_PER_REP, 2)

        if form_scores:
            self.session.avg_form_score = round(sum(form_scores) / len(form_scores), 1)
        if rep_times:
            self.session.avg_rep_speed = round(sum(rep_times) / len(rep_times), 2)

        # Periodic snapshots
        if now - self._last_snapshot_time >= self._snapshot_interval:
            snap = WorkoutSnapshot(
                timestamp=now - self.session.start_time,
                rep_count=rep_count,
                form_score=form_score,
                elbow_angle=elbow_angle,
                stage=stage_label,
                rep_speed=self.classify_speed(rep_times[-1] if rep_times else 0),
            )
            self.session.snapshots.append(snap)
            self._last_snapshot_time = now

    def classify_speed(self, duration: float) -> str:
        if duration <= 0:
            return RepSpeed.UNKNOWN.value
        if duration < 1.2:
            return RepSpeed.FAST.value
        elif duration <= 3.0:
            return RepSpeed.OPTIMAL.value
        else:
            return RepSpeed.SLOW.value

    def get_current_speed_label(self) -> str:
        if not self.session.rep_times:
            return "—"
        return self.classify_speed(self.session.rep_times[-1])

    def get_calories(self) -> float:
        return self.session.calories_burned

    def get_duration(self) -> str:
        return self.session.duration_formatted

    def get_intensity_data(self) -> List[Dict]:
        """Returns rep count over time for intensity chart."""
        return [
            {"time": round(s.timestamp, 1), "reps": s.rep_count}
            for s in self.session.snapshots
        ]

    def get_form_trend(self) -> List[Dict]:
        """Returns form score over time."""
        return [
            {"time": round(s.timestamp, 1), "score": s.form_score}
            for s in self.session.snapshots
        ]

    def finalize_session(self):
        self.session.end_time = time.time()
        return self.session

    def reset(self):
        self.session = WorkoutSession()
        self._last_snapshot_time = 0.0
