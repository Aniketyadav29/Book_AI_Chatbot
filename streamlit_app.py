"""
Streamlit Cloud Entrypoint for The Ancient Heritage Library & Book Intelligence
Directs execution to book-ai-chatbot-main/app.py
"""
import sys
import runpy
from pathlib import Path

# Ensure book-ai-chatbot-main is in sys.path
inner_dir = Path(__file__).resolve().parent / "book-ai-chatbot-main"
if str(inner_dir) not in sys.path:
    sys.path.insert(0, str(inner_dir))

app_path = inner_dir / "app.py"
runpy.run_path(str(app_path), run_name="__main__")
