import html
import re
import uuid
from io import BytesIO
from pathlib import Path

from dotenv import load_dotenv
from fpdf import FPDF
import streamlit as st

load_dotenv(Path(__file__).resolve().parent / ".env")

from agent import graph

# ─────────────────────────────────────────────────────────────
# Page config
# ─────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="TripPlanner AI | LangGraph Agent",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────────
# Custom CSS
# ─────────────────────────────────────────────────────────────

st.markdown(
    """
<style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:ital,opsz,wght@0,9..40,400;0,9..40,500;0,9..40,600;0,9..40,700;1,9..40,400&display=swap');

    html, body, [class*="css"] {
        font-family: 'DM Sans', sans-serif;
    }

    .stApp {
        background: #000000;
        color: #f1f5f9;
    }

    section.main .block-container {
        padding-top: 1.5rem;
        max-width: 1100px;
        color: #f1f5f9;
    }

    section.main h1, section.main h2, section.main h3, section.main h4,
    section.main p, section.main label, section.main .stMarkdown,
    section.main [data-testid="stCaptionContainer"] {
        color: #f1f5f9 !important;
    }

    section.main .stExpander details summary {
        color: #f1f5f9 !important;
    }

    .main-header {
        background: linear-gradient(135deg, #0f766e 0%, #0e7490 45%, #1e40af 100%);
        padding: 2.5rem 2.75rem;
        border-radius: 20px;
        color: white;
        margin-bottom: 1.75rem;
        box-shadow: 0 20px 50px rgba(15, 118, 110, 0.22);
        position: relative;
        overflow: hidden;
    }

    .main-header::after {
        content: "";
        position: absolute;
        top: -40%;
        right: -10%;
        width: 280px;
        height: 280px;
        background: radial-gradient(circle, rgba(255,255,255,0.12) 0%, transparent 70%);
        border-radius: 50%;
    }

    .main-header h1 {
        font-size: 2.35rem;
        font-weight: 700;
        margin: 0 0 0.5rem 0;
        color: white !important;
        letter-spacing: -0.02em;
    }

    .main-header p {
        font-size: 1.05rem;
        opacity: 0.94;
        margin: 0;
        max-width: 680px;
        line-height: 1.6;
    }

    .badge-row {
        display: flex;
        flex-wrap: wrap;
        gap: 0.55rem;
        margin-top: 1.25rem;
    }

    .badge {
        background: rgba(255,255,255,0.14);
        border: 1px solid rgba(255,255,255,0.28);
        border-radius: 999px;
        padding: 0.3rem 0.85rem;
        font-size: 0.78rem;
        font-weight: 600;
        letter-spacing: 0.02em;
        transition: background 0.2s ease;
    }

    .badge:hover {
        background: rgba(255,255,255,0.22);
    }

    .panel {
        background: linear-gradient(145deg, rgba(18,18,18,0.96) 0%, rgba(28,28,28,0.92) 100%);
        backdrop-filter: blur(14px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 18px;
        padding: 1.5rem 1.65rem;
        margin-bottom: 1.25rem;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.35);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }

    .panel:hover {
        transform: translateY(-2px);
        box-shadow: 0 14px 36px rgba(0, 0, 0, 0.45);
    }

    .panel-accent {
        border-top: 3px solid transparent;
        border-image: linear-gradient(90deg, #0f766e, #1e40af) 1;
    }

    .panel-features {
        background: linear-gradient(135deg, rgba(10,30,20,0.85) 0%, rgba(15,20,35,0.9) 100%);
        border: 1px solid rgba(16, 185, 129, 0.25);
    }

    .panel h3, .panel h4 {
        color: #ffffff !important;
        margin: 0 0 0.85rem 0;
        font-weight: 700;
        letter-spacing: -0.01em;
    }

    .panel p, .panel li, .panel span {
        color: #e2e8f0 !important;
        line-height: 1.75;
    }

    .feature-grid {
        display: grid;
        grid-template-columns: repeat(2, 1fr);
        gap: 0.65rem;
        margin-top: 0.5rem;
    }

    .feature-chip {
        background: linear-gradient(135deg, rgba(22,163,74,0.08) 0%, rgba(30,64,175,0.06) 100%);
        border: 1px solid rgba(22,163,74,0.22);
        border-radius: 10px;
        padding: 0.55rem 0.85rem;
        color: #15803d;
        font-weight: 600;
        font-size: 0.88rem;
        transition: background 0.2s ease;
    }

    .feature-chip:hover {
        background: linear-gradient(135deg, rgba(22,163,74,0.14) 0%, rgba(30,64,175,0.1) 100%);
    }

    .workflow-card {
        background: linear-gradient(135deg, rgba(15,118,110,0.15) 0%, rgba(30,64,175,0.12) 100%);
        border-radius: 12px;
        padding: 1rem 1.15rem;
        margin-bottom: 0.65rem;
        border-left: 3px solid #0f766e;
        color: #e2e8f0;
    }

    .workflow-card strong { color: #ffffff; }

    .step-flow {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(130px, 1fr));
        gap: 0.5rem;
        margin: 0.75rem 0;
    }

    .step-flow-item {
        background: linear-gradient(180deg, rgba(40,40,40,0.9) 0%, rgba(25,25,25,0.8) 100%);
        border-radius: 10px;
        padding: 0.65rem 0.5rem;
        text-align: center;
        font-size: 0.78rem;
        font-weight: 600;
        color: #f1f5f9;
        border: 1px solid rgba(255,255,255,0.12);
    }

    .form-panel {
        background: linear-gradient(160deg, rgba(18,18,18,0.96) 0%, rgba(28,28,28,0.92) 100%);
        backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 18px;
        padding: 1.65rem;
        box-shadow: 0 12px 32px rgba(0, 0, 0, 0.35);
    }

    .live-panel {
        background: linear-gradient(145deg, #0f172a 0%, #1e293b 55%, #0f2744 100%);
        border-radius: 18px;
        padding: 1.5rem;
        color: #e2e8f0;
        box-shadow: 0 16px 40px rgba(15, 23, 42, 0.18);
        position: sticky;
        top: 1rem;
    }

    .live-panel h4 {
        color: #f8fafc;
        margin: 0 0 1rem 0;
        font-size: 1rem;
        font-weight: 700;
        border-bottom: 1px solid rgba(148,163,184,0.25);
        padding-bottom: 0.65rem;
    }

    .live-stat {
        display: flex;
        justify-content: space-between;
        padding: 0.55rem 0;
        border-bottom: 1px solid rgba(148,163,184,0.15);
        font-size: 0.9rem;
    }

    .live-stat .label { color: #94a3b8; }
    .live-stat .value { color: #f1f5f9; font-weight: 600; }

    .preset-chip {
        background: linear-gradient(135deg, rgba(15,118,110,0.06) 0%, rgba(30,64,175,0.06) 100%);
        border: 1px dashed rgba(15,118,110,0.35);
        border-radius: 10px;
        padding: 0.5rem 0.75rem;
        font-size: 0.82rem;
        color: #334155;
        margin-bottom: 0.5rem;
    }

    .step-item {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        padding: 0.7rem 0.9rem;
        border-radius: 12px;
        margin-bottom: 0.45rem;
        background: linear-gradient(90deg, rgba(35,35,35,0.9) 0%, rgba(25,25,25,0.8) 100%);
        border: 1px solid rgba(255,255,255,0.1);
        font-size: 0.86rem;
        color: #cbd5e1;
        transition: all 0.25s ease;
    }

    .step-item.active {
        background: linear-gradient(90deg, rgba(16,185,129,0.2) 0%, rgba(14,165,233,0.12) 100%);
        border-color: rgba(16,185,129,0.45);
        color: #6ee7b7;
        font-weight: 600;
        box-shadow: 0 4px 14px rgba(16,185,129,0.15);
    }

    .step-item.done {
        background: linear-gradient(90deg, rgba(34,197,94,0.18) 0%, rgba(16,185,129,0.1) 100%);
        border-color: rgba(34,197,94,0.4);
        color: #86efac;
    }

    .step-icon {
        width: 30px;
        height: 30px;
        border-radius: 8px;
        display: flex;
        align-items: center;
        justify-content: center;
        background: linear-gradient(135deg, #cbd5e1, #94a3b8);
        font-size: 0.8rem;
        font-weight: 700;
        color: white;
        flex-shrink: 0;
    }

    .step-item.active .step-icon {
        background: linear-gradient(135deg, #0f766e, #1e40af);
    }

    .step-item.done .step-icon {
        background: linear-gradient(135deg, #16a34a, #0d9488);
    }

    .day-card {
        background: linear-gradient(145deg, rgba(22,22,22,0.95) 0%, rgba(32,32,32,0.9) 100%);
        border: 1px solid rgba(255,255,255,0.1);
        border-left: 4px solid #0f766e;
        border-radius: 14px;
        padding: 1.25rem 1.5rem;
        margin-bottom: 1rem;
        box-shadow: 0 6px 20px rgba(0, 0, 0, 0.3);
        transition: box-shadow 0.2s ease;
    }

    .day-card:hover {
        box-shadow: 0 10px 28px rgba(0, 0, 0, 0.4);
    }

    .day-card h3 {
        color: #ffffff;
        margin: 0 0 0.75rem 0;
        font-size: 1.1rem;
        font-weight: 700;
    }

    .day-card .time-heading {
        margin: 0.85rem 0 0.25rem 0;
        font-weight: 700;
        color: #ffffff;
        font-size: 0.95rem;
    }

    .day-card ul, .day-card li, .day-card p, .day-card strong {
        color: #e2e8f0;
        line-height: 1.75;
    }

    .day-card ul { margin: 0.25rem 0 0.75rem 0; padding-left: 1.25rem; }
    .day-card li { margin-bottom: 0.35rem; }
    .day-card p { margin: 0.35rem 0; }

    .full-output-doc {
        background: linear-gradient(145deg, rgba(18,18,18,0.96) 0%, rgba(28,28,28,0.92) 100%);
        border: 1px solid rgba(255,255,255,0.1);
        border-radius: 16px;
        padding: 2rem 2.25rem;
        box-shadow: 0 8px 28px rgba(0, 0, 0, 0.35);
    }

    .full-output-doc .doc-title {
        font-size: 1.75rem;
        font-weight: 700;
        color: #ffffff;
        margin: 0 0 0.35rem 0;
        border-bottom: 2px solid transparent;
        border-image: linear-gradient(90deg, #0f766e, #1e40af) 1;
        padding-bottom: 0.75rem;
    }

    .full-output-doc .doc-subtitle {
        color: #cbd5e1;
        font-size: 0.95rem;
        margin: 0 0 1.5rem 0;
    }

    .section-heading {
        font-size: 1.15rem;
        font-weight: 700;
        color: #ffffff;
        margin: 1.75rem 0 1rem 0;
        padding-bottom: 0.4rem;
        border-bottom: 2px solid transparent;
        border-image: linear-gradient(90deg, #0f766e, transparent) 1;
    }

    .research-snippet {
        background: linear-gradient(90deg, rgba(30,30,30,0.95) 0%, rgba(22,22,22,0.9) 100%);
        border-left: 3px solid #0f766e;
        border-radius: 0 10px 10px 0;
        padding: 0.9rem 1.1rem;
        margin-bottom: 0.65rem;
        color: #e2e8f0;
        line-height: 1.65;
        font-size: 0.92rem;
    }

    .result-metric {
        background: linear-gradient(145deg, rgba(22,22,22,0.95) 0%, rgba(32,32,32,0.9) 100%);
        border: 1px solid rgba(255,255,255,0.1);
        border-radius: 14px;
        padding: 1rem 1.15rem;
        text-align: center;
        box-shadow: 0 6px 18px rgba(0,0,0,0.3);
    }

    .result-metric .m-label {
        font-size: 0.72rem;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        color: #94a3b8;
        font-weight: 600;
        margin-bottom: 0.35rem;
    }

    .result-metric .m-value {
        font-size: 1.15rem;
        font-weight: 700;
        color: #ffffff;
    }

    .pipeline-header {
        font-size: 0.95rem;
        font-weight: 700;
        color: #ffffff;
        margin-bottom: 0.75rem;
        padding-bottom: 0.5rem;
        border-bottom: 1px solid rgba(255,255,255,0.12);
    }

    div[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f172a 0%, #1a2744 50%, #1e293b 100%);
    }

    div[data-testid="stSidebar"] * { color: #e2e8f0 !important; }

    div[data-testid="stSidebar"] .stButton > button {
        background: rgba(255,255,255,0.06) !important;
        border: 1px solid rgba(255,255,255,0.14) !important;
        color: #f1f5f9 !important;
        border-radius: 10px !important;
        width: 100%;
        font-weight: 600 !important;
        transition: all 0.2s ease !important;
    }

    div[data-testid="stSidebar"] .stButton > button:hover {
        background: rgba(255,255,255,0.12) !important;
        border-color: rgba(255,255,255,0.28) !important;
    }

    div[data-testid="stSidebar"] .nav-active button {
        background: linear-gradient(135deg, rgba(15,118,110,0.5) 0%, rgba(30,64,175,0.4) 100%) !important;
        border-color: rgba(94,234,212,0.35) !important;
    }

    .stButton > button[kind="primary"],
    .stFormSubmitButton button,
    div[data-testid="stDownloadButton"] > button {
        background: linear-gradient(135deg, #0f766e 0%, #0e7490 45%, #1e40af 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 0.6rem 1.5rem !important;
        font-weight: 600 !important;
        box-shadow: 0 6px 20px rgba(15, 118, 110, 0.3) !important;
        transition: all 0.2s ease !important;
    }

    .stButton > button[kind="primary"]:hover,
    .stFormSubmitButton button:hover,
    div[data-testid="stDownloadButton"] > button:hover {
        box-shadow: 0 10px 28px rgba(15, 118, 110, 0.4) !important;
        transform: translateY(-1px);
    }

    .stButton > button[kind="secondary"] {
        background: linear-gradient(145deg, rgba(255,255,255,0.9) 0%, rgba(241,245,249,0.95) 100%) !important;
        border: 1px solid rgba(15,118,110,0.3) !important;
        color: #0f766e !important;
        border-radius: 10px !important;
        font-weight: 600 !important;
    }

    div[data-testid="stTabs"] button[data-baseweb="tab"] {
        font-weight: 600;
        border-radius: 8px 8px 0 0;
    }

    div[data-testid="stTabs"] button[aria-selected="true"] {
        background: linear-gradient(180deg, rgba(15,118,110,0.08) 0%, transparent 100%);
        color: #0f766e !important;
        border-bottom: 2px solid #0f766e !important;
    }

    .stTextInput input, .stNumberInput input {
        background: #141414 !important;
        color: #ffffff !important;
        border-radius: 10px !important;
        border-color: rgba(255,255,255,0.18) !important;
    }

    .stTextInput input:focus, .stNumberInput input:focus {
        border-color: #0f766e !important;
        box-shadow: 0 0 0 2px rgba(15,118,110,0.25) !important;
    }

    div[data-testid="stTabs"] [data-baseweb="tab-panel"] {
        color: #f1f5f9;
    }

    div[data-testid="stTabs"] button[aria-selected="true"] {
        color: #6ee7b7 !important;
    }

    .stRadio label, .stRadio label span {
        color: #f1f5f9 !important;
    }
</style>
""",
    unsafe_allow_html=True,
)

