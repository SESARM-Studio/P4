class ASTNode:
    def __init__(self, kind, children=None, value=None):
        self.kind = kind
        self.value = value
        self.children = children or []
        self.parent = None

        for c in self.children:
            c.parent = self

    def add(self, child):
        child.parent = self
        self.children.append(child)


def print_ast(node, prefix="", is_last=True):
    connector = "└── " if is_last else "├── "

    # label shown
    label = node.kind
    if node.value is not None:
        label += f" ({node.value})"

    print(prefix + connector + label)

    new_prefix = prefix + ("    " if is_last else "│   ")

    for i, child in enumerate(node.children):
        last = i == len(node.children) - 1
        print_ast(child, new_prefix, last)