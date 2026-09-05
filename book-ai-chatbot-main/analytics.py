import streamlit as st
import sqlite3
import os
from pathlib import Path
from datetime import datetime

DB_PATH = Path(__file__).resolve().parent / "analytics.db"

def _get_admin_password() -> str:
    env_file = Path(__file__).resolve().parent / ".env"
    if env_file.exists():
        try:
            for line in env_file.read_text(encoding="utf-8-sig").splitlines():
                line = line.strip()
                if line.startswith("ADMIN_PASSWORD="):
                    pwd = line.split("=", 1)[1].strip()
                    if pwd:
                        return pwd
        except Exception:
            pass
    pwd = os.environ.get("ADMIN_PASSWORD", "").strip()
    if pwd:
        return pwd
    try:
        pwd = st.secrets.get("ADMIN_PASSWORD", "").strip()
        if pwd:
            return pwd
    except Exception:
        pass
    return "admin123"

def _init_db():
    conn = sqlite3.connect(str(DB_PATH))
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS queries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            timestamp TEXT,
            query TEXT,
            response TEXT,
            rating INTEGER
        )
    """)
    conn.commit()
    conn.close()

def log_interaction(user_id: str, query: str, response: str):
    _init_db()
    conn = sqlite3.connect(str(DB_PATH))
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO queries (user_id, timestamp, query, response, rating) VALUES (?,?,?,?,?)",
        (user_id or "anonymous", datetime.now().isoformat(), query, response, None),
    )
    conn.commit()
    conn.close()

def set_rating(entry_id: int, rating: int):
    conn = sqlite3.connect(str(DB_PATH))
    cur = conn.cursor()
    cur.execute("UPDATE queries SET rating=? WHERE id=?", (rating, entry_id))
    conn.commit()
    conn.close()

def _load_data():
    _init_db()
    conn = sqlite3.connect(str(DB_PATH))
    cur = conn.cursor()
    cur.execute("SELECT id, user_id, timestamp, query, response, rating FROM queries ORDER BY timestamp DESC LIMIT 100")
    rows = cur.fetchall()
    conn.close()
    return rows

def render_dashboard():
    """Admin dashboard with ratings, metrics, and activity charts."""
    if not st.session_state.get("admin_authenticated", False):
        st.warning("🔐 Admin access required to view interaction analytics.")
        pwd = st.text_input("Enter Admin Password", type="password", key="analytics_admin_pwd")
        if st.button("Unlock Analytics", key="unlock_analytics_btn"):
            if pwd and pwd == _get_admin_password():
                st.session_state.admin_authenticated = True
                st.rerun()
            else:
                st.error("❌ Invalid password.")
        return

    st.subheader("📊 Chatbot Analytics & Interaction Dashboard")
    _init_db()
    data = _load_data()
    if not data:
        st.info("ℹ️ No interactions logged yet. Ask questions in the library chat to populate analytics.")
        return

    import pandas as pd
    import altair as alt

    df = pd.DataFrame(data, columns=["id", "user_id", "timestamp", "query", "response", "rating"])
    df["timestamp_dt"] = pd.to_datetime(df["timestamp"], errors="coerce")

    # Metrics summary
    total_queries = len(df)
    rated_queries = df["rating"].notna().sum()
    upvotes = (df["rating"] == 1).sum()
    downvotes = (df["rating"] == -1).sum()
    satisfaction = f"{(upvotes / rated_queries * 100):.0f}%" if rated_queries > 0 else "N/A"

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("💬 Total Queries", total_queries)
    m2.metric("⭐ Feedback Count", int(rated_queries))
    m3.metric("👍 Upvotes", int(upvotes))
    m4.metric("✨ User Satisfaction", satisfaction)

    st.markdown("---")
    st.markdown("#### 📈 Query Volume Over Time")
    chart_df = df.dropna(subset=["timestamp_dt"]).sort_values("timestamp_dt")
    if not chart_df.empty:
        chart = alt.Chart(chart_df).mark_bar(color="#c8973a", opacity=0.85).encode(
            x=alt.X("hoursminutes(timestamp_dt):O", title="Time Window"),
            y=alt.Y("count():Q", title="Queries"),
            tooltip=[alt.Tooltip("count()", title="Queries")]
        ).properties(height=240)
        st.altair_chart(chart, use_container_width=True)

    st.markdown("---")
    st.markdown("#### 📜 Recent Query Log & Ratings")
    for idx, row in df.iterrows():
        with st.container():
            col1, col2 = st.columns([4, 1])
            with col1:
                st.markdown(f"**Q:** {row['query']}")
                resp_preview = row['response'][:220] + "..." if len(row['response']) > 220 else row['response']
                st.caption(f"**A:** {resp_preview}")
            with col2:
                current_rating = row['rating']
                if pd.isna(current_rating):
                    b1, b2 = st.columns(2)
                    with b1:
                        if st.button("👍", key=f"up_{row['id']}"):
                            set_rating(row['id'], 1)
                            st.rerun()
                    with b2:
                        if st.button("👎", key=f"down_{row['id']}"):
                            set_rating(row['id'], -1)
                            st.rerun()
                elif current_rating == 1:
                    st.success("👍 Upvoted")
                elif current_rating == -1:
                    st.error("👎 Downvoted")
            st.markdown("<hr style='margin:4px 0; border-color: rgba(212,175,55,0.15);'>", unsafe_allow_html=True)
