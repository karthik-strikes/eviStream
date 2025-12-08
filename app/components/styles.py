"""
Shared CSS styles for eviStream application
"""

import streamlit as st


def apply_global_styles():
    """Apply global CSS styles for the application."""
    st.markdown(
        """
<style>
    :root {
        --penn-blue: #011F5B;
        --penn-red: #990000;
        --penn-light-blue: #82AFD3;
        --bg-main: #f5f7fb;
        --bg-card: #ffffff;
        --text-main: #111827;
        --text-muted: #6b7280;
        --border-soft: #e5e7eb;
        --shadow-soft: 0 12px 30px rgba(15, 23, 42, 0.08);
        --radius-lg: 14px;
    }

    /* Hide default Streamlit chrome */
    #MainMenu, footer {visibility: hidden;}

    .block-container {
        padding-top: 2.6rem;   /* extra top padding so hero corners are fully visible */
        padding-bottom: 3rem;
        max-width: 1200px;
    }

    body {
        background: radial-gradient(circle at top left, #f9fafb, #eef2ff);
    }

    /* Top hero area */
    .evi-hero {
        background: linear-gradient(135deg, var(--penn-blue), #023a87);
        color: #f9fafb;
        border-radius: 20px;
        padding: 1.4rem 1.7rem;
        box-shadow: 0 20px 45px rgba(15, 23, 42, 0.18);
        border: 1px solid rgba(15, 23, 42, 0.35);
        margin-top: 0.2rem;    /* rely on extra block-container padding instead */
        margin-bottom: 2rem;
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 1.5rem;
    }
    .evi-hero-left h1 {
        font-size: 1.7rem;
        margin-bottom: 0.3rem;
        letter-spacing: -0.03em;
    }
    .evi-hero-left p {
        margin: 0;
        font-size: 0.92rem;
        color: rgba(249, 250, 251, 0.9);
    }
    .evi-hero-badge {
        display: inline-flex;
        align-items: center;
        gap: 0.35rem;
        background: rgba(15, 23, 42, 0.25);
        padding: 0.25rem 0.6rem;
        border-radius: 999px;
        font-size: 0.74rem;
        margin-bottom: 0.5rem;
    }
    .evi-hero-badge span {
        font-weight: 600;
    }

    .evi-hero-steps {
        display: flex;
        gap: 0.6rem;
        font-size: 0.78rem;
    }
    .evi-step-pill {
        border-radius: 999px;
        padding: 0.35rem 0.7rem;
        background: rgba(15, 23, 42, 0.12);
        display: flex;
        align-items: center;
        gap: 0.35rem;
        white-space: nowrap;
    }
    .evi-step-pill-active {
        background: #f97316;
        color: #111827;
        font-weight: 600;
    }

    /* Generic cards */
    .evi-card {
        background: var(--bg-card);
        border-radius: var(--radius-lg);
        padding: 1.3rem 1.4rem;
        box-shadow: var(--shadow-soft);
        border: 1px solid rgba(148, 163, 184, 0.24);
        margin-bottom: 1.2rem;
    }

    /* Project header card – make it stand out a bit more */
    .evi-project-card {
        margin-top: 1.0rem;
        margin-bottom: 1.6rem;
        box-shadow: 0 18px 40px rgba(15, 23, 42, 0.12);
    }

    .evi-card-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        gap: 0.75rem;
        margin-bottom: 0.8rem;
    }

    .evi-card-title {
        font-size: 1.02rem;
        font-weight: 600;
        color: var(--text-main);
    }

    .evi-card-subtitle {
        font-size: 0.85rem;
        color: var(--text-muted);
        margin-top: 0.1rem;
    }

    .evi-chip {
        display: inline-flex;
        align-items: center;
        padding: 0.25rem 0.55rem;
        border-radius: 999px;
        background: rgba(148, 163, 184, 0.16);
        font-size: 0.76rem;
        color: #374151;
        gap: 0.3rem;
    }

    .evi-chip-dot {
        width: 7px;
        height: 7px;
        border-radius: 999px;
        background: var(--penn-red);
    }

    /* Welcome cards on empty state */
    .evi-welcome-grid {
        display: grid;
        grid-template-columns: repeat(3, minmax(0, 1fr));
        gap: 1rem;
        margin-top: 0.5rem;
    }
    .evi-welcome-card {
        background: var(--bg-card);
        border-radius: var(--radius-lg);
        padding: 1.3rem 1.2rem;
        text-align: left;
        box-shadow: var(--shadow-soft);
        border: 1px dashed rgba(148, 163, 184, 0.4);
    }
    .evi-welcome-step {
        width: 28px;
        height: 28px;
        border-radius: 999px;
        background: var(--penn-red);
        color: #f9fafb;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 0.8rem;
        font-weight: 600;
        margin-bottom: 0.5rem;
    }
    .evi-welcome-card h3 {
        font-size: 0.98rem;
        margin-bottom: 0.15rem;
        color: var(--text-main);
    }
    .evi-welcome-card p {
        font-size: 0.82rem;
        margin: 0;
        color: var(--text-muted);
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background: #020617;
        border-right: 1px solid #1f2933;
    }
    [data-testid="stSidebar"] * {
        color: #e5e7eb !important;
    }
    /* Sidebar selectbox – stronger contrast */
    [data-testid="stSidebar"] .stSelectbox div[data-baseweb="select"] > div {
        background-color: #020617 !important;
        border-radius: 999px !important;
        border: 1px solid #4b5563 !important;
    }
    [data-testid="stSidebar"] .stSelectbox div[data-baseweb="select"] * {
        color: #f9fafb !important;
        opacity: 1 !important;
    }
    .evi-sidebar-header {
        font-size: 0.95rem;
        font-weight: 600;
        margin-bottom: 0.25rem;
    }
    .evi-sidebar-blurb {
        font-size: 0.78rem;
        color: #9ca3af;
        margin-bottom: 0.7rem;
    }
    .evi-sidebar-divider {
        border-top: 1px solid #374151;
        margin: 0.7rem 0 0.8rem 0;
    }
    .evi-sidebar-metrics {
        display: grid;
        grid-template-columns: repeat(2, minmax(0,1fr));
        gap: 0.55rem;
        margin-top: 0.6rem;
    }
    .evi-sidebar-metric-card {
        background: #020617;
        border-radius: 0.7rem;
        border: 1px solid #1f2937;
        padding: 0.45rem 0.55rem;
        font-size: 0.75rem;
    }
    .evi-sidebar-metric-label {
        color: #9ca3af;
        margin-bottom: 0.1rem;
    }
    .evi-sidebar-metric-value {
        font-weight: 600;
        font-size: 0.95rem;
        color: #e5e7eb;
    }

    /* Form field "pills" */
    .evi-field-pill {
        border-radius: 0.55rem;
        border: 1px solid var(--border-soft);
        padding: 0.55rem 0.65rem;
        margin-bottom: 0.4rem;
        display: flex;
        justify-content: space-between;
        align-items: center;
        gap: 0.6rem;
        background: #f9fafb;
    }
    .evi-field-pill-main {
        font-size: 0.82rem;
    }
    .evi-field-pill-main span {
        font-weight: 600;
        color: var(--text-main);
    }
    .evi-field-pill-desc {
        font-size: 0.78rem;
        color: var(--text-muted);
    }
    .evi-field-pill-type {
        font-size: 0.78rem;
        padding: 0.18rem 0.45rem;
        border-radius: 999px;
        background: #e0ecff;
        color: #1e3a8a;
        white-space: nowrap;
    }

    /* File uploader tweak */
    [data-testid="stFileUploader"] > div {
        padding: 0.6rem 0.8rem;
        border-radius: 0.8rem;
        border: 1px dashed var(--border-soft);
        background: rgba(248, 250, 252, 0.9);
    }

    /* Expander headers */
    .streamlit-expanderHeader {
        font-size: 0.88rem !important;
        font-weight: 500 !important;
        color: var(--text-main) !important;
    }

    /* Buttons */
    .stButton button {
        border-radius: 999px !important;
        padding: 0.32rem 0.9rem !important;
        font-size: 0.86rem !important;
        font-weight: 500 !important;
        border: none !important;
        box-shadow: 0 3px 8px rgba(15, 23, 42, 0.16) !important;
        white-space: nowrap !important;
    }
    .stButton button:hover {
        transform: translateY(-1px) !important;
    }

    /* PDF container */
    .pdf-container iframe {
        border-radius: 12px;
        border: 1px solid var(--border-soft);
        box-shadow: var(--shadow-soft);
    }

</style>
""",
        unsafe_allow_html=True,
    )
