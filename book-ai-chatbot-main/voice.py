import streamlit as st

def render():
    """Render voice UI components.
    This placeholder adds a button that toggles voice capture.
    Real implementation would embed JavaScript SpeechRecognition
    or use the `speech_recognition` library for uploaded audio.
    """
    if st.button("🎤 Enable Voice", key="voice_btn"):
        st.session_state.voice_enabled = not st.session_state.get("voice_enabled", False)
        st.success(f"Voice mode {'enabled' if st.session_state.voice_enabled else 'disabled'}")
