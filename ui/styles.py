"""
RepSense AI - UI Styles Module
Premium dark neon CSS theme for Streamlit dashboard.
"""

CUSTOM_CSS = """
<style>
/* ─── Google Fonts ──────────────────────────────────────────────────────── */
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Rajdhani:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;600&display=swap');

/* ─── Root Variables ────────────────────────────────────────────────────── */
:root {
    --bg-primary: #050508;
    --bg-secondary: #0D0D14;
    --bg-card: #111827;
    --bg-card-hover: #1A2236;
    --accent-blue: #00D4FF;
    --accent-purple: #8B5CF6;
    --accent-green: #10B981;
    --accent-orange: #F59E0B;
    --accent-red: #EF4444;
    --text-primary: #F9FAFB;
    --text-secondary: #9CA3AF;
    --border-subtle: rgba(0, 212, 255, 0.15);
    --glow-blue: 0 0 20px rgba(0, 212, 255, 0.3);
    --glow-purple: 0 0 20px rgba(139, 92, 246, 0.3);
}

/* ─── Global Reset ──────────────────────────────────────────────────────── */
.stApp {
    background: var(--bg-primary) !important;
    background-image:
        radial-gradient(ellipse at 20% 0%, rgba(139, 92, 246, 0.08) 0%, transparent 50%),
        radial-gradient(ellipse at 80% 0%, rgba(0, 212, 255, 0.05) 0%, transparent 50%) !important;
}

.main .block-container {
    padding: 1.5rem 2rem !important;
    max-width: 1400px;
}

/* ─── Typography ────────────────────────────────────────────────────────── */
h1, h2, h3, h4 {
    font-family: 'Orbitron', monospace !important;
    letter-spacing: 0.05em;
}

p, span, div, label {
    font-family: 'Rajdhani', sans-serif !important;
}

/* ─── Header / Brand ────────────────────────────────────────────────────── */
.repsense-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 1.5rem 2rem;
    background: linear-gradient(135deg, rgba(0, 212, 255, 0.05), rgba(139, 92, 246, 0.05));
    border: 1px solid var(--border-subtle);
    border-radius: 16px;
    margin-bottom: 1.5rem;
    position: relative;
    overflow: hidden;
}

.repsense-header::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, transparent, var(--accent-blue), var(--accent-purple), transparent);
}

.brand-title {
    font-family: 'Orbitron', monospace !important;
    font-size: 2.2rem !important;
    font-weight: 900;
    background: linear-gradient(135deg, var(--accent-blue), var(--accent-purple));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin: 0 !important;
    letter-spacing: 0.1em;
}

.brand-subtitle {
    font-family: 'Rajdhani', sans-serif;
    color: var(--text-secondary);
    font-size: 0.9rem;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    margin-top: 0.25rem;
}

.status-badge {
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.4rem 1rem;
    border-radius: 50px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.75rem;
    letter-spacing: 0.1em;
    text-transform: uppercase;
}

.status-active {
    background: rgba(16, 185, 129, 0.15);
    border: 1px solid rgba(16, 185, 129, 0.4);
    color: var(--accent-green);
}

.status-inactive {
    background: rgba(156, 163, 175, 0.1);
    border: 1px solid rgba(156, 163, 175, 0.2);
    color: var(--text-secondary);
}

/* ─── Metric Cards ──────────────────────────────────────────────────────── */
.metric-card {
    background: var(--bg-card);
    border: 1px solid var(--border-subtle);
    border-radius: 12px;
    padding: 1.2rem 1.4rem;
    text-align: center;
    position: relative;
    overflow: hidden;
    transition: all 0.2s ease;
}

.metric-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: var(--accent-blue);
    opacity: 0.6;
}

.metric-card.purple::before { background: var(--accent-purple); }
.metric-card.green::before { background: var(--accent-green); }
.metric-card.orange::before { background: var(--accent-orange); }

.metric-icon {
    font-size: 1.6rem;
    margin-bottom: 0.3rem;
}

.metric-label {
    font-family: 'Rajdhani', sans-serif;
    font-size: 0.72rem;
    text-transform: uppercase;
    letter-spacing: 0.15em;
    color: var(--text-secondary);
    margin-bottom: 0.3rem;
}

.metric-value {
    font-family: 'Orbitron', monospace;
    font-size: 2rem;
    font-weight: 700;
    color: var(--accent-blue);
    line-height: 1;
}

.metric-card.purple .metric-value { color: var(--accent-purple); }
.metric-card.green .metric-value { color: var(--accent-green); }
.metric-card.orange .metric-value { color: var(--accent-orange); }

/* ─── Form Score Bar ────────────────────────────────────────────────────── */
.form-score-container {
    background: var(--bg-card);
    border: 1px solid var(--border-subtle);
    border-radius: 12px;
    padding: 1.2rem;
    margin: 0.5rem 0;
}

.form-score-bar-bg {
    background: rgba(255,255,255,0.05);
    border-radius: 50px;
    height: 10px;
    overflow: hidden;
}

.form-score-bar-fill {
    height: 100%;
    border-radius: 50px;
    background: linear-gradient(90deg, var(--accent-blue), var(--accent-purple));
    transition: width 0.5s ease;
    box-shadow: 0 0 8px rgba(0, 212, 255, 0.4);
}

/* ─── Feedback Messages ─────────────────────────────────────────────────── */
.feedback-good {
    background: rgba(16, 185, 129, 0.1);
    border-left: 3px solid var(--accent-green);
    padding: 0.5rem 0.8rem;
    border-radius: 0 8px 8px 0;
    margin: 0.25rem 0;
    font-family: 'Rajdhani', sans-serif;
    color: var(--accent-green);
    font-size: 0.9rem;
}

.feedback-warning {
    background: rgba(245, 158, 11, 0.1);
    border-left: 3px solid var(--accent-orange);
    padding: 0.5rem 0.8rem;
    border-radius: 0 8px 8px 0;
    margin: 0.25rem 0;
    font-family: 'Rajdhani', sans-serif;
    color: var(--accent-orange);
    font-size: 0.9rem;
}

.feedback-error {
    background: rgba(239, 68, 68, 0.1);
    border-left: 3px solid var(--accent-red);
    padding: 0.5rem 0.8rem;
    border-radius: 0 8px 8px 0;
    margin: 0.25rem 0;
    font-family: 'Rajdhani', sans-serif;
    color: var(--accent-red);
    font-size: 0.9rem;
}

/* ─── Stage Display ─────────────────────────────────────────────────────── */
.stage-display {
    background: var(--bg-card);
    border: 1px solid var(--border-subtle);
    border-radius: 12px;
    padding: 0.8rem 1.2rem;
    text-align: center;
    font-family: 'Orbitron', monospace;
    font-size: 0.9rem;
    letter-spacing: 0.1em;
    color: var(--accent-blue);
    text-transform: uppercase;
}

/* ─── Section Headers ───────────────────────────────────────────────────── */
.section-header {
    font-family: 'Orbitron', monospace;
    font-size: 0.85rem;
    font-weight: 700;
    color: var(--text-secondary);
    text-transform: uppercase;
    letter-spacing: 0.2em;
    margin: 1rem 0 0.75rem;
    padding-bottom: 0.5rem;
    border-bottom: 1px solid var(--border-subtle);
}

/* ─── History Table ─────────────────────────────────────────────────────── */
.history-table {
    width: 100%;
    border-collapse: collapse;
    font-family: 'Rajdhani', sans-serif;
    font-size: 0.9rem;
}

.history-table th {
    font-family: 'Orbitron', monospace;
    font-size: 0.7rem;
    text-transform: uppercase;
    letter-spacing: 0.15em;
    color: var(--text-secondary);
    padding: 0.75rem 1rem;
    border-bottom: 1px solid var(--border-subtle);
    text-align: left;
}

.history-table td {
    padding: 0.65rem 1rem;
    color: var(--text-primary);
    border-bottom: 1px solid rgba(255,255,255,0.04);
}

.history-table tr:hover td {
    background: var(--bg-card-hover);
}

/* ─── Buttons ───────────────────────────────────────────────────────────── */
.stButton > button {
    font-family: 'Orbitron', monospace !important;
    font-size: 0.8rem !important;
    letter-spacing: 0.1em !important;
    text-transform: uppercase !important;
    border-radius: 8px !important;
    border: 1px solid var(--accent-blue) !important;
    background: rgba(0, 212, 255, 0.08) !important;
    color: var(--accent-blue) !important;
    transition: all 0.2s ease !important;
}

.stButton > button:hover {
    background: rgba(0, 212, 255, 0.18) !important;
    box-shadow: var(--glow-blue) !important;
}

/* Reset button — scoped via .reset-btn wrapper div */
div.reset-btn > div > .stButton > button {
    border-color: rgba(139, 92, 246, 0.5) !important;
    background: rgba(139, 92, 246, 0.07) !important;
    color: var(--accent-purple) !important;
}

div.reset-btn > div > .stButton > button:hover {
    background: rgba(139, 92, 246, 0.16) !important;
    box-shadow: 0 0 18px rgba(139, 92, 246, 0.35) !important;
}

/* ─── Streamlit Overrides ───────────────────────────────────────────────── */
.stSidebar {
    background: var(--bg-secondary) !important;
    border-right: 1px solid var(--border-subtle) !important;
}

.stSidebar .sidebar-content {
    background: var(--bg-secondary) !important;
}

[data-testid="stMetricValue"] {
    font-family: 'Orbitron', monospace !important;
    color: var(--accent-blue) !important;
}

[data-testid="stMetricLabel"] {
    font-family: 'Rajdhani', sans-serif !important;
    color: var(--text-secondary) !important;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    font-size: 0.75rem !important;
}

div[data-testid="stMetric"] {
    background: var(--bg-card) !important;
    border: 1px solid var(--border-subtle) !important;
    border-radius: 12px !important;
    padding: 1rem 1.2rem !important;
}

.stSelectbox > div {
    background: var(--bg-card) !important;
    border-color: var(--border-subtle) !important;
}

.stSlider > div {
    color: var(--accent-blue) !important;
}

/* ─── Alert/Info boxes ──────────────────────────────────────────────────── */
.stAlert {
    background: rgba(0, 212, 255, 0.05) !important;
    border: 1px solid var(--border-subtle) !important;
    border-radius: 8px !important;
}

/* ─── Plotly chart containers ───────────────────────────────────────────── */
.js-plotly-plot .plotly {
    border-radius: 12px !important;
}

/* ─── Camera container ──────────────────────────────────────────────────── */
.camera-container {
    border-radius: 16px;
    overflow: hidden;
    border: 1px solid var(--border-subtle);
    box-shadow: var(--glow-blue);
}

/* ─── Divider ───────────────────────────────────────────────────────────── */
.neon-divider {
    height: 1px;
    background: linear-gradient(90deg, transparent, var(--accent-blue), var(--accent-purple), transparent);
    margin: 1.5rem 0;
    opacity: 0.4;
}

/* ─── Grade badge ───────────────────────────────────────────────────────── */
.grade-badge {
    display: inline-block;
    padding: 0.2rem 0.6rem;
    border-radius: 6px;
    font-family: 'Orbitron', monospace;
    font-size: 0.85rem;
    font-weight: 700;
}

.grade-a-plus { background: rgba(16,185,129,0.2); color: #10B981; border: 1px solid rgba(16,185,129,0.4); }
.grade-a { background: rgba(0,212,255,0.15); color: #00D4FF; border: 1px solid rgba(0,212,255,0.3); }
.grade-b { background: rgba(139,92,246,0.15); color: #8B5CF6; border: 1px solid rgba(139,92,246,0.3); }
.grade-c { background: rgba(245,158,11,0.15); color: #F59E0B; border: 1px solid rgba(245,158,11,0.3); }
.grade-d { background: rgba(239,68,68,0.15); color: #EF4444; border: 1px solid rgba(239,68,68,0.3); }

/* ─── Scrollbar ─────────────────────────────────────────────────────────── */
::-webkit-scrollbar { width: 4px; height: 4px; }
::-webkit-scrollbar-track { background: var(--bg-secondary); }
::-webkit-scrollbar-thumb { background: var(--accent-blue); border-radius: 2px; opacity: 0.5; }

/* ─── Hide default streamlit elements ───────────────────────────────────── */
#MainMenu { visibility: hidden; }
footer { visibility: hidden; }
header { visibility: hidden; }
</style>
"""


