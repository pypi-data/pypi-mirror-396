from IPython.display import Markdown, display
from langgraph.graph.state import CompiledStateGraph


def ppc(code: str, ocaml=False):
    s = f"```ocaml\n{code}\n```" if ocaml else f"```python\n{code}\n```"
    display(Markdown(s))


def view_compiled_graph(app: CompiledStateGraph, xray=True):
    from IPython.display import Image, display

    try:
        display(Image(app.get_graph(xray=xray).draw_mermaid_png()))
    except Exception as e:
        print(f"Failed to display the compiled graph: {e}")


def ppm(messages: list | dict, truncate=False):
    """Pretty print message list"""
    if isinstance(messages, dict):
        messages = messages["messages"]
    for i, message in enumerate(messages):
        role = message.type.upper()
        title = f"{i}: {role}"
        print("+" + "-" * (len(title) + 2) + "+")
        print("| " + title + " |")
        print("+" + "-" * (len(title) + 2) + "+")
        content = message.content
        # collapse the content if it's too long
        if len(content) > 1000 and truncate:
            print(content[:1000])
            print()
            print("...content truncated...")
            print()
        else:
            print(content)
        print()
