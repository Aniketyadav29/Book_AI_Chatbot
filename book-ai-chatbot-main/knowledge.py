import streamlit as st
import requests


def _fetch_wikipedia(query: str) -> str:
    try:
        url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{query}" if not query.startswith("http") else query
        resp = requests.get(url, timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            return data.get("extract", "")
    except Exception:
        return ""
    return ""


def _fetch_openlibrary(isbn: str) -> str:
    try:
        url = f"https://openlibrary.org/api/books?bibkeys=ISBN:{isbn}&format=json&jscmd=data"
        resp = requests.get(url, timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            key = f"ISBN:{isbn}"
            if key in data:
                title = data[key].get("title", "")
                authors = ", ".join(a.get("name", "") for a in data[key].get("authors", []))
                return f"{title} by {authors}"
    except Exception:
        return ""
    return ""


def render_external_search():
    """Simple UI to fetch external knowledge and store it in session state.
    The fetched text is appended to `st.session_state['external_context']`.
    """
    st.subheader("🔗 External Knowledge Integration")
    query = st.text_input("Search Wikipedia or Open Library (ISBN)")
    source = st.radio("Source", ["Wikipedia", "Open Library"], horizontal=True)
    if st.button("Fetch") and query:
        if source == "Wikipedia":
            result = _fetch_wikipedia(query)
        else:
            result = _fetch_openlibrary(query)
        if result:
            st.session_state["external_context"] = result
            st.success(f"Fetched from {source}: \n{result[:300]}{'...' if len(result) > 300 else ''}")
        else:
            st.warning("No result found or an error occurred.")
