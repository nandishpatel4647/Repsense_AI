"""
RepSense AI - Main Application  [Python 3.13 Compatible]
Streamlit-based real-time push-up tracking and form analysis dashboard.
Powered by YOLOv8-pose (Ultralytics) — no MediaPipe required.

Run with: streamlit run app.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import streamlit as st
import cv2
import numpy as np
import time
import pandas as pd

# ─── Page Config ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="RepSense AI",
    page_icon="💪",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─── Module Imports ───────────────────────────────────────────────────────────
from vision.pose_detector import PoseDetector, KP
from vision.angle_calculator import calculate_angle
from exercise.pushup_counter import PushUpCounter
from exercise.form_analyzer import FormAnalyzer
from analytics.metrics import MetricsTracker
from analytics.charts import (
    make_rep_speed_chart, make_reps_timeline_chart,
    make_form_accuracy_chart, make_speed_distribution_chart,
)
from database.db_manager import DatabaseManager
from ui.styles import (
    CUSTOM_CSS, get_metric_card_html, get_form_score_bar_html,
    get_header_html, get_grade_badge_html, get_stage_display_html,
    get_section_header_html, get_neon_divider_html,
)
from utils.helpers import draw_overlay_panel

# ─── Inject Styles ────────────────────────────────────────────────────────────
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# ─── Session State Init ───────────────────────────────────────────────────────
def init_session_state():
    defaults = {
        "running": False, "session_started": False,
        "rep_count": 0, "form_score": 0.0, "elbow_angle": 0.0,
        "stage_label": "— POSITION", "speed_label": "—",
        "calories": 0.0, "duration": "00:00", "grade": "—",
        "feedback_msgs": [], "rep_times": [], "form_scores_history": [],
        "intensity_data": [], "form_trend": [],
        "session_saved": False, "error_message": None,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_session_state()

# ─── Cached Resources ─────────────────────────────────────────────────────────
@st.cache_resource
def get_detector():
    # yolov8n-pose.pt = ~6 MB, downloads automatically on first run
    return PoseDetector(model_name="yolov8n-pose.pt", min_detection_confidence=0.50)

@st.cache_resource
def get_db():
    return DatabaseManager()

counter  = PushUpCounter()
analyzer = FormAnalyzer()
tracker  = MetricsTracker()
db       = get_db()

# ─── Header ───────────────────────────────────────────────────────────────────
st.markdown(get_header_html(st.session_state.running), unsafe_allow_html=True)

# ─── Control Bar ──────────────────────────────────────────────────────────────
ctrl_col1, ctrl_col2, ctrl_col3, ctrl_col4 = st.columns([1, 1, 1, 1])

with ctrl_col1:
    if st.button("▶  START SESSION", use_container_width=True):
        st.session_state.running = True
        st.session_state.session_started = True
        st.session_state.session_saved = False
        st.session_state.error_message = None
        counter.reset(); analyzer.reset(); tracker.reset()
        st.rerun()

with ctrl_col2:
    if st.button("⏹  STOP SESSION", use_container_width=True):
        st.session_state.running = False
        st.rerun()

with ctrl_col3:
    can_save = (st.session_state.session_started and
                st.session_state.rep_count > 0 and
                not st.session_state.session_saved)
    if st.button("💾  SAVE SESSION", use_container_width=True, disabled=not can_save):
        session = tracker.finalize_session()
        from exercise.form_analyzer import FormAnalyzer as FA
        grade = FA()._score_to_grade(session.avg_form_score)
        db.save_session(
            duration_secs=session.duration_seconds,
            total_reps=session.total_reps,
            avg_rep_speed=session.avg_rep_speed,
            form_score=session.avg_form_score,
            calories=session.calories_burned,
            grade=grade,
        )
        st.session_state.session_saved = True
        st.success("✅ Session saved!")
        time.sleep(1); st.rerun()

with ctrl_col4:
    st.markdown('<div class="reset-btn">', unsafe_allow_html=True)
    if st.button("🔄  RESET SESSION", use_container_width=True, key="reset_btn"):
        # Stop any running session
        st.session_state.running = False
        # Reset all workout state back to zero
        st.session_state.session_started = False
        st.session_state.session_saved = False
        st.session_state.rep_count = 0
        st.session_state.form_score = 0.0
        st.session_state.elbow_angle = 0.0
        st.session_state.stage_label = "— POSITION"
        st.session_state.speed_label = "—"
        st.session_state.calories = 0.0
        st.session_state.duration = "00:00"
        st.session_state.grade = "—"
        st.session_state.feedback_msgs = []
        st.session_state.rep_times = []
        st.session_state.form_scores_history = []
        st.session_state.intensity_data = []
        st.session_state.form_trend = []
        st.session_state.error_message = None
        counter.reset()
        analyzer.reset()
        tracker.reset()
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# ─── Main Layout ──────────────────────────────────────────────────────────────
st.markdown(get_neon_divider_html(), unsafe_allow_html=True)
cam_col, metrics_col = st.columns([3, 2])

with cam_col:
    st.markdown(get_section_header_html("📷 LIVE CAMERA FEED"), unsafe_allow_html=True)
    frame_placeholder = st.empty()
    error_placeholder = st.empty()

with metrics_col:
    st.markdown(get_section_header_html("📊 REAL-TIME METRICS"), unsafe_allow_html=True)
    m1, m2 = st.columns(2)
    with m1:
        reps_placeholder  = st.empty()
        angle_placeholder = st.empty()
    with m2:
        stage_placeholder = st.empty()
        speed_placeholder = st.empty()
    st.markdown("<br>", unsafe_allow_html=True)
    form_bar_placeholder = st.empty()
    gc1, gc2 = st.columns(2)
    with gc1: grade_placeholder    = st.empty()
    with gc2: calories_placeholder = st.empty()
    duration_placeholder = st.empty()
    st.markdown(get_section_header_html("💬 FORM FEEDBACK"), unsafe_allow_html=True)
    feedback_placeholder = st.empty()

# ─── Charts & History placeholders ───────────────────────────────────────────
st.markdown(get_neon_divider_html(), unsafe_allow_html=True)
st.markdown(get_section_header_html("📈 WORKOUT ANALYTICS"), unsafe_allow_html=True)
cc1, cc2 = st.columns(2)
with cc1: speed_chart_ph    = st.empty()
with cc2: timeline_chart_ph = st.empty()
cc3, cc4 = st.columns(2)
with cc3: form_chart_ph = st.empty()
with cc4: dist_chart_ph = st.empty()

st.markdown(get_neon_divider_html(), unsafe_allow_html=True)
st.markdown(get_section_header_html("🗄️ WORKOUT HISTORY"), unsafe_allow_html=True)
history_placeholder = st.empty()


# ─── UI Render Helpers ────────────────────────────────────────────────────────
def render_metrics_ui():
    reps_placeholder.markdown(
        get_metric_card_html("💪", "TOTAL REPS", str(st.session_state.rep_count), "blue"),
        unsafe_allow_html=True)
    angle_placeholder.markdown(
        get_metric_card_html("📐", "ELBOW ANGLE", f"{st.session_state.elbow_angle:.0f}°", "purple"),
        unsafe_allow_html=True)
    stage_placeholder.markdown(
        get_stage_display_html(st.session_state.stage_label), unsafe_allow_html=True)
    speed_placeholder.markdown(
        get_metric_card_html("⚡", "REP SPEED", st.session_state.speed_label, "orange"),
        unsafe_allow_html=True)
    form_bar_placeholder.markdown(
        get_form_score_bar_html(st.session_state.form_score), unsafe_allow_html=True)
    grade_placeholder.markdown(
        get_metric_card_html("🏆", "GRADE", st.session_state.grade, "green"),
        unsafe_allow_html=True)
    calories_placeholder.markdown(
        get_metric_card_html("🔥", "CALORIES", f"{st.session_state.calories:.1f}", "orange"),
        unsafe_allow_html=True)
    duration_placeholder.markdown(
        get_metric_card_html("⏱", "DURATION", st.session_state.duration, ""),
        unsafe_allow_html=True)

    fb_html = ""
    for msg in st.session_state.feedback_msgs[-3:]:
        fb_html += f'<div class="feedback-{msg.severity}">{msg.icon} {msg.message}</div>'
    if not fb_html:
        fb_html = '<div class="feedback-good">✅ Start a session to get feedback</div>'
    feedback_placeholder.markdown(fb_html, unsafe_allow_html=True)


def render_charts():
    suffix = str(int(time.time() * 1000))
    speed_chart_ph.plotly_chart(
        make_rep_speed_chart(st.session_state.rep_times),
        use_container_width=True, key=f"sc_{suffix}")
    timeline_chart_ph.plotly_chart(
        make_reps_timeline_chart(st.session_state.intensity_data),
        use_container_width=True, key=f"tc_{suffix}")
    form_chart_ph.plotly_chart(
        make_form_accuracy_chart(st.session_state.form_trend),
        use_container_width=True, key=f"fc_{suffix}")
    dist_chart_ph.plotly_chart(
        make_speed_distribution_chart(st.session_state.rep_times),
        use_container_width=True, key=f"dc_{suffix}")


def render_history():
    sessions = db.get_all_sessions()
    if not sessions:
        history_placeholder.info("No workout history yet. Complete and save a session!")
        return
    stats = db.get_total_stats()
    sc = st.columns(4)
    for col, (lbl, val) in zip(sc, [
        ("🏋️ Sessions", str(stats["sessions"])),
        ("💪 Total Reps", str(stats["total_reps"])),
        ("🔥 Calories", f"{stats['total_calories']:.1f}"),
        ("🎯 Avg Form", f"{stats['avg_form']:.1f}%"),
    ]):
        col.metric(lbl, val)

    rows = []
    for s in sessions[:15]:
        m, sec = divmod(int(s.duration_seconds), 60)
        rows.append({"Date": s.date, "Duration": f"{m:02d}:{sec:02d}",
                     "Reps": s.total_reps,
                     "Avg Speed": f"{s.avg_rep_speed:.1f}s" if s.avg_rep_speed else "—",
                     "Form Score": f"{s.form_score:.1f}%",
                     "Calories": f"{s.calories_burned:.1f}", "Grade": s.grade})
    history_placeholder.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)


# Initial static render
render_metrics_ui()
render_charts()
render_history()


# ─── LIVE CAMERA LOOP ─────────────────────────────────────────────────────────
if st.session_state.running:
    detector = get_detector()

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        st.session_state.running = False
        st.session_state.error_message = "❌ Camera not detected. Please check your webcam."
        st.rerun()

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    cap.set(cv2.CAP_PROP_FPS, 30)

    frame_count = 0
    UI_INTERVAL = 3   # update metrics every N frames

    while st.session_state.running:
        ret, frame = cap.read()
        if not ret:
            error_placeholder.error("⚠️ Failed to read frame. Check your camera.")
            break

        frame = cv2.flip(frame, 1)
        frame, pose = detector.process_frame(frame)

        if pose is not None:
            # ── Draw skeleton ─────────────────────────────────────────────
            detector.draw_custom_skeleton(frame, pose)

            # ── Extract keypoint coords using KP indices ──────────────────
            left_shoulder  = pose.get(KP.LEFT_SHOULDER)
            left_elbow     = pose.get(KP.LEFT_ELBOW)
            left_wrist     = pose.get(KP.LEFT_WRIST)
            right_shoulder = pose.get(KP.RIGHT_SHOULDER)
            right_elbow    = pose.get(KP.RIGHT_ELBOW)
            right_wrist    = pose.get(KP.RIGHT_WRIST)
            left_hip       = pose.get(KP.LEFT_HIP)
            right_hip      = pose.get(KP.RIGHT_HIP)
            left_ankle     = pose.get(KP.LEFT_ANKLE)
            right_ankle    = pose.get(KP.RIGHT_ANKLE)

            # ── Elbow angles (average both arms) ──────────────────────────
            l_angle = calculate_angle(left_shoulder,  left_elbow,  left_wrist)
            r_angle = calculate_angle(right_shoulder, right_elbow, right_wrist)
            elbow_angle = (l_angle + r_angle) / 2.0

            # ── Push-up counter FSM ───────────────────────────────────────
            rep_count, stage, smoothed_angle = counter.update(elbow_angle)
            stage_label  = counter.get_stage_label()
            speed_label  = counter.classify_rep_speed().value

            # ── Form analysis (mid-points) ────────────────────────────────
            mid_shoulder = ((left_shoulder[0] + right_shoulder[0]) // 2,
                            (left_shoulder[1] + right_shoulder[1]) // 2)
            mid_hip      = ((left_hip[0]  + right_hip[0])  // 2,
                            (left_hip[1]  + right_hip[1])  // 2)
            mid_ankle    = ((left_ankle[0] + right_ankle[0]) // 2,
                            (left_ankle[1] + right_ankle[1]) // 2)

            form_result = analyzer.analyze(
                mid_shoulder, mid_hip, mid_ankle, smoothed_angle, stage_label)

            # ── Metrics tracker ───────────────────────────────────────────
            tracker.update(
                rep_count=rep_count,
                form_score=form_result.score,
                elbow_angle=smoothed_angle,
                stage_label=stage_label,
                rep_times=counter.get_rep_times(),
                form_scores=[form_result.score],
            )

            calories = tracker.get_calories()
            duration = tracker.get_duration()

            # ── HUD overlay ───────────────────────────────────────────────
            frame = draw_overlay_panel(
                frame, reps=rep_count, stage=stage_label,
                elbow_angle=smoothed_angle, form_score=form_result.score,
                speed_label=speed_label, calories=calories, duration=duration,
            )

            # ── Update session state (throttled) ──────────────────────────
            if frame_count % UI_INTERVAL == 0:
                st.session_state.rep_count      = rep_count
                st.session_state.elbow_angle    = smoothed_angle
                st.session_state.stage_label    = stage_label
                st.session_state.speed_label    = speed_label
                st.session_state.form_score     = form_result.score
                st.session_state.calories       = calories
                st.session_state.duration       = duration
                st.session_state.feedback_msgs  = form_result.feedback
                st.session_state.grade          = form_result.overall_grade
                st.session_state.rep_times      = counter.get_rep_times()
                st.session_state.intensity_data = tracker.get_intensity_data()
                st.session_state.form_trend     = tracker.get_form_trend()

        else:
            h, w = frame.shape[:2]
            cv2.putText(frame, "NO PERSON DETECTED",
                        (w // 2 - 180, h // 2), cv2.FONT_HERSHEY_SIMPLEX,
                        1.0, (239, 68, 68), 2, cv2.LINE_AA)
            cv2.putText(frame, "Position yourself in frame",
                        (w // 2 - 160, h // 2 + 40), cv2.FONT_HERSHEY_SIMPLEX,
                        0.6, (156, 163, 175), 1, cv2.LINE_AA)

        # Display
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame_placeholder.image(rgb, channels="RGB", use_column_width=True)

        if frame_count % (UI_INTERVAL * 5) == 0:
            render_metrics_ui()
            render_charts()

        frame_count += 1

    cap.release()
    st.rerun()

else:
    with frame_placeholder:
        st.markdown("""
        <div style="background:linear-gradient(135deg,#0D0D14,#111827);
                    border:1px solid rgba(0,212,255,0.15);border-radius:16px;
                    height:400px;display:flex;flex-direction:column;
                    align-items:center;justify-content:center;gap:1rem;">
            <div style="font-size:4rem;">📷</div>
            <div style="font-family:'Orbitron',monospace;color:#00D4FF;
                        font-size:1.2rem;letter-spacing:0.1em;">CAMERA STANDBY</div>
            <div style="font-family:'Rajdhani',sans-serif;color:#6B7280;font-size:0.9rem;">
                Press START SESSION to begin tracking</div>
        </div>""", unsafe_allow_html=True)

    if st.session_state.error_message:
        st.error(st.session_state.error_message)