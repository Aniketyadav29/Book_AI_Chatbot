"""
Streamlit Cloud Entrypoint for The Ancient Heritage Library & Book Intelligence
Redirects execution directly to app.py
"""
import sys
import runpy
from pathlib import Path

app_dir = Path(__file__).resolve().parent
if str(app_dir) not in sys.path:
    sys.path.insert(0, str(app_dir))

app_path = app_dir / "app.py"
runpy.run_path(str(app_path), run_name="__main__")

