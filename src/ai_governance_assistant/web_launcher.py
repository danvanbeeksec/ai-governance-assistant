"""Launch the optional Streamlit demonstration through its console script."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def format_tier(value: str) -> str:
    return value.replace("_", " ").title()


def main() -> None:
    app = Path(__file__).with_name("web.py")
    raise SystemExit(
        subprocess.call([sys.executable, "-m", "streamlit", "run", str(app), *sys.argv[1:]])
    )