# ─────────────────────────────────────────────────────────────
# Constants
# ─────────────────────────────────────────────────────────────

PIPELINE_STEPS = [
    ("collect_preferences", "Collect Preferences"),
    ("research_attractions", "Attractions Search (Parallel)"),
    ("research_food", "Food Search (Parallel)"),
    ("research_transport", "Transport Search (Parallel)"),
    ("merge_research", "Merge Research Results"),
    ("generate_itinerary", "Generate Itinerary"),
    ("review_itinerary", "Quality Review"),
    ("improve_itinerary", "Improve & Retry"),
]

TRAVEL_STYLES = ["Budget", "Luxury", "Adventure", "Family", "Solo"]

DEMO_PRESETS = {
    "Skardu Adventure": {
        "destination": "Skardu",
        "days": 5,
        "budget": 120000,
        "travel_style": "Adventure",
    },
    "Murree Family Trip": {
        "destination": "Murree",
        "days": 2,
        "budget": 35000,
        "travel_style": "Family",
    },
    "Hunza Luxury Escape": {
        "destination": "Hunza",
        "days": 4,
        "budget": 200000,
        "travel_style": "Luxury",
    },
}

STYLE_DESCRIPTIONS = {
    "Budget": "Hostels, local food, public transport",
    "Luxury": "Premium stays, fine dining, private tours",
    "Adventure": "Trekking, outdoor activities, exploration",
    "Family": "Kid-friendly spots, relaxed pace, comfort",
    "Solo": "Flexible schedule, social & safe experiences",
}

