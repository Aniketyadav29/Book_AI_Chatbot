import streamlit as st

# Ancient Heritage Theme Tokens & Mode Styling

def _dark_css() -> str:
    return """
    <style>
    .stApp {
        background-color: #0e0a07 !important;
        color: #f5eedb !important;
    }
    .stButton > button {
        background: linear-gradient(135deg, #966330 0%, #633e1a 100%) !important;
        color: #fff4d6 !important;
        border: 1px solid rgba(212, 175, 55, 0.6) !important;
    }
    </style>
    """

def _light_css() -> str:
    return """
    <style>
    .stApp {
        background-color: #fcf8f0 !important;
        color: #2b2118 !important;
    }
    .stButton > button {
        background: linear-gradient(135deg, #d8ab62 0%, #b88636 100%) !important;
        color: #1a1208 !important;
        border: 1px solid rgba(184, 134, 54, 0.8) !important;
    }
    </style>
    """

def render_theme_toggle():
    """Render a toggle switch for obsidian dark mode vs parchment light mode."""
    if "theme" not in st.session_state:
        st.session_state.theme = "dark"
    theme = st.toggle("🌙 Obsidian Dark Mode", value=(st.session_state.theme == "dark"), key="heritage_theme_toggle")
    st.session_state.theme = "dark" if theme else "light"
    if st.session_state.theme == "dark":
        st.markdown(_dark_css(), unsafe_allow_html=True)
    else:
        st.markdown(_light_css(), unsafe_allow_html=True)
