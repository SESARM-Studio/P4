from copy import copy, deepcopy
import networkx as nx

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
        edge = [src, dst, weight]
        self.graph.add_weighted_edges_from(edge)
    
    def add_weighted_edges(self, edges):
        self.graph.add_weighted_edges_from(edges)

    def remove_node(self, node):
        self.graph.remove_node(node)
    
    def remove_edge(self, src, dst):
        self.graph.remove_edge(src, dst)

    def get_nodes(self):
        return self.graph.nodes
    
    def get_edges(self):
        return self.graph.edges
    
    def get_edge_data(self, src, dst):
        return self.graph.get_edge_data(src, dst)

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