LANGGRAPH_FEATURES = [
    "TypedDict State",
    "8 Agent Nodes",
    "Parallel Research",
    "Conditional Edges",
    "Iterative Retry Loop",
    "3 Web Search Tools",
    "MemorySaver",
    "Structured Output",
]

# ─────────────────────────────────────────────────────────────
# Session state
# ─────────────────────────────────────────────────────────────

if "thread_id" not in st.session_state:
    st.session_state.thread_id = f"user_{uuid.uuid4().hex[:8]}"

if "result" not in st.session_state:
    st.session_state.result = None

if "form_defaults" not in st.session_state:
    st.session_state.form_defaults = {
        "destination": "",
        "days": 3,
        "budget": 50000,
        "travel_style": "Budget",
    }

if "page" not in st.session_state:
    st.session_state.page = "home"

# ─────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────


def format_pkr(amount: int) -> str:
    return f"PKR {amount:,}"


DAY_SPLIT_PATTERN = re.compile(
    r"(?=(?:\*\*|#{1,3}\s*)?Day\s+\d+)",
    re.IGNORECASE,
)

SECTION_KEYWORDS = re.compile(
    r"^(Morning|Afternoon|Evening|Night|Breakfast|Lunch|Dinner|"
    r"Activity|Activities|Accommodation|Stay|Transport|Tips|Overview)$",
    re.IGNORECASE,
)

