#
#   Imandra Inc.
#
#   help.py
#
from pathlib import Path
from functools import partial

from rich.style import Style
from rich.text import Text

from textual.screen import Screen
from textual.widgets import Footer, Markdown, Tree, Static
from textual.containers import Horizontal, VerticalScroll

from codelogician.util import maybe, snd
from codelogician.doc.utils.docs import flatten_docs, walk_directory
from ..common import MyHeader


TOGGLE_STYLE = Style.from_meta({"toggle": True})

class TOC(Tree):
    def __init__(self, nodes):
        Tree.__init__(self, "Code Logician Help")

        def add_children(node, sub_nodes):
            for n in sub_nodes: add_subtree(node, n)

        def add_subtree(dest, src_node):
            kind, data = src_node
            if kind == 'leaf':
                _, doc = data
                dest.add_leaf(snd(data).title, data=data)
            else:
                data, sub_nodes = data
                add_children(dest.add(snd(data).title, data=data), sub_nodes)

        self.root.expand()
        add_children(self.root, nodes)

    def render_label(self, node, base_style, style):
        node_label = node._label.copy()
        node_label.stylize(style)

        def toggled_icon():
            icon = self.ICON_NODE_EXPANDED if node.is_expanded else self.ICON_NODE
            return icon, base_style + TOGGLE_STYLE

        prefix = toggled_icon() if node._allow_expand else ("", base_style)
        return Text.assemble(prefix, node_label)


def code_block(lang, code):
    return f'```{lang}\n{code}\n```\n'

def fix_code_blocks(s): return s.replace("```iml", "```ocaml")

content_wrappers = {
    '': fix_code_blocks,
    '.md': fix_code_blocks,
    '.iml': partial(code_block,'ocaml'),
    '.py': partial(code_block, 'python')
}

class HelpScreen(Screen):
    DEFAULT_CSS = "TOC { width: 25% } VerticalScroll { width: 75% }"

    def __init__(self):
        Screen.__init__(self)
        self.title = "Help"

    def compose(self):
        doc_path = Path(__file__).parent / "../../doc/data"
        nodes = walk_directory(doc_path.resolve())

        yield MyHeader()
        with Horizontal() as h:
            yield TOC(nodes)
            with VerticalScroll():
                markdown = Markdown("# Code Logician\nClick the tree to read the docs.", id="content")
                # markdown.code_indent_guides = False
                yield markdown
        yield Footer()

    def on_tree_node_selected(self, event):
        def select_node(node_data):
            path, doc = node_data
            content = content_wrappers[Path(path).suffix](doc.content)
            text = f'# {doc.order}: {doc.title}\n{content}'
            self.query_one("#content").update(text)

        maybe(select_node, event.node.data)
