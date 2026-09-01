import streamlit as st
import os

# Simple theme toggle (light/dark) stored in session_state and applied via CSS injection.

def _dark_css() -> str:
    return """
    <style>
    .stApp {background-color: #0a0a0a; color: #f5f5f5;}
    .stButton > button {background: #444; color: #fff;}
    </style>
    """

def _light_css() -> str:
    return """
    <style>
    .stApp {background-color: #fafafa; color: #212529;}
    .stButton > button {background: #e0e0e0; color: #212529;}
    </style>
    """

def render_theme_toggle():
    """Render a toggle switch for light/dark mode and inject corresponding CSS."""
    if "theme" not in st.session_state:
        st.session_state.theme = "light"
    # Toggle UI
    theme = st.toggle("🌙 Dark mode", value=st.session_state.theme == "dark", key="theme_toggle")
    st.session_state.theme = "dark" if theme else "light"
    # Inject CSS
    if st.session_state.theme == "dark":
        st.markdown(_dark_css(), unsafe_allow_html=True)
    else:
        st.markdown(_light_css(), unsafe_allow_html=True)
