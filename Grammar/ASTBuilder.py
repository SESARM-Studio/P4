class ASTNode:
    def __init__(self, token, children=None, value=None):
        self.token = token
        self.value = value
        self.children = children or []
        self.parent = None

        for c in self.children:
            c.parent = self

def print_ast(node, prefix="", is_last=True):
    connector = "└── " if is_last else "├── "

    # label shown
    label = node.token
    if node.value is not None:
        label += f" ({node.value})"

    print(prefix + connector + label)

    new_prefix = prefix + ("    " if is_last else "│   ")

    for i, child in enumerate(node.children):
        last = i == len(node.children) - 1
        print_ast(child, new_prefix, last)


# Class for the abstract syntax
class AbstractSyntaxTreeBuilder:
    def __init__(self, input_string):
        self.input = input_string

    # After parsing completes successfully, the single remaining node in the stack is the non-terminal representing the start symbol.
    # Therefore, the AST is build on the single element in the stack.
    def build_tree(self, stack):
        if not stack:
            exit("Stack is empty")
        root = stack[0]
        return self.recursive_builder(root)

    # Splices the input_string from begin to end index, and returns that string.
    def characters(self, b, e):
        return self.input[b:e]
    
    # Recursive function, which builds the AST from last non-terminal of the stack, in the ASTNode format.
    def recursive_builder(self, symbol):
        symbol_children = []
        accepted_children = []

        # Base case: If symbol does not have attribute children, it is a terminal.
        if hasattr(symbol, "children") is False:
            return ASTNode(symbol.name, [], self.characters(symbol.getBegin(), symbol.getEnd()))

        # Creates a new array of the symbols children, and reduces redundant tokens.
        for child in symbol.children:
            if child.name not in self.SKIP_WORDS:
                symbol_children.append(child)

        if len(symbol_children) <= 0:
            exit("Error: Non-terminal has no children or they have all been terminated")

        if len(symbol_children) == 1:
            return self.recursive_builder(symbol_children[0])

        for child in symbol_children:
            accepted_children.append(self.recursive_builder(child))

        # Return the non-terminal as a ASTNode with the array of ASTNode children.
        return ASTNode(symbol.name, accepted_children)


    SKIP_WORDS = [
        "'('", "')'", "','"
    ]