from pathlib import Path

__version__ = (Path(__file__).resolve().parent/"VERSION").read_text().strip()