"""Compatibility entry point for the scoped record synchronizer.

The former global replacements could corrupt Organization URLs and rewrite
unrelated game records. Current facts are maintained in identity.json.
"""
from pathlib import Path
import runpy

runpy.run_path(str(Path(__file__).with_name("sync_linkedin_records.py")), run_name="__main__")
