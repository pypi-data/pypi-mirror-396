"""CLI entry point for baicai-webui."""

import sys
from pathlib import Path


def main() -> None:
    """Main entry point for baicai-webui command."""
    import subprocess

    # Get the path to app.py
    app_path = Path(__file__).parent / "app.py"
    
    # Run streamlit
    cmd = [sys.executable, "-m", "streamlit", "run", str(app_path)]
    
    # Pass through any command line arguments
    cmd.extend(sys.argv[1:])
    
    subprocess.run(cmd)

