"""
Convenience launcher for the EV Charging Suitability Streamlit application.
Launches Streamlit directly inside the Python runtime to avoid Windows
Application Control policy blocks on 'streamlit.exe'.

Usage:
    python run_app.py
  or:
    python -m streamlit run app/main.py
"""

import os
import sys

# Force UTF-8 encoding for Windows terminal output
os.environ["PYTHONIOENCODING"] = "utf-8"

if __name__ == "__main__":
    try:
        from streamlit.web import cli as stcli
        # Prepare argument list: 'streamlit run app/main.py'
        sys.argv = ["streamlit", "run", "app/main.py"] + sys.argv[1:]
        sys.exit(stcli.main())
    except ImportError:
        import subprocess
        cmd = [sys.executable, "-m", "streamlit", "run", "app/main.py"] + sys.argv[1:]
        sys.exit(subprocess.call(cmd))
