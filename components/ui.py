"""Peças visuais reutilizadas pelas telas."""

from html import escape
from pathlib import Path

import streamlit as st

from dados.models import STATUS_COLORS

ROOT = Path(__file__).resolve().parent.parent
LOGO = ROOT / "assets" / "logo.png"
CSS = ROOT / "assets" / "css" / "main.css"


def inject_css():
    if CSS.exists():
        st.html(f"<style>{CSS.read_text(encoding='utf-8')}</style>")


def page_header(title, subtitle=None, eyebrow=None):
    parts = ['<div class="page-head">']

    if eyebrow:
        parts.append(f'<div class="eyebrow">{escape(eyebrow)}</div>')

    parts.append(f"<h1>{escape(title)}</h1>")

    if subtitle:
        parts.append(f"<p>{escape(subtitle)}</p>")

    parts.append("</div>")
    st.markdown("".join(parts), unsafe_allow_html=True)


def stat_card(label, value, hint=None, tone="var(--berry)"):
    hint_html = f'<div class="hint">{escape(hint)}</div>' if hint else ""

    st.markdown(
        f'<div class="stat" style="--tone:{tone}">'
        f'<div class="label">{escape(label)}</div>'
        f'<div class="value">{escape(str(value))}</div>'
        f"{hint_html}</div>",
        unsafe_allow_html=True,
    )


def status_badge(status, soft=False):
    color = STATUS_COLORS.get(status, "#7D9FC3")
    css = "badge soft" if soft else "badge"
    return f'<span class="{css}" style="--tone:{color}">{escape(status)}</span>'


def payment_badge(paid):
    if paid:
        return '<span class="badge" style="--tone:#5E9C7F">Pago</span>'
    return '<span class="badge soft" style="--tone:#C9894B">A receber</span>'


def empty_state(text):
    st.markdown(f'<div class="empty">{escape(text)}</div>', unsafe_allow_html=True)


def status_legend():
    items = "".join(
        f'<span style="--tone:{color}">{escape(status)}</span>'
        for status, color in STATUS_COLORS.items()
    )
    st.markdown(f'<div class="legend">{items}</div>', unsafe_allow_html=True)


def slot_row(time_text, end_text, title, meta, right_html="", tone=None):
    tone_css = f' style="--tone:{tone}"' if tone else ""

    st.markdown(
        f'<div class="slot"{tone_css}>'
        f'<div class="time">{escape(time_text)}<small>{escape(end_text)}</small></div>'
        f'<div><div class="who-name">{escape(title)}</div><div class="meta">{escape(meta)}</div></div>'
        f"<div>{right_html}</div></div>",
        unsafe_allow_html=True,
    )
