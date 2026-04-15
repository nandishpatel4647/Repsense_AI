"""
RepSense AI - Push-Up Counter Module
State machine for detecting and counting push-up repetitions.
"""

import time
from enum import Enum
from typing import Optional, Tuple
from vision.angle_calculator import AngleBuffer


class PushUpStage(Enum):
    UNKNOWN = "unknown"
    UP = "up"
    DOWN = "down"
    TRANSITION_DOWN = "going_down"
    TRANSITION_UP = "going_up"


class RepSpeed(Enum):
    FAST = "Fast ⚡"
    OPTIMAL = "Optimal ✓"
    SLOW = "Slow 🐢"
    UNKNOWN = "—"


# Angle thresholds for push-up detection
ELBOW_DOWN_THRESHOLD = 70.0    # degrees — bottom of push-up
ELBOW_UP_THRESHOLD = 160.0     # degrees — top of push-up
ELBOW_TRANSITION_DOWN = 120.0  # entering downward phase
ELBOW_TRANSITION_UP = 130.0    # entering upward phase

# Rep speed thresholds (seconds per rep)
SPEED_FAST_THRESHOLD = 1.2
SPEED_OPTIMAL_MAX = 3.0


class PushUpCounter:
    """
    Finite state machine for counting push-up repetitions.

    States:
        UP → TRANSITION_DOWN → DOWN → TRANSITION_UP → UP (= 1 rep)

    Features:
    - Smoothed angle input via AngleBuffer
    - Rep timing for speed classification
    - Debounce to prevent double-counting
    - Partial rep detection
    """

    def __init__(self):
        self.rep_count: int = 0
        self.stage: PushUpStage = PushUpStage.UNKNOWN
        self.angle_buffer = AngleBuffer(buffer_size=5)

        self._rep_start_time: Optional[float] = None
        self._stage_enter_time: Optional[float] = None
        self._last_rep_time: float = 0.0
        self._rep_times: list = []

        # Debounce
        self._min_rep_interval: float = 0.5  # seconds
        self._last_count_time: float = 0.0

        # Stats
        self.current_angle: float = 0.0
        self.last_rep_duration: float = 0.0
        self.avg_rep_time: float = 0.0

    def update(self, raw_elbow_angle: float) -> Tuple[int, PushUpStage, float]:
        """
        Feed a new elbow angle reading and update state machine.

        Returns:
            (rep_count, current_stage, smoothed_angle)
        """
        smoothed = self.angle_buffer.add(raw_elbow_angle)
        self.current_angle = smoothed
        now = time.time()

        prev_stage = self.stage

        # State transitions
        if self.stage == PushUpStage.UNKNOWN:
            if smoothed > ELBOW_UP_THRESHOLD:
                self.stage = PushUpStage.UP
                self._stage_enter_time = now
            elif smoothed < ELBOW_DOWN_THRESHOLD:
                self.stage = PushUpStage.DOWN

        elif self.stage == PushUpStage.UP:
            if smoothed < ELBOW_TRANSITION_DOWN:
                self.stage = PushUpStage.TRANSITION_DOWN
                self._rep_start_time = now

        elif self.stage == PushUpStage.TRANSITION_DOWN:
            if smoothed < ELBOW_DOWN_THRESHOLD:
                self.stage = PushUpStage.DOWN
            elif smoothed > ELBOW_UP_THRESHOLD:
                # Aborted — go back up without counting
                self.stage = PushUpStage.UP

        elif self.stage == PushUpStage.DOWN:
            if smoothed > ELBOW_TRANSITION_UP:
                self.stage = PushUpStage.TRANSITION_UP

        elif self.stage == PushUpStage.TRANSITION_UP:
            if smoothed > ELBOW_UP_THRESHOLD:
                self.stage = PushUpStage.UP
                # Complete rep — check debounce
                if (now - self._last_count_time) > self._min_rep_interval:
                    self.rep_count += 1
                    self._last_count_time = now
                    if self._rep_start_time:
                        duration = now - self._rep_start_time
                        self.last_rep_duration = duration
                        self._rep_times.append(duration)
                        self.avg_rep_time = sum(self._rep_times) / len(self._rep_times)
                    self._rep_start_time = None
            elif smoothed < ELBOW_DOWN_THRESHOLD:
                # Went back down
                self.stage = PushUpStage.DOWN

        return self.rep_count, self.stage, smoothed

    def classify_rep_speed(self, duration: Optional[float] = None) -> RepSpeed:
        """Classify last rep speed."""
        t = duration or self.last_rep_duration
        if t <= 0:
            return RepSpeed.UNKNOWN
        if t < SPEED_FAST_THRESHOLD:
            return RepSpeed.FAST
        elif t <= SPEED_OPTIMAL_MAX:
            return RepSpeed.OPTIMAL
        else:
            return RepSpeed.SLOW

    def get_rep_times(self) -> list:
        return list(self._rep_times)

    def get_stage_label(self) -> str:
        stage_labels = {
            PushUpStage.UP: "⬆ UP",
            PushUpStage.DOWN: "⬇ DOWN",
            PushUpStage.TRANSITION_DOWN: "↘ GOING DOWN",
            PushUpStage.TRANSITION_UP: "↗ GOING UP",
            PushUpStage.UNKNOWN: "— POSITION",
        }
        return stage_labels.get(self.stage, "—")

    def reset(self):
        """Reset counter for new session."""
        self.rep_count = 0
        self.stage = PushUpStage.UNKNOWN
        self.angle_buffer.reset()
        self._rep_start_time = None
        self._last_count_time = 0.0
        self._rep_times.clear()
        self.last_rep_duration = 0.0
        self.avg_rep_time = 0.0
        self.current_angle = 0.0
