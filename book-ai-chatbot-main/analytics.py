import streamlit as st
import sqlite3
from datetime import datetime

DB_PATH = "analytics.db"

def _init_db():
    conn = sqlite3.connect(DB_PATH)
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
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO queries (user_id, timestamp, query, response, rating) VALUES (?,?,?,?,?)",
        (user_id, datetime.utcnow().isoformat(), query, response, None),
    )
    conn.commit()
    conn.close()

def set_rating(entry_id: int, rating: int):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("UPDATE queries SET rating=? WHERE id=?", (rating, entry_id))
    conn.commit()
    conn.close()

def _load_data():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT id, user_id, timestamp, query, response, rating FROM queries ORDER BY timestamp DESC LIMIT 100")
    rows = cur.fetchall()
    conn.close()
    return rows

def render_dashboard():
    """Admin dashboard with thumbs‑up/down rating and simple charts (Altair)."""
    if "admin_authenticated" not in st.session_state:
        st.warning("Admin access required. Enter password below.")
        pwd = st.text_input("Admin password", type="password")
        if pwd and pwd == st.secrets.get("admin_password"):
            st.session_state.admin_authenticated = True
        else:
            return
    st.subheader("📊 Analytics Dashboard")
    _init_db()
    data = _load_data()
    if not data:
        st.info("No interactions logged yet.")
        return
    # Show a table with rating buttons
    import pandas as pd
    import altair as alt
    df = pd.DataFrame(data, columns=["id", "user_id", "timestamp", "query", "response", "rating"])
    for idx, row in df.iterrows():
        col1, col2 = st.columns([4, 1])
        with col1:
            st.write(f"**Q:** {row['query']}")
            st.write(f"**A:** {row['response'][:200]}{'...' if len(row['response'])>200 else ''}")
        with col2:
            if pd.isna(row['rating']):
                if st.button("👍", key=f"up_{row['id']}"):
                    set_rating(row['id'], 1)
                if st.button("👎", key=f"down_{row['id']}"):
                    set_rating(row['id'], -1)
    # Simple chart: queries over time
    chart = alt.Chart(df).mark_line().encode(
        x="timestamp:T",
        y=alt.Y("count():Q", title="Number of Queries"),
        tooltip=["timestamp", "query"]
    ).properties(width=700, height=300)
    st.altair_chart(chart, use_container_width=True)
