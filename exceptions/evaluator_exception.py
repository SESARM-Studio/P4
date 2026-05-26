from parser.ast_builder import ASTNode
class EvaluatorException(Exception):
    def __init__(self, message: str, node: ASTNode):
        super().__init__(message)

        self.message = message
        self.span = node.span