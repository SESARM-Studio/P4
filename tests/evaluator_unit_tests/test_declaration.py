from evaluator.functions import Location, Graph
from parser.ast_builder import *
from evaluator.categories.declaration import execute_declaration
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
        declaration.dimension.type = 'NATURAL_NUMBER'
        declaration.dimension.value = dimension

    return declaration

#### Declare arithmetic data types #### (D1)
# Declare int
def test_int_declaration():
    # Arrange
    dec = make_declaration(["x", "y"], TypeEnum.INT)
    env_graph = dict()
    env_var = dict()
    env_algo = dict()
    loc = Location()
    graph_object = Graph()
    store = dict()

    # Act
    ret = execute_declaration(dec, env_graph, env_var, env_algo, loc, graph_object, store)

    # Assert
    assert ret.env_var.get("x") and ret.env_var.get("y")
    assert ret.env_var.get("x") != ret.env_var.get("y")
    assert ret.store.get(ret.env_var.get("x")) == 0 and ret.store.get(ret.env_var.get("y")) == 0

# Declare nat
def test_nat_declaration():
    # Arrange
    dec = make_declaration(["x", "y"], TypeEnum.NAT)
    env_graph = dict()
    env_var = dict()
    env_algo = dict()
    loc = Location()
    graph_object = Graph()
    store = dict()

    # Act
    ret = execute_declaration(dec, env_graph, env_var, env_algo, loc, graph_object, store)

    # Assert
    assert ret.env_var.get("x") and ret.env_var.get("y")
    assert ret.env_var.get("x") != ret.env_var.get("y")
    assert ret.store.get(ret.env_var.get("x")) == 0 and ret.store.get(ret.env_var.get("y")) == 0

# Declare real
def test_real_declaration():
    # Arrange
    dec = make_declaration(["x", "y"], TypeEnum.REAL)
    env_graph = dict()
    env_var = dict()
    env_algo = dict()
    loc = Location()
    graph_object = Graph()
    store = dict()

    # Act
    ret = execute_declaration(dec, env_graph, env_var, env_algo, loc, graph_object, store)

    # Assert
    assert ret.env_var.get("x") and ret.env_var.get("y")
    assert ret.env_var.get("x") != ret.env_var.get("y")
    assert ret.store.get(ret.env_var.get("x")) == 0 and ret.store.get(ret.env_var.get("y")) == 0

#### Declare other types #### (D2)

# Declare text
def test_text_declaration():
    # Arrange
    dec = make_declaration(["x", "y"], TypeEnum.TEXT)
    env_graph = dict()
    env_var = dict()
    env_algo = dict()
    loc = Location()
    graph_object = Graph()
    store = dict()

    # Act
    ret = execute_declaration(dec, env_graph, env_var, env_algo, loc, graph_object, store)

    # Assert
    assert ret.env_var.get("x") and ret.env_var.get("y")
    assert ret.env_var.get("x") != ret.env_var.get("y")
    assert len(ret.store) == 0

# Declare bool
def test_bool_declaration():
    # Arrange
    dec = make_declaration(["x", "y"], TypeEnum.BOOL)
    env_graph = dict()
    env_var = dict()
    env_algo = dict()
    loc = Location()
    graph_object = Graph()
    store = dict()

    # Act
    ret = execute_declaration(dec, env_graph, env_var, env_algo, loc, graph_object, store)

    # Assert
    assert ret.env_var.get("x") and ret.env_var.get("y")
    assert ret.env_var.get("x") != ret.env_var.get("y")
    assert len(ret.store) == 0

# Declare node

def test_node_declaration():
    # Arrange
    dec = make_node_declaration(["x", "y"])
    env_graph = dict()
    env_var = dict()
    env_algo = dict()
    loc = Location()
    graph_object = Graph()
    store = dict()

    # Act
    ret = execute_declaration(dec, env_graph, env_var, env_algo, loc, graph_object, store)

    # Assert
    assert ret.env_var.get("x") and ret.env_var.get("y")
    assert ret.env_var.get("x") != ret.env_var.get("y")
    assert len(ret.store) == 0

# Declare node in graph (D2NODE)

def test_node_in_graph_declaration():
    # Arrange
    dec = make_node_declaration(["x", "y"])
    env_var = dict()
    env_algo = dict()
    loc = Location()
    graph_object = Graph()
    graph_object.create_graph("graph")
    env_graph = dict()
    env_graph.update({"g": graph_object})
    store = dict()

    # Act
    ret = execute_declaration(dec, env_graph, env_var, env_algo, loc, graph_object, store)

    # Assert
    assert len(ret.env_var) == 0
    assert 'x' in env_graph.get("g").get_nodes()
    assert 'y' in env_graph.get("g").get_nodes()

### Declare lists ###

# Declare single-dimensional list of arithmetic data type
def test_int_1d_list_declaration():
    # Arrange
    dec = make_declaration(["x"], TypeEnum.INT, True)
    env_graph = dict()
    env_var = dict()
    env_algo = dict()
    loc = Location()
    graph_object = Graph()
    store = dict()

    # Act
    ret = execute_declaration(dec, env_graph, env_var, env_algo, loc, graph_object, store)
    actual_type = ret.store.get(ret.env_var.get("x"))
    expected_type = list

    # Assert
    assert ret.env_var.get("x")
    assert isinstance(actual_type, expected_type)
    assert len(ret.store.get(ret.env_var.get("x"))) == 0

# Declare multi-dimensional list of arithmetic data type
def test_int_3d_list_declaration():
    # Arrange
    dec = make_declaration(["x"], TypeEnum.INT, True, 3)
    env_graph = dict()
    env_var = dict()
    env_algo = dict()
    loc = Location()
    graph_object = Graph()
    store = dict()

    # Act
    ret = execute_declaration(dec, env_graph, env_var, env_algo, loc, graph_object, store)
    actual_type = ret.store.get(ret.env_var.get("x"))
    expected_type = list

    # Assert
    assert ret.env_var.get("x")
    assert isinstance(actual_type, expected_type)
    assert len(ret.store.get(ret.env_var.get("x"))[0][0]) == 0

# Declare single-dimensional list of other data type
def test_node_1d_list_declaration():
    # Arrange
    dec = make_node_declaration(["x"], True)
    env_graph = dict()
    env_var = dict()
    env_algo = dict()
    loc = Location()
    graph_object = Graph()
    store = dict()

    # Act
    ret = execute_declaration(dec, env_graph, env_var, env_algo, loc, graph_object, store)
    actual_type = ret.store.get(ret.env_var.get("x"))
    expected_type = list

    # Assert
    assert ret.env_var.get("x")
    assert isinstance(actual_type, expected_type)
    assert len(ret.store.get(ret.env_var.get("x"))) == 0

# Declare multi-dimensional list of other data type
def test_text_3d_list_declaration():
    # Arrange
    dec = make_declaration(["x"], TypeEnum.TEXT, True, 3)
    env_graph = dict()
    env_var = dict()
    env_algo = dict()
    loc = Location()
    graph_object = Graph()
    store = dict()

    # Act
    ret = execute_declaration(dec, env_graph, env_var, env_algo, loc, graph_object, store)
    actual_type = ret.store.get(ret.env_var.get("x"))
    expected_type = list

    # Assert
    assert ret.env_var.get("x")
    assert isinstance(actual_type, expected_type)
    assert len(ret.store.get(ret.env_var.get("x"))[0][0]) == 0
