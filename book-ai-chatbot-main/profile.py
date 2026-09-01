import streamlit as st
import json
import os
from pathlib import Path

PROFILE_DIR = Path(__file__).parent / "user_data"
PROFILE_DIR.mkdir(exist_ok=True)

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

def render_profile_section():
    """Render an expander allowing the user to edit simple preferences.
    For this MVP we store only favorite genres (list of strings) and reading speed.
    """
    user_id = st.session_state.get("user_id", "anonymous")
    profile = st.session_state.get("profile", load_profile(user_id))

    with st.expander("👤 Profile Settings"):
        genres = st.multiselect("Favorite Genres", options=["Fiction", "Non‑fiction", "Poetry", "Science", "History", "Fantasy"], default=profile.get("genres", []))
        speed = st.slider("Reading Speed (words per minute)", min_value=100, max_value=500, value=profile.get("speed", 250), step=10)
        # Save on change
        if st.button("Save Profile"):
            profile["genres"] = genres
            profile["speed"] = speed
            save_profile(user_id, profile)
            st.session_state.profile = profile
            st.success("Profile saved!")
