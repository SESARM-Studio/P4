class ParseException(Exception):

    def __init__(self, b, e, s, o, x):
        self.begin = b
        self.end = e
        self.state = s
        self.offending = o
        self.expected = x

    def error(self):
        if self.offending < 0:
            return "Lexical analysis failed"
        else:
            return "Syntax error"

    def serialize(self, eventHandler):
        pass

    def getBegin(self):
        return self.begin

    def getEnd(self):
        return self.end

    def getState(self):
        return self.state

    def getOffending(self):
        return self.offending

    def getExpected(self):
        return self.expected

    def isAmbiguousInput(self):
        return False