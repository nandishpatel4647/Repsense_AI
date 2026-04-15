"""
RepSense AI - Charts Module
Plotly-based analytics visualizations with dark neon theme.
"""

import plotly.graph_objects as go
import plotly.express as px
from typing import List, Dict

# ─── Color Palette ────────────────────────────────────────────────────────────
NEON_BLUE = "#00D4FF"
NEON_PURPLE = "#8B5CF6"
NEON_GREEN = "#10B981"
NEON_ORANGE = "#F59E0B"
BG_DARK = "#0A0A0F"
BG_CARD = "#111827"
GRID_COLOR = "#1F2937"
TEXT_COLOR = "#E5E7EB"

BASE_LAYOUT = dict(
    paper_bgcolor=BG_DARK,
    plot_bgcolor=BG_CARD,
    font=dict(color=TEXT_COLOR, family="'Rajdhani', monospace"),
    margin=dict(l=40, r=20, t=40, b=40),
    xaxis=dict(
        gridcolor=GRID_COLOR,
        showgrid=True,
        zeroline=False,
        color=TEXT_COLOR,
    ),
    yaxis=dict(
        gridcolor=GRID_COLOR,
        showgrid=True,
        zeroline=False,
        color=TEXT_COLOR,
    ),
)


def make_rep_speed_chart(rep_times: List[float]) -> go.Figure:
    """Bar chart of individual rep durations with speed color coding."""
    if not rep_times:
        return _empty_chart("Rep Speed — No data yet")

    colors = []
    for t in rep_times:
        if t < 1.2:
            colors.append(NEON_ORANGE)
        elif t <= 3.0:
            colors.append(NEON_GREEN)
        else:
            colors.append(NEON_PURPLE)

    rep_labels = [f"Rep {i+1}" for i in range(len(rep_times))]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=rep_labels,
        y=rep_times,
        marker=dict(
            color=colors,
            line=dict(color="rgba(255,255,255,0.1)", width=1),
        ),
        text=[f"{t:.1f}s" for t in rep_times],
        textposition="outside",
        textfont=dict(color=TEXT_COLOR, size=10),
        hovertemplate="<b>%{x}</b><br>Duration: %{y:.2f}s<extra></extra>",
    ))

    # Optimal zone reference line
    fig.add_hline(y=3.0, line_dash="dot", line_color=NEON_GREEN, opacity=0.5,
                  annotation_text="Optimal max", annotation_position="right",
                  annotation_font=dict(color=NEON_GREEN, size=9))
    fig.add_hline(y=1.2, line_dash="dot", line_color=NEON_ORANGE, opacity=0.5,
                  annotation_text="Fast limit", annotation_position="right",
                  annotation_font=dict(color=NEON_ORANGE, size=9))

    layout = dict(**BASE_LAYOUT)
    layout["title"] = dict(text="⚡ Rep Speed Analysis", font=dict(size=14, color=NEON_BLUE))
    layout["yaxis"]["title"] = "Duration (s)"
    layout["showlegend"] = False
    fig.update_layout(**layout)
    return fig


def make_reps_timeline_chart(intensity_data: List[Dict]) -> go.Figure:
    """Line chart showing cumulative reps over workout time."""
    if not intensity_data:
        return _empty_chart("Rep Timeline — No data yet")

    times = [d["time"] for d in intensity_data]
    reps = [d["reps"] for d in intensity_data]

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=times,
        y=reps,
        mode="lines+markers",
        line=dict(color=NEON_BLUE, width=2.5, shape="spline"),
        marker=dict(color=NEON_BLUE, size=5),
        fill="tozeroy",
        fillcolor=f"rgba(0, 212, 255, 0.08)",
        hovertemplate="Time: %{x:.0f}s<br>Reps: %{y}<extra></extra>",
    ))

    layout = dict(**BASE_LAYOUT)
    layout["title"] = dict(text="📈 Rep Timeline", font=dict(size=14, color=NEON_BLUE))
    layout["xaxis"]["title"] = "Time (s)"
    layout["yaxis"]["title"] = "Total Reps"
    fig.update_layout(**layout)
    return fig


def make_form_accuracy_chart(form_trend: List[Dict]) -> go.Figure:
    """Area chart showing form score over time."""
    if not form_trend:
        return _empty_chart("Form Accuracy — No data yet")

    times = [d["time"] for d in form_trend]
    scores = [d["score"] for d in form_trend]

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=times,
        y=scores,
        mode="lines",
        line=dict(color=NEON_GREEN, width=2),
        fill="tozeroy",
        fillcolor="rgba(16, 185, 129, 0.1)",
        hovertemplate="Time: %{x:.0f}s<br>Score: %{y:.1f}%<extra></extra>",
    ))

    # Perfect form line
    fig.add_hline(y=90, line_dash="dash", line_color=NEON_GREEN, opacity=0.3,
                  annotation_text="Excellent", annotation_position="right",
                  annotation_font=dict(color=NEON_GREEN, size=9))

    layout = dict(**BASE_LAYOUT)
    layout["title"] = dict(text="🎯 Form Accuracy Trend", font=dict(size=14, color=NEON_GREEN))
    layout["xaxis"]["title"] = "Time (s)"
    layout["yaxis"]["title"] = "Form Score (%)"
    layout["yaxis"]["range"] = [0, 105]
    fig.update_layout(**layout)
    return fig


def make_speed_distribution_chart(rep_times: List[float]) -> go.Figure:
    """Donut chart showing speed distribution."""
    if not rep_times:
        return _empty_chart("Speed Distribution — No data yet")

    fast = sum(1 for t in rep_times if t < 1.2)
    optimal = sum(1 for t in rep_times if 1.2 <= t <= 3.0)
    slow = sum(1 for t in rep_times if t > 3.0)

    labels = ["Fast ⚡", "Optimal ✓", "Slow 🐢"]
    values = [fast, optimal, slow]
    colors = [NEON_ORANGE, NEON_GREEN, NEON_PURPLE]

    # Filter out zeros
    filtered = [(l, v, c) for l, v, c in zip(labels, values, colors) if v > 0]
    if not filtered:
        return _empty_chart("Speed Distribution — No data yet")

    labels, values, colors = zip(*filtered)

    fig = go.Figure(go.Pie(
        labels=list(labels),
        values=list(values),
        hole=0.6,
        marker=dict(colors=list(colors), line=dict(color=BG_DARK, width=2)),
        textfont=dict(color=TEXT_COLOR, size=11),
        hovertemplate="%{label}: %{value} reps (%{percent})<extra></extra>",
    ))

    layout = dict(**BASE_LAYOUT)
    layout["title"] = dict(text="🏃 Speed Distribution", font=dict(size=14, color=NEON_PURPLE))
    layout["showlegend"] = True
    layout["legend"] = dict(font=dict(color=TEXT_COLOR))
    fig.update_layout(**layout)
    return fig


def _empty_chart(title: str) -> go.Figure:
    """Placeholder chart when no data is available."""
    fig = go.Figure()
    fig.add_annotation(
        text="Start your workout to see data",
        xref="paper", yref="paper",
        x=0.5, y=0.5, showarrow=False,
        font=dict(size=14, color=GRID_COLOR),
    )
    layout = dict(**BASE_LAYOUT)
    layout["title"] = dict(text=title, font=dict(size=14, color=NEON_BLUE))
    fig.update_layout(**layout)
    return fig
