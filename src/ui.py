"""Premium dark UI primitives for internal growth analytics."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

import plotly.graph_objects as go
import streamlit as st

CHART_LAYOUT = dict(
    template="plotly_dark",
    font=dict(family="Inter, Segoe UI, system-ui, sans-serif", size=12, color="#E5E7EB"),
    margin=dict(l=48, r=24, t=58, b=46),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(size=11)),
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
)

PM_LIFECYCLE_COLORS = {
    "active": "#60A5FA",
    "habitual": "#34D399",
    "at-risk": "#FBBF24",
    "dormant": "#94A3B8",
    "churn-risk": "#F87171",
}

RetentionHealth = Literal["Healthy", "Improving", "At Risk", "Critical"]


@dataclass(frozen=True)
class Trend:
    delta: float
    suffix: str = "%"
    label: str = "vs prev period"

    def render(self) -> str:
        arrow = "▲" if self.delta >= 0 else "▼"
        sign = "+" if self.delta >= 0 else ""
        if self.suffix == "%":
            return f"{arrow} {sign}{self.delta:.1f}{self.suffix} {self.label}"
        return f"{arrow} {sign}{self.delta:.1f}{self.suffix} {self.label}"


def inject_styles() -> None:
    st.markdown(
        """
        <style>
        :root {
          --bg: #0B1020;
          --panel: rgba(255,255,255,0.06);
          --panel2: rgba(255,255,255,0.04);
          --border: rgba(255,255,255,0.10);
          --muted: rgba(229,231,235,0.70);
          --text: #E5E7EB;
          --title: #F9FAFB;
          --accent: #60A5FA;
          --green: #34D399;
          --amber: #FBBF24;
          --red: #F87171;
        }
        .stApp { background: radial-gradient(1200px 800px at 20% 0%, rgba(96,165,250,0.14), transparent 45%), var(--bg); }
        [data-testid="stSidebar"] { background: linear-gradient(180deg, rgba(255,255,255,0.04) 0%, rgba(255,255,255,0.02) 100%); border-right: 1px solid var(--border); }
        [data-testid="stSidebar"] * { color: var(--text) !important; }
        h1, h2, h3 { color: var(--title) !important; letter-spacing: -0.02em; }
        [data-testid="stMetricValue"] { color: var(--title) !important; }
        [data-testid="stCaptionContainer"] { color: var(--muted) !important; }
        .pm-section-title { font-size: 0.78rem; font-weight: 700; letter-spacing: 0.09em; text-transform: uppercase; color: rgba(229,231,235,0.72); margin: 0.6rem 0 0.35rem; }

        .kpi-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; }
        @media (max-width: 1100px) { .kpi-grid { grid-template-columns: repeat(2, 1fr); } }
        .kpi-card {
          background: linear-gradient(180deg, rgba(255,255,255,0.08) 0%, rgba(255,255,255,0.05) 100%);
          border: 1px solid var(--border);
          border-radius: 14px;
          padding: 14px 14px 12px;
          box-shadow: 0 10px 24px rgba(0,0,0,0.18);
        }
        .kpi-top { display: flex; align-items: center; justify-content: space-between; gap: 8px; }
        .kpi-label { font-size: 0.72rem; font-weight: 700; letter-spacing: 0.08em; text-transform: uppercase; color: rgba(229,231,235,0.72); }
        .kpi-badge { font-size: 0.68rem; font-weight: 800; letter-spacing: 0.06em; padding: 4px 8px; border-radius: 999px; border: 1px solid var(--border); background: rgba(255,255,255,0.04); }
        .kpi-value { font-size: 1.55rem; font-weight: 800; color: var(--title); margin-top: 8px; line-height: 1.2; }
        .kpi-sub { font-size: 0.82rem; color: rgba(229,231,235,0.78); margin-top: 6px; line-height: 1.35; }
        .kpi-trend { margin-top: 10px; font-size: 0.78rem; font-weight: 650; color: rgba(229,231,235,0.78); display: flex; align-items: center; gap: 8px; }
        .kpi-dot { width: 8px; height: 8px; border-radius: 50%; display: inline-block; }

        .insight-rail {
          background: linear-gradient(180deg, rgba(96,165,250,0.14) 0%, rgba(255,255,255,0.05) 100%);
          border: 1px solid var(--border);
          border-radius: 14px;
          padding: 14px;
        }
        .critical-item { padding: 10px 10px; border-radius: 12px; border: 1px solid rgba(255,255,255,0.10); background: rgba(0,0,0,0.10); margin-bottom: 10px; }
        .critical-kicker { font-size: 0.68rem; font-weight: 800; letter-spacing: 0.08em; text-transform: uppercase; color: rgba(229,231,235,0.72); margin-bottom: 6px; }
        .critical-text { font-size: 0.92rem; color: var(--title); line-height: 1.35; }

        .pm-insight-card {
          background: linear-gradient(180deg, rgba(255,255,255,0.06) 0%, rgba(255,255,255,0.04) 100%);
          border: 1px solid var(--border);
          border-radius: 14px;
          padding: 12px 12px;
        }
        .pm-insight-tag { font-size: 0.68rem; font-weight: 800; letter-spacing: 0.08em; text-transform: uppercase; color: rgba(229,231,235,0.72); }
        .pm-insight-title { font-weight: 750; color: var(--title); font-size: 0.98rem; margin-top: 8px; margin-bottom: 6px; letter-spacing: -0.01em; }
        .pm-insight-body { color: rgba(229,231,235,0.78); font-size: 0.86rem; line-height: 1.42; }

        .pm-rec-card {
          background: linear-gradient(180deg, rgba(251,191,36,0.14) 0%, rgba(255,255,255,0.04) 100%);
          border: 1px solid rgba(251,191,36,0.28);
          border-radius: 14px;
          padding: 14px 14px 12px;
        }
        .pm-rec-priority { font-size: 0.68rem; font-weight: 900; letter-spacing: 0.08em; text-transform: uppercase; color: rgba(251,191,36,0.95); }
        .pm-rec-title { font-weight: 800; color: var(--title); margin: 8px 0 6px; font-size: 1.02rem; }
        .pm-rec-body { font-size: 0.86rem; color: rgba(229,231,235,0.78); line-height: 1.45; }
        .pm-rec-action { font-size: 0.82rem; color: rgba(229,231,235,0.86); margin-top: 8px; }

        .brief-card {
          background: linear-gradient(180deg, rgba(255,255,255,0.07) 0%, rgba(255,255,255,0.04) 100%);
          border: 1px solid var(--border);
          border-radius: 14px;
          padding: 14px;
        }
        .brief-title { font-weight: 850; letter-spacing: -0.02em; color: var(--title); font-size: 1.05rem; margin-bottom: 8px; }
        .brief-bullet { color: rgba(229,231,235,0.80); font-size: 0.88rem; line-height: 1.45; margin-bottom: 6px; }
        </style>
        """,
        unsafe_allow_html=True,
    )


def page_header(title: str, subtitle: str) -> None:
    st.markdown(f"## {title}")
    st.caption(subtitle)

def section_title(text: str) -> None:
    st.markdown(f'<div class="pm-section-title">{text}</div>', unsafe_allow_html=True)


def retention_health_badge(status: RetentionHealth) -> str:
    color = {
        "Healthy": "#34D399",
        "Improving": "#60A5FA",
        "At Risk": "#FBBF24",
        "Critical": "#F87171",
    }[status]
    return (
        f'<span class="kpi-badge" style="border-color: {color}55; color: {color}; '
        f'background: {color}14;">{status}</span>'
    )


def kpi_card(
    label: str,
    value: str,
    subtext: str,
    *,
    trend: Trend | None = None,
    health: RetentionHealth | None = None,
    badge_text: str | None = None,
) -> None:
    badge = retention_health_badge(health) if health else (f'<span class="kpi-badge">{badge_text}</span>' if badge_text else "")
    trend_html = ""
    if trend is not None:
        dot_color = "#34D399" if trend.delta >= 0 else "#F87171"
        trend_html = (
            f'<div class="kpi-trend"><span class="kpi-dot" style="background:{dot_color};"></span>'
            f"{trend.render()}</div>"
        )
    st.markdown(
        f"""
        <div class="kpi-card">
          <div class="kpi-top">
            <div class="kpi-label">{label}</div>
            {badge}
          </div>
          <div class="kpi-value">{value}</div>
          <div class="kpi-sub">{subtext}</div>
          {trend_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def kpi_row(cards: list[dict]) -> None:
    st.markdown('<div class="kpi-grid">', unsafe_allow_html=True)
    for c in cards:
        kpi_card(**c)
    st.markdown("</div>", unsafe_allow_html=True)


def insight_card(title: str, body: str, tag: str = "Product insight") -> None:
    st.markdown(
        f'<div class="pm-insight-card"><div class="pm-insight-tag">{tag}</div>'
        f'<div class="pm-insight-title">{title}</div>'
        f'<div class="pm-insight-body">{body}</div></div>',
        unsafe_allow_html=True,
    )


def recommendation_card(title: str, body: str, action: str, priority: str = "Medium") -> None:
    st.markdown(
        f'<div class="pm-rec-card"><span class="pm-rec-priority">{priority} priority</span>'
        f'<div class="pm-rec-title">{title}</div><div class="pm-rec-body">{body}</div>'
        f'<div class="pm-rec-action"><strong>Suggested action:</strong> {action}</div></div>',
        unsafe_allow_html=True,
    )

def critical_insights(items: list[tuple[str, str]]) -> None:
    st.markdown('<div class="insight-rail">', unsafe_allow_html=True)
    st.markdown('<div class="pm-section-title" style="margin-top:0">Critical Insights</div>', unsafe_allow_html=True)
    for kicker, text in items:
        st.markdown(
            f'<div class="critical-item"><div class="critical-kicker">{kicker}</div>'
            f'<div class="critical-text">{text}</div></div>',
            unsafe_allow_html=True,
        )
    st.markdown("</div>", unsafe_allow_html=True)


def leadership_brief(title: str, bullets: list[str]) -> None:
    st.markdown('<div class="brief-card">', unsafe_allow_html=True)
    st.markdown(f'<div class="brief-title">{title}</div>', unsafe_allow_html=True)
    for b in bullets:
        st.markdown(f'<div class="brief-bullet">• {b}</div>', unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)


def apply_chart_style(fig: go.Figure, title: str, y_title: str = "", x_title: str = "") -> go.Figure:
    fig.update_layout(title=dict(text=title, x=0, xanchor="left", font=dict(size=15)), **CHART_LAYOUT)
    fig.update_xaxes(showgrid=True, gridcolor="rgba(148,163,184,0.15)", zeroline=False)
    fig.update_yaxes(showgrid=True, gridcolor="rgba(148,163,184,0.15)", zeroline=False)
    if y_title:
        fig.update_yaxes(title_text=y_title)
    if x_title:
        fig.update_xaxes(title_text=x_title)
    return fig


def metric_row(cards: list[tuple[str, str, str]], columns: int = 4) -> None:
    cols = st.columns(columns)
    for col, (label, value, help_text) in zip(cols, cards):
        with col:
            kpi_card(label, value, help_text)


def insight_row(insights: list[tuple[str, str, str]]) -> None:
    cols = st.columns(len(insights))
    for col, (title, body, tag) in zip(cols, insights):
        with col:
            insight_card(title, body, tag)
