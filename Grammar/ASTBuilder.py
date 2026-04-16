from tree import *

class AbstractSyntaxTreeBuilder:
    def __init__(self, input_string):
        self.input = input_string

    def buildTree(self, stack):
        root = stack[0]
        for symbol in root.children:
            print(symbol.getName())

    def characters(self, b, e):
        return self.input[b:e]

    # Can not be called on Terminals as they have no children
    def recBuilder(self, symbol):
        note_children = []
        for child in symbol.children:
            if not hasattr(child, "children"):
                if not (child.name in self.SKIP_WORDS):
                    note_children.append(ASTNode(child.name, [], self.characters(child.getBegin(), child.getEnd())))
            else:
                if len(symbol.children) == 1:
                    return self.recBuilder(child)
                note_children.append(self.recBuilder(child))
        return ASTNode(symbol.getName(), note_children)

    SKIP_WORDS = [
        "'('", "')'", "','"
    ]