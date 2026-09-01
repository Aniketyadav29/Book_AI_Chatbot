"""
summarizer.py – Smart AI Summarizer
LLM-powered chapter/answer summarizer with highlight mode,
reading time estimate, bullet-point extraction, and key-quote mining.
"""
import streamlit as st
import re
import os


def _get_llm():
    """Lazy-load the Groq LLM from session state or env."""
    if "llm" in st.session_state and st.session_state.llm is not None:
        return st.session_state.llm
    try:
        from langchain_groq import ChatGroq
        api_key = os.environ.get("GROQ_API_KEY", "")
        if api_key:
            return ChatGroq(model="llama3-8b-8192", temperature=0.3, api_key=api_key)
    except Exception:
        pass
    return None


def _call_llm(prompt: str) -> str:
    """Call LLM with a prompt and return result text."""
    llm = _get_llm()
    if llm is None:
        return "⚠️ LLM not available. Please ensure your GROQ_API_KEY is set."
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
    # Highlight the first 30% of sentences as "key"
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

    if st.button("✨ Generate", use_container_width=True, key="sum_generate_btn"):
        with st.spinner("Analysing with AI…"):

            if mode == "📝 Concise Summary":
                prompt = (
                    f"You are a literary analyst. Summarize the following text in 3–5 clear, "
                    f"insightful sentences. Capture the core themes and main ideas.\n\nText:\n{text[:4000]}"
                )
                result = _call_llm(prompt)
                st.markdown("**📝 Summary:**")
                st.markdown(f"""
                <div style='background:rgba(20,14,8,0.8);border:1px solid rgba(212,175,55,0.35);
                    border-radius:12px;padding:18px;color:#f3ecd8;font-size:0.98rem;line-height:1.7;'>
                {result}
                </div>""", unsafe_allow_html=True)

            elif mode == "📌 Key Bullet Points":
                prompt = (
                    f"Extract the 5–8 most important ideas or facts from the following text as "
                    f"concise bullet points. Use '•' as bullet prefix.\n\nText:\n{text[:4000]}"
                )
                result = _call_llm(prompt)
                st.markdown("**📌 Key Points:**")
                st.markdown(f"""
                <div style='background:rgba(20,14,8,0.8);border:1px solid rgba(212,175,55,0.35);
                    border-radius:12px;padding:18px;color:#f3ecd8;font-size:0.98rem;line-height:1.8;'>
                {result.replace(chr(10), "<br>")}
                </div>""", unsafe_allow_html=True)

            elif mode == "💬 Key Quotes":
                prompt = (
                    f"From the following text, extract 3–5 of the most powerful, memorable, "
                    f"or insightful quotes. Present each in quotation marks on a new line, "
                    f"followed by a brief (1-sentence) explanation of why it matters.\n\nText:\n{text[:4000]}"
                )
                result = _call_llm(prompt)
                st.markdown("**💬 Key Quotes:**")
                st.markdown(f"""
                <div style='background:rgba(20,14,8,0.8);border:1px solid rgba(212,175,55,0.35);
                    border-radius:12px;padding:18px;color:#f3ecd8;font-size:0.98rem;line-height:1.8;
                    font-style:italic;'>
                {result.replace(chr(10), "<br>")}
                </div>""", unsafe_allow_html=True)

            else:  # Highlight Mode
                st.markdown("**🔆 Highlighted Key Sentences:**")
                highlighted = _highlight_sentences(text[:3000])
                st.markdown(f"""
                <div style='background:rgba(20,14,8,0.8);border:1px solid rgba(212,175,55,0.35);
                    border-radius:12px;padding:18px;color:#f3ecd8;font-size:0.97rem;line-height:1.8;'>
                {highlighted}
                </div>""", unsafe_allow_html=True)

        # Download button
        st.download_button(
            label="📥 Download Summary",
            data=text,
            file_name="book_summary.txt",
            mime="text/plain",
            key="sum_download"
        )
