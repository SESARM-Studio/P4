from copy import copy, deepcopy
import networkx as nx

class Location:
    def __init__(self):
        self.number = 0
        self.name = f"l{self.number}"


    def __repr__(self):
        """Return a readable string representation rather than a memory address, for debugging."""
        return f"{self.name}"

    def __eq__(self, other):
        """Compare objects based on their contents instead of memory address - so a copy of a location
        will evaluate as equal to the original."""
        return (isinstance(other, type(self)) and (self.number, self.name) == (other.number, other.name))

    def __hash__(self):
        """Return a hash value so equal objects can be found correctly in sets and dictionaries."""
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
    
    def add_node(self, new_node):
        if len(self.graph.nodes) > 0: # If graph has nodes
            created_graph_node_attributes = self.graph.nodes[next(iter(self.graph.nodes))] # Get attributes of the first node in graph since all nodes share same attributes
            if len(created_graph_node_attributes) == 0: # If nodes of the graph has no attributes
                self.graph.add_node(new_node)
            else:
                attributes = dict()
                for key in created_graph_node_attributes:
                    attributes.update({key: None}) # Create dictionary of nodes
                self.graph.add_node(new_node, **attributes) # **attributes unpacks the dictionary
        else: # If graph has no nodes
            self.graph.add_node(new_node)

    def add_nodes(self, new_nodes):
        if len(self.graph.nodes) > 0: # If graph has nodes
            created_graph_node_attributes = self.graph.nodes[next(iter(self.graph.nodes))] # Get attributes of the first node in graph since all nodes share same attributes
            if len(created_graph_node_attributes) == 0: # If nodes of the graph has no attributes
                self.graph.add_nodes_from(new_nodes)
            else:
                attributes = dict()
                for key in created_graph_node_attributes:
                    attributes.update({key: None}) # Create dictionary of nodes      
                self.graph.add_nodes_from(new_nodes, **attributes) # **attributes unpacks the dictionary
        else: # If graph has no nodes
            self.graph.add_nodes_from(new_nodes)

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