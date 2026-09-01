"""
offline.py – Offline / Local LLM Mode
Provides a UI to configure and use a locally-running Ollama model
(or any OpenAI-compatible local endpoint) as an alternative to Groq.
"""
import streamlit as st
import os
import requests


OLLAMA_DEFAULT_URL = "http://localhost:11434"
POPULAR_MODELS = [
    "llama3",
    "llama3:8b",
    "mistral",
    "phi3",
    "gemma",
    "gemma2",
    "deepseek-r1",
    "codellama",
    "orca-mini",
]


def _check_ollama(base_url: str) -> bool:
    """Check if Ollama server is reachable."""
    try:
        resp = requests.get(f"{base_url}/api/tags", timeout=3)
        return resp.status_code == 200
    except Exception:
        return False


def _list_local_models(base_url: str) -> list:
    """Return list of locally available Ollama model names."""
    try:
        resp = requests.get(f"{base_url}/api/tags", timeout=4)
        if resp.status_code == 200:
            models = resp.json().get("models", [])
            return [m["name"] for m in models]
    except Exception:
        pass
    return []


def _call_ollama(base_url: str, model: str, prompt: str, system: str = "") -> str:
    """Send a prompt to local Ollama and stream the response."""
    try:
        payload = {
            "model": model,
            "prompt": prompt,
            "system": system,
            "stream": False,
        }
        resp = requests.post(f"{base_url}/api/generate", json=payload, timeout=60)
        if resp.status_code == 200:
            return resp.json().get("response", "No response returned.")
    except requests.exceptions.ConnectionError:
        return "❌ Could not connect to Ollama. Make sure it's running (`ollama serve`)."
    except Exception as e:
        return f"❌ Error: {e}"
    return "❌ Unexpected error."


def render():
    """Render the Offline / Local LLM mode panel."""
    st.markdown("### 💻 Offline Local LLM Mode (via Ollama)")
    st.caption("Run AI queries entirely offline using a locally-installed Ollama model. No API key required.")

    # Connection settings
    with st.expander("⚙️ Ollama Server Settings", expanded=True):
        base_url = st.text_input(
            "Ollama Server URL",
            value=st.session_state.get("ollama_url", OLLAMA_DEFAULT_URL),
            key="ollama_url_input",
            help="Default: http://localhost:11434 – change if Ollama runs on a different port."
        )
        st.session_state["ollama_url"] = base_url

        col1, col2 = st.columns([2, 1])
        with col1:
            is_online = _check_ollama(base_url)
        with col2:
            if st.button("🔄 Check Connection", key="ollama_check"):
                is_online = _check_ollama(base_url)

        if is_online:
            st.success(f"✅ Ollama is **online** at `{base_url}`")
        else:
            st.error("❌ Ollama not detected. Install it from [ollama.com](https://ollama.com) and run `ollama serve`.")

    # Model selection
    st.markdown("---")
    local_models = _list_local_models(base_url)
    if local_models:
        model_options = local_models
        st.success(f"Found **{len(local_models)}** local model(s): `{'`, `'.join(local_models)}`")
    else:
        model_options = POPULAR_MODELS
        st.info("No local models detected. Showing popular model names – pull one first with `ollama pull <model>`.")

    selected_model = st.selectbox(
        "🤖 Select Local Model",
        options=model_options,
        key="ollama_model_sel"
    )
    st.session_state["ollama_model"] = selected_model

    # Quick install guide
    with st.expander("📖 How to set up Ollama"):
        st.markdown("""
        1. **Install Ollama**: Download from [ollama.com](https://ollama.com/download) (Windows, macOS, Linux)
        2. **Start the server**: Run `ollama serve` in your terminal
        3. **Pull a model**: `ollama pull llama3` (or any model above)
        4. **Come back here** and click "Check Connection" — you're ready!

        **Recommended models for book Q&A:**
        | Model | Size | Best For |
        |-------|------|----------|
        | `llama3:8b` | 4.7 GB | General Q&A (fast) |
        | `mistral` | 4.1 GB | Creative analysis |
        | `phi3` | 2.3 GB | Low-RAM devices |
        | `gemma2` | 5.5 GB | High accuracy |
        """)

    # Chat interface
    st.markdown("---")
    st.markdown("#### 🗨️ Chat with Local Model")

    # Show book context hint
    if st.session_state.get("current_book_data"):
        book = st.session_state["current_book_data"]
        st.info(f"📖 Active book: **{book['filename']}** — context will be injected automatically.")
    else:
        st.caption("No book loaded. Queries will use only the local model's built-in knowledge.")

    sys_prompt = st.text_area(
        "System Prompt (optional)",
        value="You are a literary scholar and book expert. Answer questions thoughtfully and cite relevant passages when possible.",
        height=80,
        key="ollama_sys_prompt"
    )

    user_query = st.text_area(
        "Your Question",
        height=100,
        placeholder="Ask anything about books, literature, or philosophy…",
        key="ollama_user_query"
    )

    if st.button("🚀 Ask Local Model", use_container_width=True, key="ollama_ask_btn"):
        if not user_query.strip():
            st.warning("Enter a question first.")
        elif not is_online:
            st.error("Ollama is not running. Please start it first.")
        else:
            # Inject book context if available
            context = ""
            if st.session_state.get("current_book_data"):
                book = st.session_state["current_book_data"]
                full_text = book.get("full_text", "")
                context = f"\n\nBook Context (from '{book['filename']}'):\n{full_text[:3000]}"

            full_prompt = f"{user_query}{context}"

            with st.spinner(f"🤖 Querying `{selected_model}` locally…"):
                result = _call_ollama(base_url, selected_model, full_prompt, sys_prompt)

            st.markdown("**🤖 Local Model Response:**")
            st.markdown(f"""
            <div style='background:rgba(20,14,8,0.85);border:1px solid rgba(212,175,55,0.35);
                border-radius:12px;padding:18px;color:#f3ecd8;font-size:0.97rem;line-height:1.75;'>
            {result.replace(chr(10), "<br>")}
            </div>""", unsafe_allow_html=True)

            # Store for summarizer
            st.session_state["last_response"] = result

            st.download_button(
                "📥 Download Response",
                data=result,
                file_name="local_llm_response.txt",
                mime="text/plain",
                key="ollama_download"
            )

    st.markdown("---")
    st.markdown("""
    <div style='background:rgba(20,14,8,0.7);border:1px solid rgba(212,175,55,0.2);
        border-radius:10px;padding:14px 18px;color:#c4b595;font-size:0.85rem;'>
    🔒 <strong>100% Private:</strong> When using Offline Mode, your books and questions
    never leave your machine. No cloud API is called. Perfect for sensitive or confidential documents.
    </div>
    """, unsafe_allow_html=True)