INLINE_HEADING_PATTERN = re.compile(
    r"^(?:\*\*|__)?(.+?)(?:\*\*|__)?\s*:\s*(.+)$"
)

BULLET_PATTERN = re.compile(r"^[\s]*(?:[-*•]|\d+\.)\s+", re.MULTILINE)


def clean_text(text: str) -> str:
    text = text.replace("\r\n", "\n").strip()
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text


def format_inline(text: str) -> str:
    escaped = html.escape(text)
    return re.sub(
        r"\*\*(.+?)\*\*",
        lambda m: f"<strong>{m.group(1)}</strong>",
        escaped,
    )


def parse_itinerary_days(itinerary: str) -> list[tuple[str, str]]:
    itinerary = clean_text(itinerary)
    if not itinerary:
        return []

    chunks = DAY_SPLIT_PATTERN.split(itinerary)
    chunks = [c.strip() for c in chunks if c.strip()]

    days: list[tuple[str, str]] = []
    for chunk in chunks:
        match = re.match(
            r"^(?:\*\*|#{1,3}\s*)?(Day\s+\d+[^:\n]*(?::[^\n]*)?)\*?\*?\s*\n?(.*)",
            chunk,
            re.IGNORECASE | re.DOTALL,
        )
        if match:
            title = re.sub(r"\*+|#+\s*", "", match.group(1)).strip()
            content = match.group(2).strip()
            if not content and ":" in title:
                name, rest = title.split(":", 1)
                if rest.strip():
                    title = name.strip()
                    content = rest.strip()
            days.append((title, content))
        elif not days:
            days.append(("Overview", chunk))
        else:
            prev_title, prev_content = days[-1]
            days[-1] = (prev_title, f"{prev_content}\n\n{chunk}")

    if not days:
        days.append(("Full Itinerary", itinerary))

    return days


