class ASTNode:
    def __init__(self, kind, children=None, value=None):
        self.kind = kind
        self.value = value
        self.children = children or []
        self.parent = None

        for c in self.children:
            c.parent = self

    # def add(self, child):
    #     child.parent = self
    #     self.children.append(child)


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



class AbstractSyntaxTreeBuilder:
    def __init__(self, input_string):
        self.input = input_string

    def build_tree(self, stack):
        root = stack[0]
        return self.recursive_builder(root)

    def characters(self, b, e):
        return self.input[b:e]


    def recursive_builder(self, symbol):
        symbol_children = []
        accepted_children = []

        if hasattr(symbol, "children") is False:
            return ASTNode(symbol.name, [], self.characters(symbol.getBegin(), symbol.getEnd()))

        for child in symbol.children:
            if child.name not in self.SKIP_WORDS:
                symbol_children.append(child)

        for child in symbol_children:
            if len(symbol_children) == 1:
                return self.recursive_builder(child)
            accepted_children.append(self.recursive_builder(child))

        return ASTNode(symbol.getName(), accepted_children)


    SKIP_WORDS = [
        "'('", "')'", "','"
    ]