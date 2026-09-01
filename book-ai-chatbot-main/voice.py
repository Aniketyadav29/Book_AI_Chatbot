"""
voice.py – Voice-Enabled Conversations
Uses browser SpeechRecognition API (via streamlit-js-eval / HTML component)
and Web Speech Synthesis for text-to-speech output.
"""
import streamlit as st
import streamlit.components.v1 as components


# ── JS Speech Recognition component ──────────────────────────────────────────
_STT_SCRIPT = """
<div style="
  background: linear-gradient(135deg, rgba(30,20,10,0.85), rgba(20,14,8,0.9));
  border: 1px solid rgba(212,175,55,0.4);
  border-radius: 14px;
  padding: 20px 24px;
  margin: 10px 0;
  font-family: 'Cinzel', serif;
">
  <p style="color:#e5c98b; font-size:1rem; margin-bottom:12px; font-weight:600;">
    🎤 Voice Input (Browser Speech Recognition)
  </p>
  <button id="startBtn" onclick="startListening()" style="
      background: linear-gradient(135deg, #c8973a, #a07828);
      color: #0d0a06; border: none; border-radius: 8px;
      padding: 10px 24px; font-weight: 700; cursor: pointer;
      font-family: 'Cinzel', serif; font-size: 0.9rem;
      box-shadow: 0 3px 10px rgba(0,0,0,0.5); margin-right:10px;
  ">🎙️ Start Listening</button>
  <button onclick="stopListening()" style="
      background: rgba(60,40,20,0.7);
      color: #e5c98b; border: 1px solid rgba(212,175,55,0.4);
      border-radius: 8px; padding: 10px 20px;
      font-weight: 600; cursor: pointer; font-size: 0.9rem;
  ">⏹ Stop</button>
  <p id="statusLabel" style="color:#c4b595; font-size:0.85rem; margin-top:12px;"></p>
  <textarea id="resultBox" rows="3" style="
    width:100%; background:rgba(15,10,5,0.7); color:#f3ecd8;
    border:1px solid rgba(212,175,55,0.3); border-radius:8px;
    padding:10px; font-size:0.95rem; margin-top:8px; resize:none;
    font-family: 'Plus Jakarta Sans', sans-serif;
  " placeholder="Recognised speech will appear here…"></textarea>
  <button onclick="copyToClipboard()" style="
    margin-top:10px;
    background: rgba(60,40,20,0.7); color:#e5c98b;
    border: 1px solid rgba(212,175,55,0.4); border-radius: 8px;
    padding: 8px 18px; cursor: pointer; font-size: 0.85rem;
  ">📋 Copy Text</button>
</div>

<script>
var recognition = null;
function startListening() {
  var SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (!SpeechRecognition) {
    document.getElementById('statusLabel').innerText = '❌ Speech Recognition not supported in this browser. Try Chrome.';
    return;
  }
  recognition = new SpeechRecognition();
  recognition.continuous = true;
  recognition.interimResults = true;
  recognition.lang = 'en-US';
  document.getElementById('statusLabel').innerText = '🔴 Listening…';
  recognition.onresult = function(event) {
    var transcript = '';
    for (var i = event.resultIndex; i < event.results.length; i++) {
      transcript += event.results[i][0].transcript;
    }
    document.getElementById('resultBox').value = transcript;
  };
  recognition.onerror = function(event) {
    document.getElementById('statusLabel').innerText = '⚠️ Error: ' + event.error;
  };
  recognition.onend = function() {
    document.getElementById('statusLabel').innerText = '✅ Done. Copy the text and paste it into the chat.';
  };
  recognition.start();
}
function stopListening() {
  if (recognition) { recognition.stop(); }
}
function copyToClipboard() {
  var tb = document.getElementById('resultBox');
  tb.select();
  document.execCommand('copy');
  document.getElementById('statusLabel').innerText = '✅ Copied to clipboard!';
}
</script>
"""

# ── TTS ───────────────────────────────────────────────────────────────────────
def _tts_script(text: str, lang: str = "en-US") -> str:
    safe = text.replace("'", "\\'").replace("\n", " ").replace('"', '\\"')
    return f"""
<script>
(function() {{
  var u = new SpeechSynthesisUtterance('{safe}');
  u.lang = '{lang}';
  u.rate = 0.95;
  u.pitch = 1.0;
  window.speechSynthesis.speak(u);
}})();
</script>
"""


def render():
    """Render the Voice Features panel: Speech-to-Text + Text-to-Speech."""
    st.markdown("### 🎙️ Voice-Enabled Conversations")
    st.caption("Use your microphone to ask questions by voice, or listen to AI responses read aloud.")

    col1, col2 = st.columns([1, 1])

    with col1:
        st.markdown("#### 🎤 Speech → Text")
        components.html(_STT_SCRIPT, height=280, scrolling=False)
        st.info("💡 Tip: Click **Start Listening**, speak your question, then **Copy Text** and paste it into any chat input box.")

    with col2:
        st.markdown("#### 🔊 Text → Speech (TTS)")
        tts_text = st.text_area(
            "Enter text to read aloud",
            value=st.session_state.get("last_response", "")[:500] if st.session_state.get("last_response") else "",
            height=130,
            key="tts_input"
        )
        lang_map = {
            "English (US)": "en-US",
            "English (UK)": "en-GB",
            "Hindi": "hi-IN",
            "Spanish": "es-ES",
            "French": "fr-FR",
            "German": "de-DE",
            "Chinese": "zh-CN",
        }
        tts_lang_label = st.selectbox("TTS Language", list(lang_map.keys()), key="tts_lang_sel")
        tts_lang = lang_map[tts_lang_label]

        if st.button("▶️ Speak Now", use_container_width=True, key="tts_speak_btn"):
            if tts_text.strip():
                components.html(_tts_script(tts_text, tts_lang), height=0)
                st.success("🔊 Speaking…")
            else:
                st.warning("Enter some text first.")

        if st.button("⏹ Stop Speech", use_container_width=True, key="tts_stop_btn"):
            components.html("<script>window.speechSynthesis.cancel();</script>", height=0)

    st.markdown("---")
    st.markdown("""
    <div style='
        background: rgba(20,14,8,0.7);
        border: 1px solid rgba(212,175,55,0.25);
        border-radius: 10px; padding: 14px 18px;
        color: #c4b595; font-size: 0.88rem;
    '>
    🌐 <strong>Browser Compatibility:</strong> Speech Recognition works best in <b>Google Chrome</b> and <b>Microsoft Edge</b>.
    Text-to-Speech works in all modern browsers. Safari has limited SpeechRecognition support.
    </div>
    """, unsafe_allow_html=True)
