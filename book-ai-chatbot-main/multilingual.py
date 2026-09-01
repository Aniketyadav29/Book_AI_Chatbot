"""
multilingual.py – Multilingual & Translation Mode
Supports language detection and translation via LibreTranslate (free API)
with a fallback to basic hardcoded phrases. Stores language in session_state.
"""
import streamlit as st
import requests
from typing import Optional


LANGUAGES = {
    "English": "en",
    "Hindi (हिंदी)": "hi",
    "Spanish (Español)": "es",
    "French (Français)": "fr",
    "German (Deutsch)": "de",
    "Chinese (中文)": "zh",
    "Arabic (العربية)": "ar",
    "Portuguese (Português)": "pt",
    "Russian (Русский)": "ru",
    "Japanese (日本語)": "ja",
}

LIBRE_TRANSLATE_URL = "https://libretranslate.com/translate"
LIBRE_DETECT_URL = "https://libretranslate.com/detect"


def detect_language(text: str) -> str:
    """Detect language using LibreTranslate API. Falls back to 'en'."""
    try:
        resp = requests.post(
            LIBRE_DETECT_URL,
            json={"q": text[:200]},
            timeout=5,
        )
        if resp.status_code == 200:
            results = resp.json()
            if results:
                return results[0].get("language", "en")
    except Exception:
        pass
    return "en"


def translate_text(text: str, target_lang: str, source_lang: str = "auto") -> str:
    """Translate text using LibreTranslate free API."""
    if target_lang == "en" and source_lang in ("en", "auto"):
        return text
    try:
        payload = {
            "q": text,
            "source": source_lang if source_lang != "auto" else "en",
            "target": target_lang,
            "format": "text",
        }
        resp = requests.post(LIBRE_TRANSLATE_URL, json=payload, timeout=10)
        if resp.status_code == 200:
            return resp.json().get("translatedText", text)
    except Exception:
        pass
    return text  # graceful fallback – return original


def get_ui_labels(lang: str) -> dict:
    """Return localised UI label strings for key UI elements."""
    labels = {
        "en": {
            "ask_placeholder": "Ask anything about the book…",
            "search_btn": "Search",
            "upload_prompt": "Upload a book manuscript",
        },
        "hi": {
            "ask_placeholder": "किताब के बारे में कुछ भी पूछें…",
            "search_btn": "खोजें",
            "upload_prompt": "पुस्तक पांडुलिपि अपलोड करें",
        },
        "es": {
            "ask_placeholder": "Pregunta algo sobre el libro…",
            "search_btn": "Buscar",
            "upload_prompt": "Subir manuscrito",
        },
        "fr": {
            "ask_placeholder": "Posez une question sur le livre…",
            "search_btn": "Rechercher",
            "upload_prompt": "Télécharger un manuscrit",
        },
    }
    return labels.get(lang, labels["en"])


def render_language_selector():
    """Render a styled language selector and store choice in session state."""
    st.markdown("### 🌍 Language & Translation Settings")

    lang_label = st.selectbox(
        "🌐 Interface & Response Language",
        options=list(LANGUAGES.keys()),
        index=0,
        key="lang_selector",
        help="The AI will try to answer in your selected language."
    )
    selected_code = LANGUAGES[lang_label]
    st.session_state["language"] = selected_code
    st.session_state["language_label"] = lang_label

    st.success(f"✅ Language set to **{lang_label}** (`{selected_code}`)")

    # Translation tool
    st.markdown("---")
    st.markdown("#### 🔄 Quick Translator")
    src_text = st.text_area("Text to Translate", height=120, key="translate_input",
                            placeholder="Paste any text from the book here…")
    col1, col2 = st.columns(2)
    with col1:
        src_lang_label = st.selectbox("From", list(LANGUAGES.keys()), key="src_lang")
        src_code = LANGUAGES[src_lang_label]
    with col2:
        tgt_lang_label = st.selectbox("To", list(LANGUAGES.keys()), index=1, key="tgt_lang")
        tgt_code = LANGUAGES[tgt_lang_label]

    if st.button("🔄 Translate", key="translate_btn", use_container_width=True):
        if src_text.strip():
            with st.spinner("Translating via LibreTranslate…"):
                result = translate_text(src_text, tgt_code, src_code)
            st.markdown("**Translation Result:**")
            st.markdown(f"""
            <div style='
                background: rgba(20,14,8,0.8);
                border: 1px solid rgba(212,175,55,0.35);
                border-radius: 10px; padding: 16px;
                color: #f3ecd8; font-size: 1rem;
                line-height: 1.6;
            '>{result}</div>
            """, unsafe_allow_html=True)
        else:
            st.warning("Enter some text to translate.")

    # Detect language tool
    st.markdown("---")
    st.markdown("#### 🔍 Detect Language")
    detect_input = st.text_input("Paste text to detect its language", key="detect_input")
    if st.button("Detect", key="detect_btn"):
        if detect_input.strip():
            with st.spinner("Detecting…"):
                detected = detect_language(detect_input)
            lang_name = {v: k for k, v in LANGUAGES.items()}.get(detected, detected)
            st.success(f"Detected language: **{lang_name}** (`{detected}`)")
        else:
            st.warning("Enter some text first.")

    st.markdown("""
    <div style='
        background: rgba(20,14,8,0.7);
        border: 1px solid rgba(212,175,55,0.2);
        border-radius: 10px; padding: 12px 16px;
        color: #c4b595; font-size: 0.83rem; margin-top: 12px;
    '>
    ℹ️ Translation is powered by <b>LibreTranslate</b> (open-source, free API).
    Quality varies by language pair. For best results, use English as the source.
    </div>
    """, unsafe_allow_html=True)
