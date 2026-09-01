import streamlit as st


def render_summarizer():
    """Render a button to summarize the latest chatbot answer.
    When pressed, it sends the last answer to the LLM with a summarization prompt
    and displays the result with <mark> highlights (placeholder implementation).
    """
    if "last_response" not in st.session_state:
        st.info("Ask a question first to enable summarization.")
        return
    if st.button("⚡ Summarize Answer"):
        # Placeholder: In a real implementation you would call the LLM with a summarization prompt.
        summary = f"**Summary:** {st.session_state.last_response[:200]}..."
        # Highlight key sentences – demo by wrapping every sentence ending with a period.
        highlighted = summary.replace('. ', '. <mark>').replace('.<mark>', '</mark>.')
        st.markdown(highlighted, unsafe_allow_html=True)
