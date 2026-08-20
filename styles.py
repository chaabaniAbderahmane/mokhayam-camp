# -*- coding: utf-8 -*-
"""Mobile-first CSS with a clear, high-contrast, Palestinian-inspired visual identity."""
import streamlit as st

GREEN = "#0a7a52"
GREEN_DARK = "#075c3d"
RED = "#c0392b"
BLACK = "#111111"
WHITE = "#ffffff"
GREY_TEXT = "#3a3a3a"


def inject_css(lang: str):
    direction = "rtl" if lang == "ar" else "ltr"
    align = "right" if lang == "ar" else "left"
    font = "'Tajawal', 'Cairo', sans-serif" if lang == "ar" else "'Segoe UI', sans-serif"
    side = "right" if lang == "ar" else "left"

    st.markdown(f"""
    <link href="https://fonts.googleapis.com/css2?family=Tajawal:wght@400;500;700;900&family=Cairo:wght@400;600;800&display=swap" rel="stylesheet">
    <style>
        /* Only set direction on the actual document flow + main content text,
           NEVER on Streamlit's internal structural/transform-driven wrappers
           (that previously broke the sidebar collapse animation). */
        html, body {{
            direction: {direction};
        }}
        [data-testid="stAppViewContainer"] {{
            direction: {direction};
        }}
        .block-container, .block-container * {{
            direction: {direction};
        }}
        [data-testid="stMarkdownContainer"] {{
            text-align: {align};
        }}
        body, p, li, label, span, div, h1, h2, h3, h4, input, textarea {{
            font-family: {font} !important;
        }}
        .stApp {{
            background: #f6f7f6;
        }}

        /* ---------- Make EVERYTHING bigger and readable on a phone ---------- */
        p, li, label, span, div {{
            font-size: 1rem;
        }}
        .block-container {{
            padding-top: 1rem;
            padding-bottom: 5rem;
            padding-left: 1rem;
            padding-right: 1rem;
            max-width: 700px;
        }}

        /* ---------- Force columns to stack on narrow phone screens ----------
           Scoped ONLY to the main content area - never to the sidebar - so we
           don't break Streamlit's own sidebar collapse/resize mechanism. */
        @media (max-width: 700px) {{
            .block-container [data-testid="stHorizontalBlock"] {{
                flex-direction: column !important;
            }}
            .block-container [data-testid="stHorizontalBlock"] > div {{
                width: 100% !important;
                flex: 1 1 100% !important;
                min-width: 100% !important;
            }}
        }}

        /* ---------- Sidebar ----------
           IMPORTANT: no `direction` property is set on the sidebar shell or its
           structural wrappers - only text-align on the inner content, so the
           collapse/expand animation keeps working correctly. */
        [data-testid="stSidebar"] {{
            background: {BLACK};
            direction: ltr !important;
        }}
        [data-testid="stSidebarUserContent"] {{
            text-align: {align};
        }}
        [data-testid="stSidebar"] * {{
            color: {WHITE} !important;
            font-size: 1.05rem !important;
        }}
        [data-testid="stSidebar"] .stButton>button {{
            background: #1c1c1c;
            border: 1px solid #333;
            text-align: {align};
            justify-content: flex-start;
            font-weight: 600;
        }}
        [data-testid="stSidebar"] .stButton>button:hover {{
            background: {GREEN};
            border-color: {GREEN};
        }}

        /* ---------- Header ---------- */
        .flag-bar {{
            height: 7px;
            width: 100%;
            border-radius: 6px;
            background: linear-gradient(90deg, {BLACK} 0 33%, {WHITE} 33% 66%, {GREEN} 66% 100%);
            position: relative;
            margin-bottom: 0.8rem;
            border: 1px solid #ddd;
        }}
        .flag-bar::after {{
            content: "";
            position: absolute;
            {side}: 0;
            top: -100%;
            height: 300%;
            width: 14px;
            background: {RED};
            clip-path: polygon(0 0, 100% 50%, 0 100%);
            {"transform: scaleX(-1);" if lang == "ar" else ""}
        }}
        .brand-title {{
            font-weight: 900;
            font-size: 2rem;
            color: {BLACK};
            margin: 0.3rem 0 0.1rem 0;
            line-height: 1.2;
        }}
        .brand-sub {{
            color: {GREEN_DARK};
            font-weight: 700;
            font-size: 1.15rem;
            margin-bottom: 1.2rem;
        }}
        h1, h2, h3, h4 {{ color: {BLACK}; }}

        /* ---------- Cards ---------- */
        .camp-card {{
            background: {WHITE};
            border: 1px solid #e2e4e3;
            border-{side}: 6px solid {GREEN};
            border-radius: 14px;
            padding: 18px 18px;
            margin-bottom: 14px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.05);
            font-size: 1.05rem;
            line-height: 1.9;
            color: {BLACK};
        }}
        .camp-card.urgent {{ border-{side}-color: {RED}; background: #fff8f7; }}
        .camp-card h4 {{
            margin: 0 0 10px 0;
            color: {BLACK};
            font-size: 1.25rem;
            font-weight: 800;
        }}
        .camp-card b {{ color: {GREEN_DARK}; font-weight: 800; }}
        .camp-card small {{ color: #666; font-size: 0.9rem; }}

        /* ---------- Stat cards ---------- */
        .stat-card {{
            background: {WHITE};
            border-radius: 16px;
            padding: 18px 10px;
            text-align: center;
            border: 2px solid {GREEN};
            box-shadow: 0 2px 8px rgba(0,0,0,0.06);
            margin-bottom: 14px;
        }}
        .stat-num {{ font-size: 2rem; font-weight: 900; color: {BLACK}; line-height: 1.1; }}
        .stat-label {{ font-size: 0.95rem; color: {GREY_TEXT}; margin-top: 4px; font-weight: 600; }}

        /* ---------- Badges ---------- */
        .badge {{
            display: inline-block;
            padding: 6px 16px;
            border-radius: 999px;
            font-size: 0.9rem;
            font-weight: 800;
        }}
        .badge-green {{ background: #dff3ea; color: {GREEN_DARK}; }}
        .badge-red {{ background: #fbe3e0; color: {RED}; }}
        .badge-grey {{ background: #e9e9e9; color: #444; }}
        .badge-gold {{ background: #fff0c2; color: #8a6300; }}

        /* ---------- Buttons ---------- */
        .stButton>button {{
            border-radius: 12px;
            font-weight: 700;
            font-size: 1.05rem;
            padding: 0.6rem 1rem;
            min-height: 3rem;
            width: 100%;
        }}
        .stButton>button[kind="primary"] {{
            background: {GREEN};
            border-color: {GREEN};
            color: {WHITE};
        }}
        .stButton>button[kind="primary"]:hover {{
            background: {GREEN_DARK};
            border-color: {GREEN_DARK};
        }}

        /* ---------- Inputs ---------- */
        .stTextInput input, .stTextArea textarea, .stNumberInput input,
        [data-baseweb="select"] {{
            font-size: 1.05rem !important;
        }}
        label[data-testid="stWidgetLabel"] p {{
            font-size: 1rem !important;
            font-weight: 700 !important;
            color: {BLACK} !important;
        }}

        /* ---------- Tabs ---------- */
        button[data-baseweb="tab"] {{
            font-size: 1rem !important;
            font-weight: 700 !important;
        }}

        /* ---------- Metrics ---------- */
        [data-testid="stMetricValue"] {{ color: {BLACK}; font-size: 1.4rem; }}
        [data-testid="stMetricLabel"] {{ font-size: 0.95rem; font-weight: 700; }}

        /* ---------- Expanders ---------- */
        [data-testid="stExpander"] summary {{
            font-size: 1.05rem;
            font-weight: 700;
        }}

        hr {{ border-color: #e0e0e0; }}
        [data-testid="stCaptionContainer"] {{ font-size: 0.95rem !important; color: #555 !important; }}
    </style>
    """, unsafe_allow_html=True)


def flag_header(title: str, subtitle: str = ""):
    st.markdown(f"""
    <div class="flag-bar"></div>
    <div class="brand-title">{title}</div>
    <div class="brand-sub">{subtitle}</div>
    """, unsafe_allow_html=True)


def stat_card_html(number, label):
    return f"""<div class="stat-card"><div class="stat-num">{number}</div><div class="stat-label">{label}</div></div>"""


def badge(text, kind="grey"):
    return f'<span class="badge badge-{kind}">{text}</span>'
