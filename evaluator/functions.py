class Location:
    def __init__(self):
        self.number = 0
        self.name = f"l{self.number}"

    def __repr__(self):
        return f"{self.name}"

    def next_location(self):
        l = Location()
        l.number = self.number + 1
        l.name = f"l{l.number}"
        return l

class Graph:
    pass
