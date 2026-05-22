class PreprocessorException(Exception):
    def __init__(self, message: str, span: list):
        super().__init__(message)

        self.message = message
        self.span = span