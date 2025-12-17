"""Fiddler SDK for instrumenting GenAI Applications."""

from pathlib import Path

from fiddler_langgraph.core.client import FiddlerClient

# Read version from VERSION file
_version_file = Path(__file__).parent / 'VERSION'
__version__ = _version_file.read_text().strip()

__all__ = ['FiddlerClient', '__version__']
