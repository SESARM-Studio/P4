from typesystem.type_env import ScopedTypeEnvironment
from typesystem.data_types import TypeEnum

def test_scoped_type_env_binding_found_in_outer_scope():
    # Arrange
    expected = TypeEnum.REAL
    env = ScopedTypeEnvironment()

    # Act
    env.current_scope = env.current_scope.bind("weight_sum", TypeEnum.REAL)

    env = env.enter_scope()
    env.current_scope = env.current_scope.bind("new_sum", TypeEnum.REAL)
    env.current_scope = env.current_scope.bind("chromatic_color", TypeEnum.TEXT)
    env.current_scope = env.current_scope.bind("Trie", TypeEnum.TREE)

    actual = env.lookup("weight_sum")

    # Assert
    assert actual is not TypeEnum.UNKNOWN, "Binding not found"
    assert actual == expected, f"actual -> {actual.name} == {expected.name} <- expected"

def test_scoped_type_env_scope_destroyed():
    # Arrange
    expected = None
    env = ScopedTypeEnvironment()

    # Act
    env = env.enter_scope()
    env.current_scope = env.current_scope.bind("graph_num", TypeEnum.NAT)
    env = env.exit_scope()

    actual = env.lookup("graph_num")

    # Assert
    assert actual is TypeEnum.UNKNOWN, "Bindings in destroyed scope was not removed"

def test_scoped_type_env_variable_shadowed():
    # Arrange
    expected = TypeEnum.INT
    env = ScopedTypeEnvironment()

    # Act
    env.current_scope = env.current_scope.bind("node_num", TypeEnum.NAT)

    env = env.enter_scope()
    env.current_scope = env.current_scope.bind("node_num", TypeEnum.INT)

    actual = env.lookup("node_num")

    # Assert
    assert actual is not None, "Binding not found"
    assert actual == expected, f"actual -> {actual.name} == {expected.name} <- expected"

def test_scoped_type_env_shadowed_variable_restored():
    # Arrange
    expected = TypeEnum.NAT
    env = ScopedTypeEnvironment()

    # Act
    env = env.bind("node_num", TypeEnum.NAT)

    env = env.enter_scope()
    env = env.bind("node_num", TypeEnum.INT)

    env = env.exit_scope()

    actual = env.lookup("node_num")

    # Assert
    assert actual is not None, "Binding not found"
    assert actual == expected, f"actual -> {actual.name} == {expected.name} <- expected"

def test_scoped_type_env_static():
    # Arrange
    expected = TypeEnum.INT
    env = ScopedTypeEnvironment()

    # Act
    env = env.bind("node_num", TypeEnum.NAT)

    new_env = env.enter_scope()
    new_env = new_env.bind("node_num", TypeEnum.INT)

    env = new_env.exit_scope()

    actual = new_env.lookup("node_num")

    # Assert
    assert actual is not None, "Binding not found"
    assert actual == expected, f"actual -> {actual.name} == {expected.name} <- expected"
