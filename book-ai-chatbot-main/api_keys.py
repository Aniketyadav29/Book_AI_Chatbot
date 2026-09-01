import streamlit as st
import os
from pathlib import Path

# Simple admin UI to set API keys (Groq, OpenAI, etc.)
# Keys are stored in st.session_state['api_keys'] and optionally written to .env (git‑ignored)

def _save_to_env(key: str, value: str):
    env_path = Path(__file__).parent.parent / ".env"
    # Append or replace the line for the given key
    lines = []
    if env_path.exists():
        with open(env_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
        # Remove existing line for the key
        lines = [ln for ln in lines if not ln.startswith(f"{key}=")]
    lines.append(f"{key}={value}\n")
    with open(env_path, "w", encoding="utf-8") as f:
        f.writelines(lines)

def render_api_key_manager():
    """Admin panel for entering API keys.
    Only visible after entering the admin password (checked elsewhere).
    """
    if "admin_authenticated" not in st.session_state:
        return  # Not admin yet
    st.subheader("🔐 API Key Management")
    # Load current keys from session_state if present
    keys = st.session_state.get("api_keys", {})
    groq = st.text_input("Groq API Key", value=keys.get("GROQ_API_KEY", ""), type="password")
    openai = st.text_input("OpenAI API Key", value=keys.get("OPENAI_API_KEY", ""), type="password")
    if st.button("Save Keys"):
        # Update session_state
        st.session_state.api_keys = {"GROQ_API_KEY": groq.strip(), "OPENAI_API_KEY": openai.strip()}
        # Persist to .env (git‑ignored) for convenience
        if groq:
            _save_to_env("GROQ_API_KEY", groq.strip())
        if openai:
            _save_to_env("OPENAI_API_KEY", openai.strip())
        st.success("API keys saved securely.")