def get_metric_card_html(icon: str, label: str, value: str, color_class: str = "") -> str:
    return f"""
    <div class="metric-card {color_class}">
        <div class="metric-icon">{icon}</div>
        <div class="metric-label">{label}</div>
        <div class="metric-value">{value}</div>
    </div>
    """


def get_form_score_bar_html(score: float) -> str:
    color = "#10B981" if score >= 80 else "#F59E0B" if score >= 60 else "#EF4444"
    return f"""
    <div class="form-score-container">
        <div style="display:flex; justify-content:space-between; margin-bottom:0.5rem;">
            <span style="font-family:'Rajdhani',sans-serif; color:#9CA3AF; font-size:0.8rem; text-transform:uppercase; letter-spacing:0.15em;">Form Score</span>
            <span style="font-family:'Orbitron',monospace; color:{color}; font-size:1.1rem; font-weight:700;">{score:.0f}%</span>
        </div>
        <div class="form-score-bar-bg">
            <div class="form-score-bar-fill" style="width:{score}%; background: linear-gradient(90deg, {color}, {color}88);"></div>
        </div>
    </div>
    """


def get_header_html(is_active: bool = False) -> str:
    status = '<span class="status-badge status-active">⬤ &nbsp;LIVE</span>' if is_active else \
             '<span class="status-badge status-inactive">⬤ &nbsp;STANDBY</span>'
    return f"""
    <div class="repsense-header">
        <div>
            <div class="brand-title">RepSense AI</div>
            <div class="brand-subtitle">Intelligent Exercise Recognition &amp; Form Analysis</div>
        </div>
        <div style="display:flex; align-items:center; gap:1rem;">
            {status}
        </div>
    </div>
    """


def get_grade_badge_html(grade: str) -> str:
    grade_map = {
        "A+": "grade-a-plus", "A": "grade-a",
        "B": "grade-b", "C": "grade-c", "D": "grade-d"
    }
    css_class = grade_map.get(grade, "grade-b")
    return f'<span class="grade-badge {css_class}">{grade}</span>'


def get_stage_display_html(stage_label: str) -> str:
    return f'<div class="stage-display">{stage_label}</div>'


def get_section_header_html(title: str) -> str:
    return f'<div class="section-header">{title}</div>'


def get_neon_divider_html() -> str:
    return '<div class="neon-divider"></div>'