import streamlit as st
from config.theme import Colors

def page_header(title: str, subtitle: str = ""):
    """Renders a premium page header."""
    st.markdown(f"""
        <div style="margin-bottom: 2rem; animation: fadeIn 0.8s ease-out;">
            <h1 style="margin-bottom: 0;">{title}</h1>
            <p style="color: {Colors.TEXT_SECONDARY}; font-size: 1.1rem; margin-top: 0.5rem;">{subtitle}</p>
        </div>
    """, unsafe_allow_html=True)

def section_header(title: str):
    """Renders a section header."""
    st.markdown(f"""
        <div style="margin-top: 2rem; margin-bottom: 1rem; border-bottom: 1px solid {Colors.BORDER}; padding-bottom: 0.5rem;">
            <h3 style="color: {Colors.PRIMARY}; margin: 0; font-weight: 600;">{title}</h3>
        </div>
    """, unsafe_allow_html=True)
