# 💪 RepSense AI
### Intelligent Exercise Recognition & Form Analysis System

<div align="center">

![Python](https://img.shields.io/badge/Python-3.9+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![MediaPipe](https://img.shields.io/badge/MediaPipe-0.10+-00C4FF?style=for-the-badge)
![Streamlit](https://img.shields.io/badge/Streamlit-1.32+-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)
![OpenCV](https://img.shields.io/badge/OpenCV-4.9+-5C3EE8?style=for-the-badge&logo=opencv&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-3-003B57?style=for-the-badge&logo=sqlite&logoColor=white)

*A production-grade AI fitness trainer that analyzes push-up form in real time using computer vision and biomechanical joint analysis.*

</div>

---

## 🌟 Overview

RepSense AI is a full-stack computer vision application that functions as an AI-powered personal trainer. It uses **MediaPipe Pose** to track 33 body landmarks at 30 FPS, computes **biomechanical joint angles**, detects push-up motion states via a **finite state machine**, evaluates posture quality, and presents everything in a **premium dark-themed dashboard**.

This project is designed for **IIT-level hackathons**, research demonstrations, and GitHub portfolios.

---

## ✨ Features

| Feature | Description |
|---|---|
| 🎯 **Real-Time Pose Estimation** | 33-landmark body tracking at 30 FPS via MediaPipe |
| 📐 **Joint Angle Calculation** | Vector-based biomechanical angle computation |
| 🔢 **Intelligent Rep Counting** | FSM-based state machine with noise filtering |
| 🏥 **Form Analysis** | Hip sag, pike, and depth detection with instant feedback |
| ⚡ **Rep Speed Tracking** | Per-rep timing classified as Fast / Optimal / Slow |
| 🔥 **Calorie Estimation** | Real-time calorie burn calculation |
| 📊 **Analytics Dashboard** | 4 interactive Plotly charts (speed, timeline, form, distribution) |
| 🗄️ **Session History** | SQLite-persisted workout history with aggregate stats |
| 🎨 **Premium Dark UI** | Neon-styled Streamlit dashboard with custom CSS |
| 🖥️ **HUD Overlay** | Real-time metric overlay directly on camera feed |

---

## 🏗 System Architecture

```
Webcam Input (OpenCV)
        │
        ▼
Frame Pre-processing (BGR→RGB, flip)
        │
        ▼
MediaPipe Pose Detection
        │
        ▼
33 Body Landmark Extraction
        │
    ┌───┴───────────────────────┐
    ▼                           ▼
Joint Angle Calculation    Body Alignment Check
(Shoulder→Elbow→Wrist)     (Shoulder→Hip→Ankle)
    │                           │
    ▼                           ▼
Push-Up State Machine      Form Analyzer
(UP/DOWN/TRANSITION)       (Score + Feedback)
    │                           │
    └───────────┬───────────────┘
                ▼
          MetricsTracker
    (reps, speed, calories, time)
                │
        ┌───────┴──────────┐
        ▼                  ▼
  HUD Overlay        Streamlit UI
  (OpenCV)           (Charts + Metrics)
                          │
                          ▼
                    SQLite Database
                    (Session History)
```

---

## 🛠 Technology Stack

| Layer | Technology |
|---|---|
| Computer Vision | MediaPipe Pose, OpenCV |
| Data Processing | NumPy, Pandas |
| Visualization | Plotly |
| Web UI | Streamlit + Custom CSS |
| Database | SQLite (via sqlite3) |
| Language | Python 3.9+ |

---

## 📁 Project Structure

```
RepSenseAI/
├── app.py                    # Main Streamlit application
│
├── vision/
│   ├── pose_detector.py      # MediaPipe pose detection + skeleton drawing
│   └── angle_calculator.py   # Vector-based joint angle computation
│
├── exercise/
│   ├── pushup_counter.py     # FSM-based rep counter with speed tracking
│   └── form_analyzer.py      # Biomechanical form evaluation + scoring
│
├── analytics/
│   ├── metrics.py            # Session metrics tracking + aggregation
│   └── charts.py             # Plotly dark-theme chart generators
│
├── database/
│   └── db_manager.py         # SQLite session persistence
│
├── ui/
│   └── styles.py             # Custom CSS + HTML component generators
│
├── utils/
│   └── helpers.py            # HUD overlay, text rendering utilities
│
├── requirements.txt
└── README.md
```

---

## 🚀 Installation

### Prerequisites
- Python 3.9 or higher
- A working webcam
- pip package manager

### Steps

```bash
# 1. Clone the repository
git clone https://github.com/yourusername/repsense-ai.git
cd repsense-ai

# 2. Create and activate virtual environment (recommended)
python -m venv venv
source venv/bin/activate      # Linux/macOS
# venv\Scripts\activate       # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the application
streamlit run app.py
```

The app will open automatically at `http://localhost:8501`

---

## 🎮 Usage

1. **Open the app** — Navigate to `http://localhost:8501`
2. **Position yourself** — Ensure your full body is visible from a side angle
3. **Click START SESSION** — Webcam activates with the AI overlay
4. **Begin push-ups** — The system auto-detects and counts each rep
5. **Monitor live feedback** — Form corrections appear in real time
6. **Click STOP SESSION** — Workout ends
7. **Click SAVE SESSION** — Data is persisted to history

### Optimal Setup Tips
- Position camera at **side-angle** or **slightly in front**
- Ensure **good lighting** (avoid strong backlight)
- Keep **full body in frame** (head to feet)
- Wear **form-fitting clothing** for better landmark detection

---

## 🧠 Algorithms

### Joint Angle Computation
Uses the **dot product formula** between vectors at the elbow vertex:

```
cos(θ) = (BA⃗ · BC⃗) / (|BA⃗| × |BC⃗|)
```

### Push-Up State Machine
```
UNKNOWN → UP (elbow > 160°)
UP → TRANSITION_DOWN (elbow < 120°)
TRANSITION_DOWN → DOWN (elbow < 70°)
DOWN → TRANSITION_UP (elbow > 130°)
TRANSITION_UP → UP (elbow > 160°)  ← REP COUNTED
```

### Form Scoring
```
base_score = 100
deductions:
  - hip deviation 15–25°  → -10
  - hip deviation > 25°   → -20 or -25
  - insufficient depth     → -15
final_score = max(0, base_score - deductions)
```

### Calorie Estimation
```
calories = total_reps × 0.4 kcal/rep
```

---

## 📊 Analytics

The dashboard includes 4 real-time Plotly charts:

- **Rep Speed Analysis** — Bar chart of per-rep durations with color-coded speed zones
- **Rep Timeline** — Cumulative rep count over workout time
- **Form Accuracy Trend** — Form score evolution throughout the workout
- **Speed Distribution** — Donut chart showing Fast/Optimal/Slow ratio

---

## 🔮 Future Extensions

- [ ] **Multi-Exercise Support** — Squats, deadlifts, pull-ups
- [ ] **Plank Detection** — Hold duration + alignment tracking
- [ ] **Yoga Pose Correction** — Static pose matching
- [ ] **Voice Feedback** — pyttsx3 audio coaching
- [ ] **3D Skeleton Visualization** — Three.js pose rendering
- [ ] **Progressive Overload Tracker** — Week-over-week improvement analysis
- [ ] **Multi-Person Tracking** — Simultaneous tracking for group sessions
- [ ] **Export Reports** — PDF workout summaries
- [ ] **REST API** — FastAPI backend for mobile app integration

---

## 📄 License

MIT License — Free for academic and personal use.

---

<div align="center">
Built with 💙 for IIT-level AI project demonstration
</div>
