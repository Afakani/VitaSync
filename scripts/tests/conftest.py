"""Macht die Skripte aus scripts/ fuer die Tests importierbar."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
