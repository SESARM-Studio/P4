from copy import copy, deepcopy
import networkx as nx

class Location:
    def __init__(self):
        self.number = 0
        self.name = f"l{self.number}"

    def __repr__(self):
        return f"{self.name}"

    def __eq__(self, other):
        return (isinstance(other, type(self)) and (self.number, self.name) == (other.number, other.name))

    def __hash__(self):
        return hash((self.number, self.name))

    def next_location(self):
        l = Location()
        l.number = self.number + 1
        l.name = f"l{l.number}"
        return l

    def copy(self):
        return copy(self)

class Graph:

    def __init__(self):
        self.graph = None

    def create_graph(self, type):
        if type == "digraph":
            self.graph = nx.DiGraph()
        else:
            self.graph = nx.Graph()
    
    def add_node(self, node):
        self.graph.add_node(node)

    def add_nodes(self, nodes):
        self.graph.add_nodes_from(nodes)

    def add_edge(self, src, dst):
        self.graph.add_edge(src, dst)
    
    def add_edges(self, edges):
        self.graph.add_edges_from(edges)

    def add_weighted_edge(self, src, dst, weight):
        edge = [(src, dst, weight)]
        self.graph.add_weighted_edges_from(edge)
    
    def add_weighted_edges(self, edges):
        self.graph.add_weighted_edges_from(edges)

    def add_attribute(self, node, attribute):
        self.graph.nodes[node][attribute] = None

    def remove_node(self, node):
        self.graph.remove_node(node)
    
    def remove_edge(self, src, dst):
        self.graph.remove_edge(src, dst)
    
    def clear_edges(self):
        return self.graph.clear_edges()

    def get_nodes(self):
        return self.graph.nodes
    
    def get_edges(self):
        return self.graph.edges
    
    def get_edge_data(self, src, dst):
        return self.graph.get_edge_data(src, dst)
    
    def get_node_data(self, node, data):
        return self.graph.nodes[node][data]

    def copy(self):
        return deepcopy(self)

def create_dimensional_array(dim, arr=None):
    if dim < 1:
        return

    if arr is None:
        arr = []

    if dim == 1:
        return arr

    arr.append(create_dimensional_array(dim - 1, []))
    return arr

def assign_nested_attribute(target, path, value):
    """
    Assign value to a nested attribute path.

    Example:
        target = x
        path = ["a", "b", "c"]

    Means:
        x.a.b.c := value
    """

    if not path:
        raise RuntimeError("Missing attribute path")

    current_key = path[0]

    # Base case: final attribute
    if len(path) == 1:
        if isinstance(target, dict):
            target[current_key] = value
        else:
            setattr(target, current_key, value)
        return

    # Recursive case: move deeper
    if isinstance(target, dict):
        if current_key not in target:
            raise RuntimeError(f"Unknown attribute: {current_key}")
        next_target = target[current_key]
    else:
        if not hasattr(target, current_key):
            raise RuntimeError(f"Unknown attribute: {current_key}")
        next_target = getattr(target, current_key)

    assign_nested_attribute(next_target, path[1:], value)