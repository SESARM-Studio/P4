from enum import Enum # built in for enums

class TypeEnum(Enum):

    """Enum of the types from the abstract syntax"""

    UNKNOWN = 0
    BOOL    = 1
    TEXT    = 2
    NODE    = 3
    EDGE    = 4
    INT     = 5
    NAT     = 6
    REAL    = 7
    GRAPH   = 8
    DIGRAPH = 9
    TREE    = 10

TYPE_MAP = {
    "bool": TypeEnum.BOOL,
    "text": TypeEnum.TEXT,
    "node": TypeEnum.NODE,
    "edge": TypeEnum.EDGE,
    "int": TypeEnum.INT,
    "nat": TypeEnum.NAT,
    "real": TypeEnum.REAL,
    "graph": TypeEnum.GRAPH,
    "digraph": TypeEnum.DIGRAPH,
    "tree": TypeEnum.TREE
}

def resolve_type(type_name: str) -> TypeEnum:
    """Converts string representation of types to type"""
    try:
        return TYPE_MAP[type_name]
    except KeyError:
        return TypeEnum.UNKNOWN
