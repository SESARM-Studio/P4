from dataclasses import dataclass
from copy import copy

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

    def copy(self):
        return copy(self)

class Graph:
    def copy(self):
        return copy(self)


@dataclass(init=True)
class State:
    env_graph: dict
    env_var: dict
    env_algo: dict
    loc: Location
    graph_object: Graph
    store: dict

