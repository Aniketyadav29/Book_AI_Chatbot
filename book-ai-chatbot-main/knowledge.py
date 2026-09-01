"""
knowledge.py – External Knowledge Integration
Fetches author/book data from Wikipedia and Open Library,
renders a rich context panel, and stores results in session state
so they can be injected into the RAG pipeline.
"""
import streamlit as st
import requests
from typing import Optional


# ── API helpers ───────────────────────────────────────────────────────────────

def _fetch_wikipedia(query: str) -> dict:
    """Fetch Wikipedia page summary. Returns dict with title, extract, thumbnail."""
    try:
        url = (
            f"https://en.wikipedia.org/api/rest_v1/page/summary/"
            f"{requests.utils.quote(query)}"
        )
        resp = requests.get(url, timeout=6)
        if resp.status_code == 200:
            data = resp.json()
            return {
                "title": data.get("title", query),
                "extract": data.get("extract", ""),
                "thumbnail": data.get("thumbnail", {}).get("source", ""),
                "url": data.get("content_urls", {}).get("desktop", {}).get("page", ""),
            }
    except Exception:
        pass
    return {}


def _fetch_openlibrary(isbn_or_title: str) -> dict:
    """Search Open Library by ISBN or title. Returns author, title, year, cover."""
    # Try ISBN first
    try:
        if isbn_or_title.replace("-", "").isdigit():
            url = f"https://openlibrary.org/api/books?bibkeys=ISBN:{isbn_or_title}&format=json&jscmd=data"
            resp = requests.get(url, timeout=6)
            if resp.status_code == 200:
                data = resp.json()
                key = f"ISBN:{isbn_or_title}"
                if key in data:
                    book = data[key]
                    return {
                        "title": book.get("title", ""),
                        "authors": ", ".join(a.get("name", "") for a in book.get("authors", [])),
                        "year": book.get("publish_date", ""),
                        "cover": book.get("cover", {}).get("medium", ""),
                        "subjects": ", ".join(s.get("name", "") for s in book.get("subjects", [])[:5]),
                        "url": f"https://openlibrary.org{book.get('key', '')}",
                    }
        # Search by title
        search_url = f"https://openlibrary.org/search.json?title={requests.utils.quote(isbn_or_title)}&limit=1"
        resp = requests.get(search_url, timeout=6)
        if resp.status_code == 200:
            docs = resp.json().get("docs", [])
            if docs:
                d = docs[0]
                cover_id = d.get("cover_i", "")
                cover_url = f"https://covers.openlibrary.org/b/id/{cover_id}-M.jpg" if cover_id else ""
                return {
                    "title": d.get("title", ""),
                    "authors": ", ".join(d.get("author_name", [])),
                    "year": str(d.get("first_publish_year", "")),
                    "cover": cover_url,
                    "subjects": ", ".join(d.get("subject", [])[:5]),
                    "url": f"https://openlibrary.org{d.get('key', '')}",
                }
    except Exception:
        pass
    return {}


def _fetch_gutenberg(author_or_title: str) -> list:
    """Search Project Gutenberg for free books."""
    try:
        url = f"https://gutendex.com/books?search={requests.utils.quote(author_or_title)}&page_size=5"
        resp = requests.get(url, timeout=6)
        if resp.status_code == 200:
            results = resp.json().get("results", [])
            books = []
            for b in results[:5]:
                books.append({
                    "title": b.get("title", ""),
                    "authors": ", ".join(a.get("name", "") for a in b.get("authors", [])),
                    "download_count": b.get("download_count", 0),
                    "formats": list(b.get("formats", {}).keys()),
                })
            return books
    except Exception:
        pass
    return []


# ── Render ────────────────────────────────────────────────────────────────────

