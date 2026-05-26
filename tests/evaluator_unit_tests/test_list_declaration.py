from evaluator.helpers import Location, Graph
from parser.ast_builder import *
from evaluator.categories.list_declaration import execute_list_declaration
from typesystem.data_types import *

def make_declaration(identifiers: list[str], _type, is_list=False, dimension =None, token="Declaration"):
    declaration = Declaration(token)
    declaration.type = _type
    declaration.identifiers = identifiers
    declaration.is_list = is_list
    if dimension:
        declaration.dimension = Term("Term")
        declaration.dimension.type = TypeEnum.NAT
        declaration.dimension.value = dimension

    return declaration

def make_node_declaration(identifiers: list[str], is_list=False, dimension=None, token="NodeDecl"):
    declaration = NodeDecl(token)
    declaration.identifiers = identifiers
    declaration.is_list = is_list
    if dimension:
        declaration.dimension = Term("Term")
        declaration.dimension.type = TypeEnum.NAT
        declaration.dimension.value = dimension

    return declaration

### Declare lists ###

# Declare single-dimensional list of arithmetic data type
def test_nat_1d_list_declaration():
    # Arrange
    dec = make_declaration(["x"], TypeEnum.NAT, True)
    env_graph = dict()
    env_var = dict()
    env_algo = dict()
    loc = Location()
    graph_object = Graph()
    store = dict()

    # Act
    ret = execute_list_declaration(dec, env_graph, env_var, env_algo, loc, graph_object, store)
    actual_type = ret.store.get(ret.env_var.get("x"))
    expected_type = list

    # Assert
    assert ret.env_var.get("x")
    assert isinstance(actual_type, expected_type)
    assert len(ret.store.get(ret.env_var.get("x"))) == 0

# Declare multi-dimensional list of arithmetic data type
def test_real_2d_list_declaration():
    # Arrange
    dec = make_declaration(["x"], TypeEnum.REAL, True, 2)
    env_graph = dict()
    env_var = dict()
    env_algo = dict()
    loc = Location()
    graph_object = Graph()
    store = dict()

    # Act
    ret = execute_list_declaration(dec, env_graph, env_var, env_algo, loc, graph_object, store)
    actual_type = ret.store.get(ret.env_var.get("x"))
    expected_type = list

    # Assert
    assert ret.env_var.get("x")
    assert isinstance(actual_type, expected_type)
    assert len(ret.store.get(ret.env_var.get("x"))[0]) == 0

# Declare single-dimensional list of other data type
def test_text_1d_list_declaration():
    # Arrange
    dec = make_declaration(["x"], TypeEnum.TEXT, True)
    env_graph = dict()
    env_var = dict()
    env_algo = dict()
    loc = Location()
    graph_object = Graph()
    store = dict()

    # Act
    ret = execute_list_declaration(dec, env_graph, env_var, env_algo, loc, graph_object, store)
    actual_type = ret.store.get(ret.env_var.get("x"))
    expected_type = list

    # Assert
    assert ret.env_var.get("x")
    assert isinstance(actual_type, expected_type)
    assert len(ret.store.get(ret.env_var.get("x"))) == 0

# Declare multi-dimensional list of other data type
def test_node_4d_list_declaration():
    # Arrange
    dec = make_node_declaration(["x"], True, 4)
    env_graph = dict()
    env_var = dict()
    env_algo = dict()
    loc = Location()
    graph_object = Graph()
    store = dict()

    # Act
    ret = execute_list_declaration(dec, env_graph, env_var, env_algo, loc, graph_object, store)
    actual_type = ret.store.get(ret.env_var.get("x"))
    expected_type = list

    # Assert
    assert ret.env_var.get("x")
    assert isinstance(actual_type, expected_type)
    assert len(ret.store.get(ret.env_var.get("x"))[0][0][0]) == 0