def render_day_body_html(content: str) -> str:
    content = clean_text(content)
    if not content:
        return ""

    lines = content.split("\n")
    html_parts: list[str] = []
    in_list = False

    for line in lines:
        stripped = line.strip()
        if not stripped:
            if in_list:
                html_parts.append("</ul>")
                in_list = False
            continue

        inline_match = INLINE_HEADING_PATTERN.match(stripped)
        if inline_match:
            if in_list:
                html_parts.append("</ul>")
                in_list = False
            heading = inline_match.group(1).strip()
            desc = inline_match.group(2).strip()
            html_parts.append(
                f"<p><strong>{format_inline(heading)}:</strong> {format_inline(desc)}</p>"
            )
            continue

        plain_heading = re.sub(r"\*+|#+\s*", "", stripped).strip()
        if SECTION_KEYWORDS.match(plain_heading):
            if in_list:
                html_parts.append("</ul>")
                in_list = False
            html_parts.append(
                f'<p class="time-heading"><strong>{html.escape(plain_heading)}</strong></p>'
            )
            continue

        if BULLET_PATTERN.match(stripped):
            if not in_list:
                html_parts.append("<ul>")
                in_list = True
            item = BULLET_PATTERN.sub("", stripped).strip()
            html_parts.append(f"<li>{format_inline(item)}</li>")
            continue

        if in_list:
            html_parts.append("</ul>")
            in_list = False

        html_parts.append(f"<p>{format_inline(stripped)}</p>")

    if in_list:
        html_parts.append("</ul>")

    return "".join(html_parts)


def get_display_days(itinerary: str) -> list[tuple[str, str]]:
    days = parse_itinerary_days(itinerary)
    valid_days = [(title, content) for title, content in days if content.strip()]
    if valid_days:
        return valid_days
    cleaned = clean_text(itinerary)
    return [("Trip Itinerary", cleaned)] if cleaned else []


def render_day_card(title: str, content: str) -> None:
    body = render_day_body_html(content)
    if not body:
        return
    st.markdown(
        f'<div class="day-card"><h3>{html.escape(title)}</h3>{body}</div>',
        unsafe_allow_html=True,
    )


def parse_research_sections(research: str) -> list[tuple[str, str]]:
    research = clean_text(research)
    if not research:
        return []

    sections = re.split(
        r"(?=\[(?:ATTRACTIONS|FOOD & DINING|TRANSPORT & LOGISTICS)\])",
        research,
    )
    parsed: list[tuple[str, str]] = []
    for section in sections:
        section = section.strip()
        if not section:
            continue
        header_match = re.match(r"^\[([^\]]+)\]\s*\n?(.*)", section, re.DOTALL)
        if header_match:
            parsed.append((header_match.group(1).strip(), header_match.group(2).strip()))
        else:
            parsed.append(("Research", section))

    if parsed:
        return parsed

    snippets = [s.strip() for s in re.split(r"\n{2,}", research) if s.strip()]
    return [(f"Source {i}", s) for i, s in enumerate(snippets, 1)]


def parse_research_snippets(research: str) -> list[str]:
    return [content for _, content in parse_research_sections(research)]


def build_download_document(result: dict) -> str:
    destination = result.get("destination", "Trip")
    days_count = result.get("days", "—")
    budget = result.get("budget", 0)
    style = result.get("travel_style", "—")
    score = result.get("review_score", 0)
    approved = result.get("approved", False)
    itinerary = result.get("itinerary", "")
    research = result.get("research", "")

    lines = [
        "=" * 60,
        f"  TRIP PLAN — {destination.upper()}",
        "=" * 60,
        "",
        "TRIP SUMMARY",
        "-" * 40,
        f"  Destination   : {destination}",
        f"  Duration      : {days_count} days",
        f"  Budget        : {format_pkr(budget)}",
        f"  Travel Style  : {style}",
        f"  Review Score  : {score} / 10",
        f"  Status        : {'Approved' if approved else 'Improved by agent'}",
        "",
        "ITINERARY",
        "-" * 40,
        "",
    ]

    for title, content in get_display_days(itinerary):
        lines.append(title.upper())
        lines.append("")
        lines.append(clean_text(content))
        lines.append("")
        lines.append("-" * 40)
        lines.append("")

    if research:
        lines.extend([
            "RESEARCH NOTES",
            "-" * 40,
            "",
            clean_text(research),
            "",
        ])

    lines.append("Generated by TripPlanner AI — LangGraph Agent")
    return "\n".join(lines)


def _pdf_safe(text: str) -> str:
    if not text:
        return ""
    cleaned = text.replace("\u2014", "-").replace("\u2013", "-")
    return cleaned.encode("latin-1", errors="replace").decode("latin-1")


def _pdf_break_long_tokens(text: str, chunk_size: int = 70) -> str:
    parts = []
    for token in text.split(" "):
        if len(token) <= chunk_size:
            parts.append(token)
        else:
            parts.extend(token[i : i + chunk_size] for i in range(0, len(token), chunk_size))
    return " ".join(parts)