def render_external_search():
    """Render the External Knowledge Integration panel."""
    st.markdown("### 🔗 External Knowledge Integration")
    st.caption("Fetch author/book data from Wikipedia, Open Library, and Project Gutenberg to enrich your research.")

    source = st.radio(
        "📚 Knowledge Source",
        ["🌐 Wikipedia", "📖 Open Library", "📜 Project Gutenberg (Free Books)"],
        horizontal=True,
        key="ext_source"
    )

    query = st.text_input(
        "Search query (book title, author name, or ISBN)",
        placeholder="e.g. Mahabharata, Jane Austen, 9780141439587",
        key="ext_query"
    )

    if st.button("🔍 Fetch Knowledge", use_container_width=True, key="ext_fetch_btn"):
        if not query.strip():
            st.warning("Enter a search query first.")
            return

        with st.spinner("Fetching from external sources…"):

            if source == "🌐 Wikipedia":
                data = _fetch_wikipedia(query)
                if data:
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.markdown(f"#### 📖 {data['title']}")
                        st.markdown(f"""
                        <div style='background:rgba(20,14,8,0.8);border:1px solid rgba(212,175,55,0.3);
                            border-radius:12px;padding:16px;color:#f3ecd8;line-height:1.7;font-size:0.95rem;'>
                        {data['extract']}
                        </div>""", unsafe_allow_html=True)
                        if data.get("url"):
                            st.markdown(f"[🔗 Read full article on Wikipedia]({data['url']})")
                    with col2:
                        if data.get("thumbnail"):
                            st.image(data["thumbnail"], caption=data["title"], use_container_width=True)

                    # Store for RAG injection
                    st.session_state["external_context"] = f"Wikipedia: {data['title']}\n\n{data['extract']}"
                    st.success("✅ Context stored and available for RAG queries.")
                else:
                    st.error("❌ No Wikipedia article found. Try a different search term.")

            elif source == "📖 Open Library":
                data = _fetch_openlibrary(query)
                if data:
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.markdown(f"#### 📚 {data.get('title', 'Unknown Title')}")
                        st.markdown(f"**Author(s):** {data.get('authors', 'N/A')}")
                        st.markdown(f"**First Published:** {data.get('year', 'N/A')}")
                        if data.get("subjects"):
                            st.markdown(f"**Subjects:** {data.get('subjects', '')}")
                        if data.get("url"):
                            st.markdown(f"[🔗 View on Open Library]({data['url']})")
                    with col2:
                        if data.get("cover"):
                            st.image(data["cover"], caption="Book Cover", use_container_width=True)

                    summary = (
                        f"Open Library: {data.get('title','')} by {data.get('authors','')}. "
                        f"Published: {data.get('year','')}. Subjects: {data.get('subjects','')}."
                    )
                    st.session_state["external_context"] = summary
                    st.success("✅ Book metadata stored for RAG queries.")
                else:
                    st.error("❌ No book found. Try a title or ISBN.")

            else:  # Project Gutenberg
                books = _fetch_gutenberg(query)
                if books:
                    st.markdown("#### 📜 Free Books from Project Gutenberg")
                    for b in books:
                        with st.expander(f"📗 {b['title']} — {b['authors']}"):
                            st.write(f"**Downloads:** {b['download_count']:,}")
                            st.write(f"**Formats:** {', '.join(b['formats'][:4])}")
                    st.session_state["external_context"] = (
                        "Project Gutenberg results: " +
                        "; ".join(f"{b['title']} by {b['authors']}" for b in books)
                    )
                    st.success("✅ Gutenberg results stored for RAG queries.")
                else:
                    st.warning("No books found on Project Gutenberg.")

    # Show stored context
    if st.session_state.get("external_context"):
        with st.expander("💾 Stored External Context (injected into next query)"):
            st.text_area(
                "Context",
                value=st.session_state["external_context"][:1500],
                height=140,
                disabled=True,
                key="ext_ctx_display"
            )
            if st.button("🗑️ Clear Context", key="ext_clear"):
                del st.session_state["external_context"]
                st.rerun()
