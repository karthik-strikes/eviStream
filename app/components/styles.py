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

    /* Modern hero area */
    .evi-hero-modern {
        background: linear-gradient(135deg, var(--penn-blue), #1e40af);
        color: #ffffff;
        border-radius: 16px;
        padding: 3rem 2.5rem;
        box-shadow: 0 10px 30px rgba(1, 31, 91, 0.3);
        margin-top: 0.5rem;
        margin-bottom: 2rem;
        position: relative;
    }
    .evi-hero-content {
        position: relative;
        z-index: 1;
    }
    .evi-hero-title {
        font-size: 2.8rem;
        margin: 1rem 0;
        letter-spacing: -0.01em;
        font-weight: 700;
        line-height: 1.2;
    }
    .highlight-text {
        color: #fbbf24;
    }
    .evi-hero-description {
        font-size: 1.05rem;
        line-height: 1.6;
        color: rgba(255, 255, 255, 0.9);
        margin-bottom: 2rem;
        max-width: 700px;
    }
    .evi-hero-badge {
        display: inline-block;
        background: rgba(255, 255, 255, 0.12);
        padding: 0.4rem 1rem;
        border-radius: 6px;
        font-size: 0.85rem;
        border: 1px solid rgba(255, 255, 255, 0.15);
        font-weight: 500;
        letter-spacing: 0.02em;
    }
    .evi-hero-stats {
        display: inline-flex;
        align-items: center;
        gap: 2rem;
        background: rgba(255, 255, 255, 0.08);
        padding: 1rem 2rem;
        border-radius: 12px;
        border: 1px solid rgba(255, 255, 255, 0.12);
        margin-top: 1.5rem;
    }
    .stat-item {
        text-align: center;
    }
    .stat-number {
        font-size: 2rem;
        font-weight: 700;
        line-height: 1;
        color: #fbbf24;
    }
    .stat-label {
        font-size: 0.75rem;
        opacity: 0.8;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        margin-top: 0.4rem;
    }
    .stat-divider {
        width: 1px;
        height: 35px;
        background: rgba(255, 255, 255, 0.2);
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

    /* Workflow section */
    .workflow-section {
        margin: 2rem 0 3rem 0;
    }
    .workflow-header {
        text-align: center;
        margin-bottom: 2.5rem;
    }
    .workflow-header h2 {
        font-size: 1.8rem;
        color: var(--text-main);
        margin-bottom: 0.5rem;
        font-weight: 600;
    }
    .workflow-header p {
        font-size: 0.95rem;
        color: var(--text-muted);
    }
    .workflow-grid {
        display: grid;
        grid-template-columns: repeat(3, minmax(0, 1fr));
        gap: 1.5rem;
    }
    .workflow-card {
        background: var(--bg-card);
        border-radius: 12px;
        padding: 1.8rem 1.5rem;
        box-shadow: 0 2px 10px rgba(15, 23, 42, 0.06);
        border: 1px solid rgba(148, 163, 184, 0.15);
        transition: all 0.2s;
    }
    .workflow-card:hover {
        border-color: var(--penn-blue);
        box-shadow: 0 4px 15px rgba(1, 31, 91, 0.12);
    }
    .workflow-number {
        background: var(--penn-blue);
        color: white;
        width: 40px;
        height: 40px;
        border-radius: 8px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 700;
        font-size: 1rem;
        margin-bottom: 1rem;
    }
    .workflow-content h3 {
        font-size: 1.1rem;
        color: var(--text-main);
        margin-bottom: 0.6rem;
        font-weight: 600;
    }
    .workflow-content p {
        font-size: 0.88rem;
        color: var(--text-muted);
        line-height: 1.5;
        margin: 0;
    }
    
    /* Info section */
    .info-section {
        background: linear-gradient(135deg, #f8fafc, #f1f5f9);
        border-radius: 12px;
        padding: 2rem;
        margin: 3rem 0;
        border: 1px solid rgba(148, 163, 184, 0.2);
    }
    .info-grid {
        display: grid;
        grid-template-columns: repeat(4, minmax(0, 1fr));
        gap: 2rem;
    }
    .info-item {
        display: flex;
        flex-direction: column;
        gap: 0.4rem;
    }
    .info-item strong {
        font-size: 0.95rem;
        color: var(--text-main);
        font-weight: 600;
    }
    .info-item span {
        font-size: 0.82rem;
        color: var(--text-muted);
        line-height: 1.4;
    }
    
    /* CTA box */
    .cta-box {
        text-align: center;
        padding: 2rem;
        background: var(--bg-card);
        border-radius: 12px;
        margin: 2rem 0;
        border: 2px dashed rgba(148, 163, 184, 0.3);
    }
    .cta-box h3 {
        font-size: 1.3rem;
        color: var(--text-main);
        margin-bottom: 0.5rem;
        font-weight: 600;
    }
    .cta-box p {
        font-size: 0.95rem;
        color: var(--text-muted);
        margin: 0;
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background: #020617;
        border-right: 1px solid #1f2933;
    }
    [data-testid="stSidebar"] * {
        color: #e5e7eb !important;
    }
    /* Sidebar home button styling */
    [data-testid="stSidebar"] button[kind="secondary"] {
        background: rgba(255, 255, 255, 0.08) !important;
        border: 1px solid rgba(255, 255, 255, 0.15) !important;
        color: #ffffff !important;
        font-weight: 500 !important;
    }
    [data-testid="stSidebar"] button[kind="secondary"]:hover {
        background: rgba(255, 255, 255, 0.15) !important;
        border-color: rgba(255, 255, 255, 0.25) !important;
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
        padding: 0.4rem 1rem !important;
        font-size: 0.86rem !important;
        font-weight: 500 !important;
        border: none !important;
        box-shadow: 0 3px 8px rgba(15, 23, 42, 0.16) !important;
        white-space: nowrap !important;
        overflow: hidden !important;
        text-overflow: ellipsis !important;
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
    
    /* Responsive design */
    @media (max-width: 1200px) {
        .evi-hero-title {
            font-size: 2.2rem;
        }
        .workflow-grid {
            grid-template-columns: repeat(2, 1fr);
        }
        .info-grid {
            grid-template-columns: repeat(2, 1fr);
        }
    }
    
    @media (max-width: 768px) {
        .evi-hero-title {
            font-size: 1.8rem;
        }
        .workflow-grid,
        .info-grid {
            grid-template-columns: 1fr;
        }
    }

</style>
""",
        unsafe_allow_html=True,
    )