def _pdf_write_block(
    pdf: FPDF,
    text: str,
    *,
    font_size: int = 11,
    bold: bool = False,
    line_height: float = 6,
) -> None:
    safe = _pdf_break_long_tokens(_pdf_safe(text))
    if not safe.strip():
        return

    pdf.set_x(pdf.l_margin)
    pdf.set_font("Helvetica", "B" if bold else "", font_size)
    pdf.multi_cell(pdf.epw, line_height, safe)


def build_download_pdf(result: dict) -> bytes:
    destination = result.get("destination", "Trip")
    days_count = result.get("days", "-")
    budget = result.get("budget", 0)
    style = result.get("travel_style", "-")
    score = result.get("review_score", 0)
    approved = result.get("approved", False)
    itinerary = result.get("itinerary", "")
    research = result.get("research", "")

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_margins(15, 15, 15)
    pdf.add_page()

    _pdf_write_block(pdf, f"TRIP PLAN - {destination.upper()}", font_size=18, bold=True, line_height=10)
    pdf.ln(4)

    _pdf_write_block(pdf, "Trip Summary", font_size=12, bold=True, line_height=8)
    summary_lines = [
        f"Destination: {destination}",
        f"Duration: {days_count} days",
        f"Budget: {format_pkr(budget)}",
        f"Travel Style: {style}",
        f"Review Score: {score} / 10",
        f"Status: {'Approved' if approved else 'Improved by agent'}",
    ]
    for line in summary_lines:
        _pdf_write_block(pdf, line)
    pdf.ln(4)

    _pdf_write_block(pdf, "Day-by-Day Itinerary", font_size=12, bold=True, line_height=8)
    for title, content in get_display_days(itinerary):
        _pdf_write_block(pdf, title, bold=True)
        _pdf_write_block(pdf, clean_text(content))
        pdf.ln(2)

    if research:
        _pdf_write_block(pdf, "Research Summary", font_size=12, bold=True, line_height=8)
        for heading, content in parse_research_sections(research):
            _pdf_write_block(pdf, heading, font_size=10, bold=True)
            _pdf_write_block(pdf, clean_text(content), font_size=10)
            pdf.ln(2)

    pdf.ln(4)
    _pdf_write_block(
        pdf,
        "Generated by TripPlanner AI - LangGraph Agent",
        font_size=9,
        line_height=6,
    )

    buffer = BytesIO()
    pdf.output(buffer)
    return buffer.getvalue()


def render_full_output(result: dict) -> None:
    destination = result.get("destination", "Your Trip")
    days_count = result.get("days", "—")
    budget = result.get("budget", 0)
    style = result.get("travel_style", "—")
    itinerary = result.get("itinerary", "")
    research = result.get("research", "")

    st.markdown(
        f"""
<div class="full-output-doc">
    <div class="doc-title">{html.escape(destination)} — Trip Plan</div>
    <div class="doc-subtitle">{days_count} days · {html.escape(str(style))} travel · {html.escape(format_pkr(budget))}</div>
</div>
""",
        unsafe_allow_html=True,
    )

    st.markdown('<div class="section-heading">Day-by-Day Itinerary</div>', unsafe_allow_html=True)
    for title, content in get_display_days(itinerary):
        render_day_card(title, content)

    if research:
        st.markdown('<div class="section-heading">Research Summary</div>', unsafe_allow_html=True)
        for heading, content in parse_research_sections(research):
            st.markdown(f"**{html.escape(heading)}**")
            for snippet in parse_research_snippets(content):
                st.markdown(
                    f'<div class="research-snippet">{html.escape(snippet)}</div>',
                    unsafe_allow_html=True,
                )


def render_pipeline_steps(completed: set[str], active: str | None = None):
    for i, (node_id, label) in enumerate(PIPELINE_STEPS, 1):
        if node_id in completed:
            css_class = "done"
        elif node_id == active:
            css_class = "active"
        else:
            css_class = ""
        st.markdown(
            f'<div class="step-item {css_class}">'
            f'<div class="step-icon">{i}</div>'
            f"<span>{label}</span></div>",
            unsafe_allow_html=True,
        )


def run_agent(destination, days, budget, travel_style):
    config = {"configurable": {"thread_id": st.session_state.thread_id}}
    initial_state = {
        "destination": destination,
        "days": days,
        "budget": budget,
        "travel_style": travel_style,
    }

    completed: set[str] = set()
    active_node = PIPELINE_STEPS[0][0]
    pipeline_placeholder = st.empty()

    with pipeline_placeholder.container():
        st.markdown('<div class="pipeline-header">Agent Pipeline</div>', unsafe_allow_html=True)
        render_pipeline_steps(completed, active_node)

    for event in graph.stream(initial_state, config, stream_mode="updates"):
        for node_name in event:
            completed.add(node_name)
            idx = next(
                (i for i, (n, _) in enumerate(PIPELINE_STEPS) if n == node_name),
                len(PIPELINE_STEPS) - 1,
            )
            active_node = (
                PIPELINE_STEPS[idx + 1][0] if idx + 1 < len(PIPELINE_STEPS) else None
            )

            with pipeline_placeholder.container():
                st.markdown('<div class="pipeline-header">Agent Pipeline</div>', unsafe_allow_html=True)
                render_pipeline_steps(completed, active_node)

    with pipeline_placeholder.container():
        st.markdown('<div class="pipeline-header">Agent Pipeline</div>', unsafe_allow_html=True)
        render_pipeline_steps(completed, None)

    snapshot = graph.get_state(config)
    return snapshot.values if snapshot else None


