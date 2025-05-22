# dfa_place_finder/dfa.py
from __future__ import annotations
import string


class DFA:
    """Deterministic Finite Automaton implemented as a character-trie."""

    class _Node:
        __slots__ = ("children", "is_final")

        def __init__(self):
            self.children: dict[str, DFA._Node] = {}
            self.is_final = False

    def __init__(self) -> None:
        self._root = self._Node()
        self._trap_node = self._Node()

    def insert(self, word: str) -> None:
        node = self._root
        for ch in word:
            node = node.children.setdefault(ch, self._Node())
        node.is_final = True

    def accepts(self, text: str) -> bool:
        node = self._root
        for ch in text:
            if ch in string.punctuation:
                continue
            if ch not in node.children:
                node = self._trap_node
                break
            else:
                node = node.children[ch]
        if node == self._trap_node:
            return False
        return node.is_final

    def to_dot(self) -> str:
        """
        Emit a GraphViz DOT string for this DFA.  States are
        numbered internally; accepting states get double circles.
        """
        from collections import deque

        # assign unique IDs to nodes
        node_ids: dict[DFA._Node, str] = {}
        def get_id(n: DFA._Node) -> str:
            if n not in node_ids:
                node_ids[n] = f"Q{len(node_ids)}"
            return node_ids[n]

        lines = [
            "digraph DFA {",
            "  rankdir=LR;",
            # background color:
            "  graph [bgcolor=\"#131a2e\"];",
            "  node [shape=circle, style=filled, fillcolor=\"#103c69\", color=\"#2B65EC\", fontcolor=\"white\", fontname=\"Courier\"];"
            "  edge [fontcolor=\"#00f7ff\", color=\"#00f7ff\", fontname=\"Courier\"];"
        ]

        # mark a start arrow (invisible node)
        lines.append("  __start__ [shape=none,label=\"\"];")
        root_id = get_id(self._root)
        lines.append(f"  __start__ -> {root_id};")

        # BFS through the trie graph
        queue = deque([self._root])
        seen = {self._root}
        while queue:
            node = queue.popleft()
            nid = get_id(node)
            
            # if this is a final (accepting) state, use doublecircle
            if node.is_final:
                lines.append(f"  {nid} [shape=doublecircle, style=filled, fillcolor=\"#66CC66\", color=\"#339933\", fontcolor=\"white\"];")
                
            for ch, child in node.children.items():
                cid = get_id(child)
                # escape quotes and backslashes in the label
                label = ch.replace("\\", "\\\\").replace("\"", "\\\"")
                lines.append(f"  {nid} -> {cid} [label=\"{label}\"];")
                if child not in seen:
                    seen.add(child)
                    queue.append(child)

        lines.append("}")
        return "\n".join(lines)
