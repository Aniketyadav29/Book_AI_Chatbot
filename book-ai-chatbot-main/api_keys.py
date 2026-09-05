import streamlit as st
import os
from pathlib import Path

# Simple admin UI to set API keys (Groq, OpenAI, etc.)
# Keys are stored in st.session_state['api_keys'] and optionally written to .env (git‑ignored)

def _save_to_env(key: str, value: str):
    env_path = Path(__file__).resolve().parent / ".env"
    lines = []
    if env_path.exists():
        with open(env_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
        lines = [ln for ln in lines if not ln.startswith(f"{key}=")]
    lines.append(f"{key}={value}\n")
    with open(env_path, "w", encoding="utf-8") as f:
        f.writelines(lines)

def render_api_key_manager():
    """Admin panel for entering API keys.
    Only visible after entering the admin password.
    """
    if not st.session_state.get("admin_authenticated", False):
        return  # Not authenticated

    st.subheader("🔐 API Key Management")
    st.caption("Configured keys are saved to session state, runtime environment, and local `.env` (git-ignored).")

    keys = st.session_state.get("api_keys", {})
    groq_default = keys.get("GROQ_API_KEY", "") or os.environ.get("GROQ_API_KEY", "")
    pinecone_default = keys.get("PINECONE_API_KEY", "") or os.environ.get("PINECONE_API_KEY", "")
    openai_default = keys.get("OPENAI_API_KEY", "") or os.environ.get("OPENAI_API_KEY", "")

    groq = st.text_input("Groq API Key", value=groq_default, type="password", placeholder="gsk_...")
    pinecone = st.text_input("Pinecone API Key (Optional)", value=pinecone_default, type="password", placeholder="pcsk_...")
    openai = st.text_input("OpenAI API Key (Optional)", value=openai_default, type="password", placeholder="sk-...")

    if st.button("💾 Save Keys", key="save_admin_api_keys", use_container_width=True):
        if "api_keys" not in st.session_state:
            st.session_state.api_keys = {}

        if groq.strip():
            st.session_state.api_keys["GROQ_API_KEY"] = groq.strip()
            os.environ["GROQ_API_KEY"] = groq.strip()
            _save_to_env("GROQ_API_KEY", groq.strip())

        if pinecone.strip():
            st.session_state.api_keys["PINECONE_API_KEY"] = pinecone.strip()
            os.environ["PINECONE_API_KEY"] = pinecone.strip()
            _save_to_env("PINECONE_API_KEY", pinecone.strip())

        if openai.strip():
            st.session_state.api_keys["OPENAI_API_KEY"] = openai.strip()
            os.environ["OPENAI_API_KEY"] = openai.strip()
            _save_to_env("OPENAI_API_KEY", openai.strip())

        st.success("✅ API keys updated and securely saved.")
