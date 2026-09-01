import streamlit as st

def render_language_selector():
    """Render a language selector and store choice in session state."""
    languages = ["en", "es", "fr", "de", "zh", "hi"]
    selected = st.selectbox("🌐 Language", options=languages, index=languages.index(st.session_state.get("language", "en")))
    st.session_state.language = selected
    st.caption(f"Selected language: {selected}")
