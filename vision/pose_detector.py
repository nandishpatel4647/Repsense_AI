"""
RepSense AI - Pose Detection Module  [Python 3.13 Compatible]
Uses Ultralytics YOLOv8-pose for real-time body landmark detection.

COCO 17-Keypoint Index Map:
  0: Nose          1: Left Eye       2: Right Eye
  3: Left Ear      4: Right Ear      5: Left Shoulder
  6: Right Shoulder 7: Left Elbow    8: Right Elbow
  9: Left Wrist   10: Right Wrist   11: Left Hip
 12: Right Hip    13: Left Knee     14: Right Knee
 15: Left Ankle   16: Right Ankle
"""

import cv2
import numpy as np
from typing import Optional, Tuple
from ultralytics import YOLO


# ── COCO Keypoint Index Constants ────────────────────────────────────────────
class KP:
    NOSE           = 0
    LEFT_EYE       = 1
    RIGHT_EYE      = 2
    LEFT_EAR       = 3
    RIGHT_EAR      = 4
    LEFT_SHOULDER  = 5
    RIGHT_SHOULDER = 6
    LEFT_ELBOW     = 7
    RIGHT_ELBOW    = 8
    LEFT_WRIST     = 9
    RIGHT_WRIST    = 10
    LEFT_HIP       = 11
    RIGHT_HIP      = 12
    LEFT_KNEE      = 13
    RIGHT_KNEE     = 14
    LEFT_ANKLE     = 15
    RIGHT_ANKLE    = 16


# Skeleton connections as (start_idx, end_idx) pairs
SKELETON_CONNECTIONS = [
    (KP.LEFT_SHOULDER,  KP.LEFT_ELBOW),
    (KP.LEFT_ELBOW,     KP.LEFT_WRIST),
    (KP.RIGHT_SHOULDER, KP.RIGHT_ELBOW),
    (KP.RIGHT_ELBOW,    KP.RIGHT_WRIST),
    (KP.LEFT_SHOULDER,  KP.RIGHT_SHOULDER),
    (KP.LEFT_SHOULDER,  KP.LEFT_HIP),
    (KP.RIGHT_SHOULDER, KP.RIGHT_HIP),
    (KP.LEFT_HIP,       KP.RIGHT_HIP),
    (KP.LEFT_HIP,       KP.LEFT_KNEE),
    (KP.LEFT_KNEE,      KP.LEFT_ANKLE),
    (KP.RIGHT_HIP,      KP.RIGHT_KNEE),
    (KP.RIGHT_KNEE,     KP.RIGHT_ANKLE),
]

KEY_JOINT_INDICES = [
    KP.LEFT_SHOULDER, KP.RIGHT_SHOULDER,
    KP.LEFT_ELBOW,    KP.RIGHT_ELBOW,
    KP.LEFT_WRIST,    KP.RIGHT_WRIST,
    KP.LEFT_HIP,      KP.RIGHT_HIP,
    KP.LEFT_KNEE,     KP.RIGHT_KNEE,
    KP.LEFT_ANKLE,    KP.RIGHT_ANKLE,
]

CONF_THRESHOLD = 0.4   # Minimum keypoint confidence to render/use


class PoseResult:
    """
    Wraps a single-person keypoint result from YOLOv8-pose.
    Provides the same interface the rest of the app expects.
    """
    def __init__(self, keypoints_xy: np.ndarray, keypoints_conf: np.ndarray):
        self.xy   = keypoints_xy    # (17, 2)
        self.conf = keypoints_conf  # (17,)

    def get(self, idx: int) -> Tuple[int, int]:
        return int(self.xy[idx, 0]), int(self.xy[idx, 1])

    def is_visible(self, idx: int, threshold: float = CONF_THRESHOLD) -> bool:
        return float(self.conf[idx]) >= threshold


class PoseDetector:
    """
    Real-time pose detection using YOLOv8n-pose (Ultralytics).
    Fully compatible with Python 3.13+.
    Drop-in replacement for the old MediaPipe PoseDetector.
    """

    def __init__(
        self,
        model_name: str = "yolov8n-pose.pt",
        min_detection_confidence: float = 0.50,
        min_tracking_confidence: float = 0.50,
        model_complexity: int = 1,
        static_image_mode: bool = False,
        smooth_landmarks: bool = True,
    ):
        self.model = YOLO(model_name)
        self.conf_threshold = min_detection_confidence
        self._last_result: Optional[PoseResult] = None

    def process_frame(self, frame: np.ndarray) -> Tuple[np.ndarray, Optional[PoseResult]]:
        results = self.model(frame, verbose=False, conf=self.conf_threshold, stream=False)
        pose_result = None
        for r in results:
            if r.keypoints is None or len(r.keypoints) == 0:
                continue
            boxes = r.boxes
            best_idx = int(boxes.conf.argmax()) if (boxes is not None and len(boxes) > 0) else 0
            kp_xy   = r.keypoints.xy[best_idx].cpu().numpy()
            kp_conf = r.keypoints.conf[best_idx].cpu().numpy()
            pose_result = PoseResult(kp_xy, kp_conf)
            break
        self._last_result = pose_result
        return frame, pose_result

    def draw_custom_skeleton(self, frame, landmarks, joint_color=(0,212,255),
                              bone_color=(100,60,220), joint_radius=6, bone_thickness=2):
        for s, e in SKELETON_CONNECTIONS:
            if landmarks.is_visible(s) and landmarks.is_visible(e):
                cv2.line(frame, landmarks.get(s), landmarks.get(e), bone_color, bone_thickness+4)
                cv2.line(frame, landmarks.get(s), landmarks.get(e), bone_color, bone_thickness)
        for idx in KEY_JOINT_INDICES:
            if landmarks.is_visible(idx):
                cx, cy = landmarks.get(idx)
                cv2.circle(frame, (cx, cy), joint_radius+3, (30,30,60), -1)
                cv2.circle(frame, (cx, cy), joint_radius,   joint_color, -1)
                cv2.circle(frame, (cx, cy), joint_radius+1, (255,255,255), 1)
        return frame

    def get_landmark_coords(self, landmarks, landmark_id, frame_shape=None):
        return landmarks.get(landmark_id)

    def is_landmark_visible(self, landmarks, landmark_id, threshold=CONF_THRESHOLD):
        return landmarks.is_visible(landmark_id, threshold)

    def get_key_landmarks(self, landmarks, frame_shape=None) -> dict:
        return {
            "left_shoulder":  landmarks.get(KP.LEFT_SHOULDER),
            "right_shoulder": landmarks.get(KP.RIGHT_SHOULDER),
            "left_elbow":     landmarks.get(KP.LEFT_ELBOW),
            "right_elbow":    landmarks.get(KP.RIGHT_ELBOW),
            "left_wrist":     landmarks.get(KP.LEFT_WRIST),
            "right_wrist":    landmarks.get(KP.RIGHT_WRIST),
            "left_hip":       landmarks.get(KP.LEFT_HIP),
            "right_hip":      landmarks.get(KP.RIGHT_HIP),
            "left_knee":      landmarks.get(KP.LEFT_KNEE),
            "right_knee":     landmarks.get(KP.RIGHT_KNEE),
            "left_ankle":     landmarks.get(KP.LEFT_ANKLE),
            "right_ankle":    landmarks.get(KP.RIGHT_ANKLE),
        }
