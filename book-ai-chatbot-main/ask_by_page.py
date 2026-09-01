import streamlit as st


def render_page_selector():
    """Allow user to select a specific page (or chunk) to restrict retrieval.
    The selected page number is stored in `st.session_state['selected_page']`.
    """
    # For demo, allow user to type a page number. In production, you'd populate based on metadata.
    page = st.number_input("📄 Page Selector (Ask‑by‑Page)", min_value=1, step=1, value=st.session_state.get("selected_page", 1))
    st.session_state["selected_page"] = page
    st.caption(f"Responses will be filtered to page {page} where possible.")
