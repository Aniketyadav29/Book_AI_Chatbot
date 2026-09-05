import streamlit as st


def render_page_selector():
    """Allow user to select a specific page or section to restrict RAG retrieval.
    Stores selected page number (or None) in `st.session_state['selected_page']`.
    """
    book = st.session_state.get("current_book_data")
    max_pages = book.get("total_pages", 1) if book else 1

    col1, col2 = st.columns([1, 1])
    with col1:
        filter_enabled = st.checkbox(
            "🎯 Restrict search to specific page/section",
            value=bool(st.session_state.get("selected_page")),
            key="enable_page_filter"
        )

    with col2:
        if filter_enabled:
            current_val = st.session_state.get("selected_page") or 1
            if current_val > max_pages:
                current_val = 1
            page = st.number_input(
                f"Page/Section (1 to {max_pages})",
                min_value=1,
                max_value=max(1, max_pages),
                step=1,
                value=current_val,
                key="page_filter_number_input"
            )
            st.session_state["selected_page"] = int(page)
            st.caption(f"🔍 Questions will focus on Section/Page **{page}**.")
        else:
            st.session_state["selected_page"] = None
            st.caption("🌐 Searching across entire manuscript.")

