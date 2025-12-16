from graphviz import Digraph
import html
from collections import defaultdict


class TrieNode:
    def __init__(self):
        self.children = {}
        self.edge_counts = defaultdict(int)
        self.is_end_of_word = False
        self.count = 0


class Trie:
    def __init__(self):
        self.root = TrieNode()

    def insert(self, text: str) -> None:
        node = self.root
        node.count += 1
        for char in text:
            if char not in node.children:
                node.children[char] = TrieNode()
            node.edge_counts[char] += 1
            node = node.children[char]
            node.count += 1
        node.is_end_of_word = True

    def minimize(self) -> 'Trie':
        """
        Minimize the trie using the Hopcroft algorithm.
        Returns a new minimized Trie (DAWG - Directed Acyclic Word Graph).
        """
        # Build equivalence classes using signatures (bottom-up approach)
        signature_to_node: dict[tuple, TrieNode] = {}

        def minimize_node(node: TrieNode) -> TrieNode:
            """
            Recursively minimize a node by replacing children with
            equivalent nodes if they exist.
            """
            # First, minimize all children
            minimized_children = {}
            edge_counts = {}
            for char, child in node.children.items():
                minimized_children[char] = minimize_node(child)
                edge_counts[char] = node.edge_counts[char]

            # Create signature for this node with minimized children
            children_sig = tuple(
                (char, id(child))
                for char, child in sorted(minimized_children.items())
            )
            signature = (node.is_end_of_word, children_sig)

            # Check if we already have an equivalent node
            if signature in signature_to_node:
                # Add count to existing node
                existing = signature_to_node[signature]
                existing.count += node.count
                for char, count in edge_counts.items():
                    existing.edge_counts[char] += count
                return existing

            # Create new minimized node
            new_node = TrieNode()
            new_node.is_end_of_word = node.is_end_of_word
            new_node.count = node.count
            new_node.children = minimized_children
            new_node.edge_counts = defaultdict(int, edge_counts)

            signature_to_node[signature] = new_node
            return new_node

        # Create new minimized trie
        minimized_trie = Trie()
        minimized_trie.root = minimize_node(self.root)

        return minimized_trie


    def as_dot(self) -> Digraph:
        dot = Digraph('Trie')
        node_to_id: dict[int, int] = {}  # Maps node object id to graph node id
        next_id = [0]

        def escape_label(char: str) -> str:
            """Escape special characters for Graphviz HTML labels."""
            if char == ' ':
                return "' '"
            if char == '\n':
                return '\\n'
            if char == '\r':
                return '\\r'
            if char == '\t':
                return '\\t'
            return html.escape(char)

        def format_count(value: int) -> str:
            """Format counts; switch to default scientific notation above 999."""
            if value <= 999:
                return str(value)
            return f"{value:.3e}"

        dot.attr(
            "node",
            fontname="JetBrainsMono Nerd Font",
            shape="ellipse",
            fixedsize="true",
            height="0.16",
        )

        dot.attr(
            "edge",
            fontname="JetBrainsMono Nerd Font",
            fontsize="8",
            penwidth="0.1",
            arrowsize="0.3",
        )

        def get_or_create_node_id(node: TrieNode) -> tuple[int, bool]:
            """
            Get existing node ID or create a new one.
            Returns (node_id, is_new).
            """
            obj_id = id(node)
            if obj_id in node_to_id:
                return node_to_id[obj_id], False
            
            node_id = next_id[0]
            next_id[0] += 1
            node_to_id[obj_id] = node_id
            return node_id, True

        def _build(node: TrieNode, node_id: int) -> None:
            if node_id == 0:
                attrs = {
                    "label": "",
                    "style": "filled",
                    "fillcolor": "gray",
                }
            else:
                attrs = {
                    "label": f"<<font point-size=\"6\" color=\"dimgray\">{format_count(node.count)}</font>>",
                }
            if node.is_end_of_word:
                attrs["peripheries"] = "2"
            dot.node(str(node_id), **attrs)

            for char, child in node.children.items():
                child_id, is_new = get_or_create_node_id(child)
                escaped_label = escape_label(char)
                dot.edge(
                    str(node_id),
                    str(child_id),
                    label=(
                        f"<<font>{escaped_label}</font>"
                        f"<font point-size=\"6\" color=\"dimgray\">({format_count(node.edge_counts[char])})</font>>"
                    ),
                )
                if is_new:
                    _build(child, child_id)

        root_id, _ = get_or_create_node_id(self.root)
        _build(self.root, root_id)
        return dot
