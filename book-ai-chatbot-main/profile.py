"""
profile.py – Personalized Reading Profile & AI Book Recommender
Users set their preferences (genres, mood, level, authors) and the AI
suggests 6 books with Open Library / Project Gutenberg / Goodreads links.
"""
import streamlit as st
import json
import os
import requests
from pathlib import Path

PROFILE_DIR = Path(__file__).parent / "user_data"
PROFILE_DIR.mkdir(exist_ok=True)

# ── Genre / preference options ────────────────────────────────────────────────
GENRES = [
    "Classic Literature", "Fantasy & Mythology", "Historical Fiction",
    "Science Fiction", "Mystery & Thriller", "Philosophy",
    "Spirituality & Religion", "Romance", "Poetry", "Biography",
    "Self-Help & Motivation", "Adventure", "Horror", "Science & Nature",
    "Political & Social", "Children & Young Adult",
]

MOODS = [
    "😌 Calm & Reflective", "🔥 Thrilling & Exciting", "😂 Light & Humorous",
    "🧠 Deep & Thought-Provoking", "😢 Emotional & Moving", "🌟 Inspiring & Uplifting",
    "🌍 Eye-Opening & Educational", "🕵️ Mysterious & Suspenseful",
]

LEVELS = ["Beginner (Simple language)", "Intermediate", "Advanced (Dense prose / classics)"]

LANGUAGES_PREF = ["English", "Hindi", "Sanskrit-translated", "Urdu", "Bengali", "Tamil", "Any"]


# ── Persistence helpers ───────────────────────────────────────────────────────

def _profile_path(user_id: str) -> Path:
    return PROFILE_DIR / f"{user_id}.json"


def load_profile(user_id: str) -> dict:
    path = _profile_path(user_id)
    if path.exists():
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}


def save_profile(user_id: str, data: dict) -> None:
    path = _profile_path(user_id)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# ── LLM recommendation engine ─────────────────────────────────────────────────

def _get_llm():
    """Lazy-load Groq LLM."""
    if st.session_state.get("llm"):
        return st.session_state.llm
    try:
        from langchain_groq import ChatGroq
        key = os.environ.get("GROQ_API_KEY", "")
        if key:
            return ChatGroq(model="llama3-8b-8192", temperature=0.6, api_key=key)
    except Exception:
        pass
    return None


def _recommend_books(profile: dict) -> str:
    """Call LLM to get personalised book recommendations with links."""
    llm = _get_llm()
    genres = ", ".join(profile.get("genres", ["Classic Literature"]))
    mood = profile.get("mood", "Deep & Thought-Provoking")
    level = profile.get("level", "Intermediate")
    authors = profile.get("fav_authors", "").strip() or "any"
    lang = profile.get("language", "English")
    extra = profile.get("extra_notes", "").strip()

    prompt = f"""You are a world-class librarian and book curator.
A reader has the following preferences:
- Favourite Genres: {genres}
- Reading Mood: {mood}
- Reading Level: {level}
- Favourite Authors (for style reference): {authors}
- Preferred Language: {lang}
- Additional notes: {extra if extra else "none"}

Recommend exactly 6 books perfectly suited to this reader.
For EACH book, provide:
1. 📚 **Title** – Author (Year)
2. 🏷️ Genre / Themes (1 line)
3. 💬 Why this reader will love it (2 sentences, personalised to their mood/genre preference)
4. 🔗 Links:
   - Project Gutenberg (if classic/free): https://www.gutenberg.org/ebooks/search/?query=TITLE
   - Open Library: https://openlibrary.org/search?q=TITLE
   - Goodreads: https://www.goodreads.com/search?q=TITLE

Format as clean markdown. Use the exact link formats above with the real book title URL-encoded."""

    if llm:
        try:
            from langchain_core.messages import HumanMessage
            result = llm.invoke([HumanMessage(content=prompt)])
            return result.content
        except Exception as e:
            return f"⚠️ LLM error: {e}"
    return "⚠️ GROQ_API_KEY not set. Please add it in the sidebar to get AI recommendations."


