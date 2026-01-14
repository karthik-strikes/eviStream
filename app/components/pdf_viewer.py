"""
PDF viewer component for eviStream
"""

import streamlit as st
import base64


def display_pdf_viewer(pdf_path: str, height: int = 650):
    """
    Display a PDF file in an iframe viewer.

    Args:
        pdf_path: Path to the PDF file
        height: Height of the viewer in pixels
    """
    try:
        with open(pdf_path, "rb") as f:
            base64_pdf = base64.b64encode(f.read()).decode("utf-8")

        st.markdown(
            f"""
        <div class="pdf-container">
            <iframe 
                src="data:application/pdf;base64,{base64_pdf}"
                width="100%"
                height="{height}px"
                type="application/pdf">
            </iframe>
        </div>
        """,
            unsafe_allow_html=True,
        )
    except Exception as e:
        st.error(f"Could not display PDF: {e}")



