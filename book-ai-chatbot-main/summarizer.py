"""
summarizer.py – Smart AI Summarizer
LLM-powered chapter/answer summarizer with highlight mode,
reading time estimate, bullet-point extraction, and key-quote mining.
"""
import streamlit as st
import re
import os


# Ordered list of active Groq models to try
_FALLBACK_MODELS = [
    "openai/gpt-oss-120b",
    "openai/gpt-oss-20b",
    "qwen/qwen3.8-27b",
    "qwen/qwen3.6-27b",
    "groq/compound",
    "groq/compound-mini",
]


def _get_llm():
    """Lazy-load the Groq LLM from session state, env, or secrets, with model fallback."""
    if "llm" in st.session_state and st.session_state.llm is not None:
        return st.session_state.llm
    try:
        from langchain_groq import ChatGroq
        api_key = os.environ.get("GROQ_API_KEY", "").strip()
        if not api_key:
            try:
                api_key = st.session_state.get("api_keys", {}).get("GROQ_API_KEY", "").strip()
            except Exception:
                pass
        if not api_key:
            try:
                api_key = st.secrets.get("GROQ_API_KEY", "").strip()
            except Exception:
                pass
        if not api_key:
            return None

        user_model = st.session_state.get("selected_model", "")
        candidates = []
        if user_model and user_model in _FALLBACK_MODELS:
            candidates.append(user_model)
        for m in _FALLBACK_MODELS:
            if m not in candidates:
                candidates.append(m)

        for model_name in candidates:
            try:
                return ChatGroq(model=model_name, temperature=0.3, api_key=api_key)
            except Exception:
                continue
    except Exception:
        pass
    return None


def _call_llm(prompt: str) -> str:
    """Call LLM with a prompt and return result text."""
    llm = _get_llm()
    if llm is None:
        return "⚠️ LLM not available. Please ensure your GROQ_API_KEY is set in the sidebar, .env, or Streamlit Secrets."
    try:
        from langchain_core.messages import HumanMessage
        result = llm.invoke([HumanMessage(content=prompt)])
        return result.content
    except Exception as e:
        return f"⚠️ LLM error: {e}"


def _highlight_sentences(text: str) -> str:
    """Wrap key sentences in highlight spans for visual emphasis."""
    sentences = re.split(r'(?<=[.!?])\s+', text)
    if not sentences:
        return text
    highlight_count = max(1, len(sentences) // 3)
    result_parts = []
    for i, sentence in enumerate(sentences):
        if i < highlight_count and len(sentence) > 20:
            result_parts.append(
                f"<mark style='background:rgba(212,175,55,0.25); color:#f5dfa3; "
                f"border-radius:4px; padding:1px 4px;'>{sentence}</mark>"
            )
        else:
            result_parts.append(sentence)
    return " ".join(result_parts)


def render_summarizer():
    """Render the smart AI summarizer panel."""
    st.markdown("### ⚡ AI Smart Summarizer")
    st.caption("Summarize any text, extract key points, mine memorable quotes, and estimate reading time.")

    # Source selector
    source = st.radio(
        "📄 Source",
        ["Use Last AI Answer", "Paste Custom Text", "Use Book Overview"],
        horizontal=True,
        key="sum_source"
    )

    if source == "Use Last AI Answer":
        text = st.session_state.get("last_response", "")
        if not text and st.session_state.get("uploaded_chat_history"):
            for m in reversed(st.session_state.uploaded_chat_history):
                if m.get("role") == "assistant" and m.get("content"):
                    text = m["content"]
                    break
        if not text:
            st.info("Ask a question in the chat first to generate a response to summarize.")
            return
    elif source == "Use Book Overview":
        text = st.session_state.get("current_book_overview", "")
        if not text:
            st.info("Upload and analyze a book first to generate an overview.")
            return
    else:
        text = st.text_area(
            "Paste text to summarize",
            height=180,
            key="sum_custom_text",
            placeholder="Paste any passage, chapter, or excerpt here…"
        )
        if not text.strip():
            st.warning("Enter text to summarize.")
            return

    # Reading time estimate
    word_count = len(text.split())
    read_mins = max(1, word_count // 200)
    col1, col2 = st.columns(2)
    col1.metric("📖 Word Count", f"{word_count:,}")
    col2.metric("⏱️ Reading Time", f"~{read_mins} min")

    st.markdown("---")
    mode = st.radio(
        "🎯 Summarization Mode",
        ["📝 Concise Summary", "📌 Key Bullet Points", "💬 Key Quotes", "🔆 Highlight Mode"],
        horizontal=True,
        key="sum_mode"
    )

    if st.button("✨ Generate Summary", use_container_width=True, key="sum_generate_btn"):
        with st.spinner("Analysing with AI…"):
            if mode == "📝 Concise Summary":
                prompt = (
                    f"You are a literary analyst. Summarize the following text in 3–5 clear, "
                    f"insightful sentences. Capture the core themes and main ideas.\n\nText:\n{text[:4000]}"
                )
                res = _call_llm(prompt)
                st.session_state["last_summary_result"] = res
                st.session_state["last_summary_html"] = res
                st.session_state["last_summary_mode"] = mode

            elif mode == "📌 Key Bullet Points":
                prompt = (
                    f"Extract the 5–8 most important ideas or facts from the following text as "
                    f"concise bullet points. Use '•' as bullet prefix.\n\nText:\n{text[:4000]}"
                )
                res = _call_llm(prompt)
                st.session_state["last_summary_result"] = res
                st.session_state["last_summary_html"] = res.replace(chr(10), "<br>")
                st.session_state["last_summary_mode"] = mode

            elif mode == "💬 Key Quotes":
                prompt = (
                    f"From the following text, extract 3–5 of the most powerful, memorable, "
                    f"or insightful quotes. Present each in quotation marks on a new line, "
                    f"followed by a brief (1-sentence) explanation of why it matters.\n\nText:\n{text[:4000]}"
                )
                res = _call_llm(prompt)
                st.session_state["last_summary_result"] = res
                st.session_state["last_summary_html"] = res.replace(chr(10), "<br>")
                st.session_state["last_summary_mode"] = mode

            else:  # Highlight Mode
                highlighted = _highlight_sentences(text[:3000])
                plain_summary = re.sub(r'<[^>]+>', '', highlighted)
                st.session_state["last_summary_result"] = plain_summary
                st.session_state["last_summary_html"] = highlighted
                st.session_state["last_summary_mode"] = mode

    # Display generated summary if present in session state
    saved_summary = st.session_state.get("last_summary_result")
    saved_html = st.session_state.get("last_summary_html", saved_summary)
    saved_mode = st.session_state.get("last_summary_mode", "Summary")

    if saved_summary:
        st.markdown(f"**{saved_mode}:**")
        st.markdown(f"""
        <div style='background:rgba(20,14,8,0.85);border:1px solid rgba(212,175,55,0.35);
            border-radius:12px;padding:18px;color:#f3ecd8;font-size:0.98rem;line-height:1.75;'>
        {saved_html}
        </div>""", unsafe_allow_html=True)

        st.download_button(
            label="📥 Download Generated Summary",
            data=saved_summary,
            file_name="book_summary.txt",
            mime="text/plain",
            key="sum_download",
            use_container_width=True
        )