def render_live_preview(destination: str, days: int, budget: int, travel_style: str) -> None:
    per_day = budget // max(days, 1)
    dest_display = destination.strip() or "Not set"
    st.markdown(
        f"""
<div class="live-panel">
    <h4>Trip Preview</h4>
    <div class="live-stat"><span class="label">Destination</span><span class="value">{html.escape(dest_display)}</span></div>
    <div class="live-stat"><span class="label">Duration</span><span class="value">{days} days</span></div>
    <div class="live-stat"><span class="label">Total Budget</span><span class="value">{html.escape(format_pkr(budget))}</span></div>
    <div class="live-stat"><span class="label">Per Day</span><span class="value">{html.escape(format_pkr(per_day))}</span></div>
    <div class="live-stat"><span class="label">Travel Style</span><span class="value">{html.escape(travel_style)}</span></div>
    <div class="live-stat" style="border:none;"><span class="label">Style Note</span><span class="value" style="font-size:0.8rem;">{html.escape(STYLE_DESCRIPTIONS[travel_style])}</span></div>
</div>
""",
        unsafe_allow_html=True,
    )


def render_trip_results(result: dict) -> None:
    st.markdown('<div class="panel panel-accent">', unsafe_allow_html=True)
    st.markdown("## Your Trip Plan")

    score = result.get("review_score", 0)
    approved = result.get("approved", False)

    m1, m2, m3, m4 = st.columns(4)
    metrics = [
        ("Destination", str(result.get("destination", "-"))),
        ("Duration", f"{result.get('days', '-')} days"),
        ("Review Score", f"{score} / 10"),
        ("Status", "Approved" if approved else "Improved"),
    ]
    for col, (label, value) in zip([m1, m2, m3, m4], metrics):
        with col:
            st.markdown(
                f'<div class="result-metric"><div class="m-label">{html.escape(label)}</div>'
                f'<div class="m-value">{html.escape(value)}</div></div>',
                unsafe_allow_html=True,
            )

    st.progress(min(score / 10, 1.0), text=f"Quality score: {score}/10")
    st.markdown("</div>", unsafe_allow_html=True)

    if not approved:
        st.warning(
            "Initial itinerary scored below threshold — the agent ran the **improve loop** "
            "to refine your plan before delivery."
        )

    tab_itinerary, tab_research, tab_raw = st.tabs(
        ["Day-by-Day Itinerary", "Research Summary", "Complete Trip Document"]
    )

    with tab_itinerary:
        for title, content in get_display_days(result.get("itinerary", "")):
            render_day_card(title, content)

    with tab_research:
        research = result.get("research", "")
        if research:
            for heading, content in parse_research_sections(research):
                st.markdown(f"**{heading}**")
                for i, snippet in enumerate(parse_research_snippets(content), 1):
                    st.markdown(
                        f'<div class="research-snippet"><strong>Source {i}</strong><br><br>'
                        f"{html.escape(snippet)}</div>",
                        unsafe_allow_html=True,
                    )
        else:
            st.info("No research data available.")

    with tab_raw:
        render_full_output(result)

    st.download_button(
        label="Download Trip Plan (.pdf)",
        data=build_download_pdf(result),
        file_name=f"trip_{result.get('destination', 'plan').replace(' ', '_').lower()}.pdf",
        mime="application/pdf",
        use_container_width=True,
    )


