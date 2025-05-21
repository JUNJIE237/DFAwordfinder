# dfa_place_finder/processor.py
"""
High-level operations:

• build_dfa()              → ready-made DFA instance + max phrase length
• scan_paragraph(text, dfa, paragraph_max_len)
      returns (verdicts, bold_markdown)
"""

from __future__ import annotations

import re
from typing import List, Tuple

from .dfa import DFA
from .phrases import ACCEPTED_PHRASES
from .utils import strip_outer_punct, longest_phrase_len


# ------------------------------------------------------------------ #
#  (1) build_dfa  – called once, can be cached by Streamlit
# ------------------------------------------------------------------ #
def build_dfa() -> tuple[DFA, int]:
    dfa = DFA()
    for phrase in ACCEPTED_PHRASES:
        dfa.insert(phrase)
    return dfa, longest_phrase_len(ACCEPTED_PHRASES)


# ------------------------------------------------------------------ #
#  (2) scan_paragraph
# ------------------------------------------------------------------ #
def scan_paragraph(
    paragraph: str, dfa: DFA, paragraph_max_len: int
) -> tuple[List[Tuple[str, bool]], str]:
    """
    Parameters
    ----------
    paragraph : raw user text
    dfa       : built DFA
    paragraph_max_len   : longest phrase length (in words)

    Returns
    -------
    verdicts        : list[(token|phrase, accepted?)]
    bold_paragraph  : the paragraph with accepted items **boldfaced**
                      (Markdown syntax, safe from nested bold)
    """
    # Tokenize the paragraphs
    tokens = [tok for word in paragraph.split() if (tok := strip_outer_punct(word))]

    verdicts: list[tuple[str, bool]] = []
    accepted_set: set[str] = set()

    i, tokens_len = 0, len(tokens)
    while i < tokens_len:
        match = None
        for L in range(min(paragraph_max_len, tokens_len - i), 0, -1):
            candidate = " ".join(tokens[i : i + L])
            if dfa.accepts(candidate):
                match = candidate
                break

        if match:
            verdicts.append((match, True))
            accepted_set.add(match)
            i += len(match.split())
        else:
            tok = tokens[i]
            is_accepted = dfa.accepts(tok)
            verdicts.append((tok, is_accepted))
            if is_accepted:
                accepted_set.add(tok)
            i += 1

    placeholders: dict[str, str] = {}
    bold_para = paragraph
    for idx, phrase in enumerate(sorted(accepted_set, key=len, reverse=True)):
        ph = f"\u0001{idx}\u0002"
        placeholders[ph] = f'<span style="background-color: #d1ffd1; color: green; font-weight: bold; border-radius: 4px; padding: 2px 4px">{phrase}</span>'
        pattern = re.compile(rf"(?<!\w)({re.escape(phrase)})(?!\w)")
        bold_para = pattern.sub(ph, bold_para)

    for ph, boldver in placeholders.items():
        bold_para = bold_para.replace(ph, boldver)

    return verdicts, bold_para
