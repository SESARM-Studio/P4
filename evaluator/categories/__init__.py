# Import all modules from the package
from .algorithm import execute_algorithm
from .declaration import execute_declaration
from .dimension import execute_dimension
from .edge_declaration import execute_edge_declaration
from .expression import execute_expression
from .graph_declaration import execute_graph_decl
from .graph_statement import execute_graph_statement
from .list_declaration import execute_list_declaration
from .node_expression import execute_node_expression
from .statement import execute_statement

# The __all__ array defines what is imported at a wildcard import:
# from evaluator.categories import *
__all__ = ["execute_algorithm",
           "execute_declaration",
           "execute_dimension",
           "execute_edge_declaration",
           "execute_expression",
           "execute_graph_decl",
           "execute_graph_statement",
           "execute_list_declaration",
           "execute_node_expression",
           "execute_statement"
           ]