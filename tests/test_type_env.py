from typesystem.TypeEnv import TypeEnv, TypeEnum

def test_type_env_binding_found():
    # Arrange
    expected = TypeEnum.REAL
    env = TypeEnv()

    # Act
    env.bind("graph_num", TypeEnum.NAT)
    env.bind("weight_sum", TypeEnum.REAL)
    env.bind("node_x", TypeEnum.NODE)

    actual = env.lookup("weight_sum")

    # Assert
    assert actual is not None, "Binding not found"
    assert actual == expected, f"actual -> {actual.name} == {expected.name} <- expected"

def test_type_env_binding_not_found():
    # Arrange
    expected = None
    env = TypeEnv()

    # Act
    env.bind("graph_num", TypeEnum.NAT)
    env.bind("weight_sum", TypeEnum.REAL)
    env.bind("node_x", TypeEnum.NODE)

    actual = env.lookup("edges")

    # Assert
    assert actual is expected, "Binding found"

def test_type_env_binding_found_in_outer_scope():
    # Arrange
    expected = TypeEnum.REAL
    env = TypeEnv()

    # Act
    env.bind("weight_sum", TypeEnum.REAL)

    env = env.enter_scope()
    env.bind("new_sum", TypeEnum.REAL)
    env.bind("chromatic_color", TypeEnum.TEXT)
    env.bind("Trie", TypeEnum.TREE)

    actual = env.lookup("weight_sum")

    # Assert
    assert actual is not None, "Binding not found"
    assert actual == expected, f"actual -> {actual.name} == {expected.name} <- expected"

def test_type_env_scope_destroyed():
    # Arrange
    expected = None
    env = TypeEnv()

    # Act
    env = env.enter_scope()
    env.bind("graph_num", TypeEnum.NAT)
    env = env.exit_scope()

    actual = env.lookup("graph_num")

    # Assert
    assert actual is None, "Bindings in destroyed scope was not removed"

def test_type_env_variable_shadowed():
    # Arrange
    expected = TypeEnum.INT
    env = TypeEnv()

    # Act
    env.bind("node_num", TypeEnum.NAT)

    env = env.enter_scope()
    env.bind("node_num", TypeEnum.INT)

    actual = env.lookup("node_num")

    # Assert
    assert actual is not None, "Binding not found"
    assert actual == expected, f"actual -> {actual.name} == {expected.name} <- expected"

def test_type_env_shadowed_variable_restored():
    # Arrange
    expected = TypeEnum.NAT
    env = TypeEnv()

    # Act
    env.bind("node_num", TypeEnum.NAT)

    new_env = env.enter_scope()
    new_env.bind("node_num", TypeEnum.INT)

    env = new_env.exit_scope()

    actual = env.lookup("node_num")

    # Assert
    assert actual is not None, "Binding not found"
    assert actual == expected, f"actual -> {actual.name} == {expected.name} <- expected"

def test_type_env_static():
    # Arrange
    expected = TypeEnum.INT
    env = TypeEnv()

    # Act
    env.bind("node_num", TypeEnum.NAT)

    new_env = env.enter_scope()
    new_env.bind("node_num", TypeEnum.INT)

    env = new_env.exit_scope()

    actual = new_env.lookup("node_num")

    # Assert
    assert actual is not None, "Binding not found"
    assert actual == expected, f"actual -> {actual.name} == {expected.name} <- expected"