def render_home_page() -> None:
    st.markdown(
        """
<div class="main-header">
    <h1>Welcome to AI Trip Planner Agent</h1>
    <p>Research destinations, build day-wise itineraries, review quality, and auto-improve — all powered by LangGraph.</p>
    <div class="badge-row">
        <span class="badge">LangGraph</span>
        <span class="badge">Gemini 2.5 Flash</span>
        <span class="badge">DuckDuckGo Search</span>
        <span class="badge">Parallel + Iterative</span>
    </div>
</div>
""",
        unsafe_allow_html=True,
    )

    col_left, col_right = st.columns(2, gap="large")

    with col_left:
        st.markdown('<div class="panel panel-accent">', unsafe_allow_html=True)
        st.markdown("### Workflow Types")
        st.markdown(
            """
<div class="workflow-card">
    <strong>Parallel</strong><br>
    3 web searches run simultaneously — attractions, food, and transport.
</div>
<div class="workflow-card">
    <strong>Iterative</strong><br>
    Generate, review, and improve until the plan passes quality check.
</div>
""",
            unsafe_allow_html=True,
        )
        st.markdown("</div>", unsafe_allow_html=True)

    with col_right:
        st.markdown('<div class="panel panel-accent">', unsafe_allow_html=True)
        st.markdown("### How It Works")
        st.markdown(
            """
<div class="step-flow">
    <div class="step-flow-item">Enter Preferences</div>
    <div class="step-flow-item">Parallel Search</div>
    <div class="step-flow-item">Merge Results</div>
    <div class="step-flow-item">Generate Plan</div>
    <div class="step-flow-item">Quality Review</div>
    <div class="step-flow-item">Auto Improve</div>
</div>
""",
            unsafe_allow_html=True,
        )
        with st.expander("View detailed steps", expanded=False):
            st.markdown(
                """
1. **Enter** your trip preferences  
2. **3 parallel web searches** — attractions, food, transport  
3. **Results merged** into one research summary  
4. **Gemini generates** a structured day-wise itinerary  
5. **Quality review** scores the plan (0–10)  
6. **Auto-improve** if score is below threshold  
"""
            )
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="panel panel-features">', unsafe_allow_html=True)
    st.markdown("### LangGraph Features")
    chips = "".join(
        f'<div class="feature-chip">{html.escape(f)}</div>' for f in LANGGRAPH_FEATURES
    )
    st.markdown(f'<div class="feature-grid">{chips}</div>', unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("Plan Your Trip — Click Here", type="primary", use_container_width=True):
        st.session_state.page = "plan"
        st.rerun()


def render_plan_page() -> None:
    st.markdown(
        """
<div class="panel panel-accent" style="margin-bottom:1.5rem;">
    <h3 style="margin:0 0 0.35rem 0;">Plan Your Trip</h3>
    <p style="margin:0;color:#cbd5e1;">Fill in your details below. The preview panel updates as you type.</p>
</div>
""",
        unsafe_allow_html=True,
    )

    st.markdown("**Quick Demo Presets**")
    preset_cols = st.columns(len(DEMO_PRESETS))
    for col, (name, preset) in zip(preset_cols, DEMO_PRESETS.items()):
        with col:
            if st.button(name, key=f"preset_{name}", use_container_width=True):
                st.session_state.form_defaults = preset.copy()
                st.rerun()

    defaults = st.session_state.form_defaults
    col_form, col_preview = st.columns([1.4, 1], gap="large")

    with col_form:
        st.markdown('<div class="form-panel">', unsafe_allow_html=True)
        destination = st.text_input(
            "Destination",
            value=defaults["destination"],
            placeholder="e.g. Skardu, Murree, Hunza, Swat",
            key="input_destination",
        )

        c1, c2 = st.columns(2)
        with c1:
            days = st.number_input(
                "Duration (days)",
                min_value=1,
                max_value=30,
                value=defaults["days"],
                key="input_days",
            )
        with c2:
            budget = st.number_input(
                "Budget (PKR)",
                min_value=1000,
                max_value=5000000,
                value=defaults["budget"],
                step=5000,
                key="input_budget",
            )

        st.markdown("**Travel Style**")
        travel_style = st.radio(
            "Travel Style",
            TRAVEL_STYLES,
            index=TRAVEL_STYLES.index(defaults["travel_style"]),
            horizontal=True,
            label_visibility="collapsed",
            key="input_style",
        )

        generate = st.button("Generate Trip Plan", type="primary", use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with col_preview:
        render_live_preview(destination, days, budget, travel_style)

    if generate:
        if not destination.strip():
            st.error("Please enter a destination to continue.")
        else:
            st.session_state.form_defaults = {
                "destination": destination,
                "days": days,
                "budget": budget,
                "travel_style": travel_style,
            }

            try:
                with st.status("Planning your trip...", expanded=True) as status:
                    st.write(f"**Destination:** {destination}")
                    st.write(
                        f"**Duration:** {days} days · **Budget:** {format_pkr(budget)} · "
                        f"**Style:** {travel_style}"
                    )
                    st.divider()

                    result = run_agent(destination, days, budget, travel_style)
                    st.session_state.result = result

                    status.update(label="Trip plan ready!", state="complete", expanded=False)

            except Exception as e:
                st.error(f"Something went wrong: {e}")
                st.info("Check that your GOOGLE_API_KEY is set in the `.env` file.")

    if st.session_state.result:
        render_trip_results(st.session_state.result)


# ─────────────────────────────────────────────────────────────
# Sidebar navigation
# ─────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown("### TripPlanner AI")
    st.markdown("*Powered by LangGraph + Gemini*")
    st.divider()

    st.markdown("**Navigation**")
    if st.button(
        "Home",
        use_container_width=True,
        type="primary" if st.session_state.page == "home" else "secondary",
    ):
        st.session_state.page = "home"
        st.rerun()
    if st.button(
        "Plan Your Trip",
        use_container_width=True,
        type="primary" if st.session_state.page == "plan" else "secondary",
    ):
        st.session_state.page = "plan"
        st.rerun()

    st.divider()
    st.markdown("**Session Memory**")
    st.caption("MemorySaver thread ID")
    st.code(st.session_state.thread_id, language=None)

    if st.button("New Session", use_container_width=True):
        st.session_state.thread_id = f"user_{uuid.uuid4().hex[:8]}"
        st.session_state.result = None
        st.rerun()

# ─────────────────────────────────────────────────────────────
# Main page router
# ─────────────────────────────────────────────────────────────

if st.session_state.page == "home":
    render_home_page()
else:
    render_plan_page()