# ── Open Library cover fetch ──────────────────────────────────────────────────

def _get_cover(title: str) -> str:
    """Fetch book cover URL from Open Library by title search."""
    try:
        resp = requests.get(
            f"https://openlibrary.org/search.json?title={requests.utils.quote(title)}&limit=1",
            timeout=5
        )
        if resp.status_code == 200:
            docs = resp.json().get("docs", [])
            if docs:
                cover_id = docs[0].get("cover_i")
                if cover_id:
                    return f"https://covers.openlibrary.org/b/id/{cover_id}-M.jpg"
    except Exception:
        pass
    return ""


# ── Main render ───────────────────────────────────────────────────────────────

def render_profile_section():
    """Full reading profile UI with AI book recommendations and links."""

    user_id = st.session_state.get("user_id", "anonymous")
    profile = st.session_state.get("profile", load_profile(user_id))

    # ── Header ────────────────────────────────────────────────────────────────
    st.markdown("""
    <div style='
        background: linear-gradient(135deg, rgba(30,20,10,0.9), rgba(20,14,8,0.95));
        border: 1px solid rgba(212,175,55,0.45);
        border-radius: 16px; padding: 22px 28px; margin-bottom: 20px;
    '>
        <h3 style='color:#f5dfa3;font-family:Cinzel,serif;margin:0 0 6px 0;'>
            👤 Your Personal Reading Profile
        </h3>
        <p style='color:#c4b595;margin:0;font-size:0.92rem;'>
            Tell us your reading preferences and our AI will curate a personalised book list —
            complete with links to read or download each book for free.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # ── Preference Form ───────────────────────────────────────────────────────
    with st.form("profile_form"):
        st.markdown("#### 📚 Reading Preferences")

        col1, col2 = st.columns(2)

        with col1:
            genres = st.multiselect(
                "🎭 Favourite Genres *(pick 1–5)*",
                options=GENRES,
                default=profile.get("genres", ["Classic Literature"]),
                help="Select genres you enjoy most."
            )
            mood = st.selectbox(
                "💭 Current Reading Mood",
                options=MOODS,
                index=MOODS.index(profile.get("mood", MOODS[3])) if profile.get("mood") in MOODS else 3,
            )
            level = st.selectbox(
                "📖 Reading Level",
                options=LEVELS,
                index=LEVELS.index(profile.get("level", LEVELS[1])) if profile.get("level") in LEVELS else 1,
            )

        with col2:
            fav_authors = st.text_input(
                "✍️ Favourite Authors *(optional)*",
                value=profile.get("fav_authors", ""),
                placeholder="e.g. Rabindranath Tagore, Fyodor Dostoevsky",
                help="We'll suggest books in a similar style."
            )
            lang = st.selectbox(
                "🌐 Preferred Language",
                options=LANGUAGES_PREF,
                index=LANGUAGES_PREF.index(profile.get("language", "English")) if profile.get("language") in LANGUAGES_PREF else 0,
            )
            speed = st.slider(
                "⚡ Reading Speed (words/min)",
                min_value=100, max_value=600,
                value=profile.get("speed", 250), step=25,
                help="Helps us estimate reading time for recommendations."
            )

        extra_notes = st.text_area(
            "💡 Anything else? *(optional)*",
            value=profile.get("extra_notes", ""),
            height=80,
            placeholder="e.g. 'I loved the Mahabharata', 'I prefer short books', 'I want Indian authors'…"
        )

        submitted = st.form_submit_button("💾 Save & Get AI Book Recommendations", use_container_width=True)

    # ── Save & Recommend ─────────────────────────────────────────────────────
    if submitted:
        if not genres:
            st.warning("⚠️ Please select at least one genre.")
        else:
            profile.update({
                "genres": genres,
                "mood": mood,
                "level": level,
                "fav_authors": fav_authors,
                "language": lang,
                "speed": speed,
                "extra_notes": extra_notes,
            })
            save_profile(user_id, profile)
            st.session_state.profile = profile
            st.success("✅ Profile saved!")

            with st.spinner("🤖 Curating personalised book recommendations for you…"):
                recs = _recommend_books(profile)
            st.session_state["book_recommendations"] = recs

    # ── Show Saved Profile Summary ────────────────────────────────────────────
    if st.session_state.get("profile"):
        p = st.session_state.profile
        if p.get("genres"):
            col1, col2, col3 = st.columns(3)
            col1.metric("🎭 Genres", len(p.get("genres", [])))
            col2.metric("📖 Level", p.get("level", "—").split(" ")[0])
            col3.metric("⚡ Speed", f"{p.get('speed', 250)} wpm")

    # ── Display Recommendations ───────────────────────────────────────────────
    recs_text = st.session_state.get("book_recommendations", "")
    if recs_text:
        st.markdown("---")
        st.markdown("""
        <h3 style='color:#f5dfa3;font-family:Cinzel,serif;margin-bottom:6px;'>
            📖 Your Personalised Book Recommendations
        </h3>
        <p style='color:#c4b595;font-size:0.9rem;margin-bottom:18px;'>
            Curated by AI based on your preferences · Click links to read or download
        </p>
        """, unsafe_allow_html=True)

        st.markdown(
            f"""<div style='
                background: rgba(16,11,7,0.85);
                border: 1px solid rgba(212,175,55,0.35);
                border-radius: 14px; padding: 24px 28px;
                color: #f3ecd8; font-size: 0.97rem; line-height: 1.85;
                font-family: "Plus Jakarta Sans", sans-serif;
            '>{recs_text}</div>""",
            unsafe_allow_html=True
        )

        # Download recommendations
        st.download_button(
            label="📥 Download My Book List",
            data=recs_text,
            file_name="my_book_recommendations.md",
            mime="text/markdown",
            key="rec_download_btn"
        )

        # Quick links panel
        st.markdown("---")
        st.markdown("#### 🔗 Quick Access – Find Any Book")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown("""
            <a href="https://www.gutenberg.org/browse/scores/top" target="_blank" style="
                display:block; background:linear-gradient(135deg,#2a1a0a,#1a0f06);
                border:1px solid rgba(212,175,55,0.4); border-radius:10px;
                padding:14px; text-align:center; text-decoration:none; color:#e5c98b;
                font-weight:600; font-size:0.92rem;
            ">📜 Project Gutenberg<br><small style='color:#c4b595;font-weight:400;'>70,000+ free classics</small></a>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown("""
            <a href="https://openlibrary.org" target="_blank" style="
                display:block; background:linear-gradient(135deg,#2a1a0a,#1a0f06);
                border:1px solid rgba(212,175,55,0.4); border-radius:10px;
                padding:14px; text-align:center; text-decoration:none; color:#e5c98b;
                font-weight:600; font-size:0.92rem;
            ">📚 Open Library<br><small style='color:#c4b595;font-weight:400;'>Borrow & read online</small></a>
            """, unsafe_allow_html=True)
        with col3:
            st.markdown("""
            <a href="https://www.goodreads.com" target="_blank" style="
                display:block; background:linear-gradient(135deg,#2a1a0a,#1a0f06);
                border:1px solid rgba(212,175,55,0.4); border-radius:10px;
                padding:14px; text-align:center; text-decoration:none; color:#e5c98b;
                font-weight:600; font-size:0.92rem;
            ">⭐ Goodreads<br><small style='color:#c4b595;font-weight:400;'>Reviews & community</small></a>
            """, unsafe_allow_html=True)

    elif not submitted:
        # First-time hint
        st.markdown("""
        <div style='
            background: rgba(20,14,8,0.75);
            border: 1px dashed rgba(212,175,55,0.3);
            border-radius: 12px; padding: 20px 24px; margin-top: 16px;
            color: #c4b595; text-align: center; font-size: 0.95rem;
        '>
        🎯 <strong>Set your preferences above</strong> and click
        <em>"Save & Get AI Book Recommendations"</em> to receive a curated list of
        6 books tailored just for you — with links to read them for free!
        </div>
        """, unsafe_allow_html=True)
