# -*- coding: utf-8 -*-
"""Mobile-first CSS with a subtle Palestinian-inspired visual identity."""
import streamlit as st

GREEN = "#0b6e4f"
RED = "#c0392b"
BLACK = "#101010"
WHITE = "#ffffff"


def inject_css(lang: str):
    direction = "rtl" if lang == "ar" else "ltr"
    align = "right" if lang == "ar" else "left"
    font = "'Tajawal', 'Cairo', sans-serif" if lang == "ar" else "'Segoe UI', sans-serif"

    st.markdown(f"""
    <link href="https://fonts.googleapis.com/css2?family=Tajawal:wght@400;500;700;900&family=Cairo:wght@400;600;800&display=swap" rel="stylesheet">
    <style>
        html, body, [class*="css"] {{
            direction: {direction};
            text-align: {align};
            font-family: {font};
        }}
        .stApp {{
            background: linear-gradient(180deg, #fbfbf9 0%, #f4f6f5 100%);
        }}
        [data-testid="stSidebar"] {{
            background: {BLACK};
        }}
        [data-testid="stSidebar"] * {{
            color: {WHITE} !important;
        }}
        .block-container {{
            padding-top: 1.2rem;
            padding-bottom: 4rem;
            max-width: 900px;
        }}
        /* Top accent bar - Palestinian flag inspired */
        .flag-bar {{
            height: 6px;
            width: 100%;
            border-radius: 6px;
            background: linear-gradient(90deg, {BLACK} 0 33%, {WHITE} 33% 66%, {GREEN} 66% 100%);
            position: relative;
            margin-bottom: 0.6rem;
        }}
        .flag-bar::after {{
            content: "";
            position: absolute;
            {"left" if lang == "ar" else "right"}: 0;
            top: -100%;
            height: 300%;
            width: 12px;
            background: {RED};
            clip-path: polygon(0 0, 100% 50%, 0 100%);
            {"transform: scaleX(-1);" if lang == "ar" else ""}
        }}
        .brand-title {{
            font-weight: 900;
            font-size: 1.6rem;
            color: {BLACK};
            margin: 0.2rem 0 0.1rem 0;
        }}
        .brand-sub {{
            color: {GREEN};
            font-weight: 600;
            font-size: 0.95rem;
            margin-bottom: 1rem;
        }}
        /* Cards */
        .camp-card {{
            background: {WHITE};
            border: 1px solid #e7e9e8;
            border-{"right" if lang=="ar" else "left"}: 5px solid {GREEN};
            border-radius: 14px;
            padding: 16px 18px;
            margin-bottom: 12px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.04);
        }}
        .camp-card.urgent {{ border-{"right" if lang=="ar" else "left"}-color: {RED}; }}
        .camp-card h4 {{ margin: 0 0 6px 0; color: {BLACK}; }}
        .stat-card {{
            background: {WHITE};
            border-radius: 16px;
            padding: 14px;
            text-align: center;
            border: 1px solid #eee;
            box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        }}
        .stat-num {{ font-size: 1.6rem; font-weight: 900; color: {BLACK}; }}
        .stat-label {{ font-size: 0.8rem; color: #555; margin-top: 2px; }}
        .badge {{
            display: inline-block;
            padding: 3px 12px;
            border-radius: 999px;
            font-size: 0.78rem;
            font-weight: 700;
        }}
        .badge-green {{ background: #e6f4ef; color: {GREEN}; }}
        .badge-red {{ background: #fbe9e7; color: {RED}; }}
        .badge-grey {{ background: #eee; color: #555; }}
        .badge-gold {{ background: #fff6dd; color: #a67c00; }}
        /* Buttons */
        .stButton>button {{
            border-radius: 12px;
            font-weight: 700;
            padding: 0.5rem 1rem;
            min-height: 2.6rem;
        }}
        .stButton>button[kind="primary"] {{
            background: {GREEN};
            border-color: {GREEN};
        }}
        /* Bigger touch targets on mobile */
        @media (max-width: 640px) {{
            .stButton>button {{ width: 100%; font-size: 1rem; }}
            .block-container {{ padding-left: 0.8rem; padding-right: 0.8rem; }}
        }}
        [data-testid="stMetricValue"] {{ color: {BLACK}; }}
        hr {{ border-color: #e5e5e5; }}
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
