class TypeCheckError(Exception):

    """
    Custom exception to make debugging of the type system easier

    Prints the function from which the type error occured
    """

    def __init__(self, type_rule, span: list, expected=None, actual=None):
        self.type_rule = type_rule
        self.span = span
        self.expected = expected
        self.actual = actual

    def __str__(self):
        type_rule_function_name = self.type_rule.__name__
        return f"[{type_rule_function_name}] expected: {self.expected}, got: {self.actual}"
