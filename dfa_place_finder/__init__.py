# dfa_place_finder/__init__.py
"""
Public re-exports so *app.py* can simply do:

    from dfa_highlighter import build_dfa, scan_paragraph
"""
from .processor import build_dfa, scan_paragraph
from .dfa import DFA

__all__ = ["build_dfa", "scan_paragraph", "DFA"]
