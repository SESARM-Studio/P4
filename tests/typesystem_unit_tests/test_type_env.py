from typesystem.type_env import TypeEnv
from typesystem.data_types import TypeEnum

def test_type_env_binding_found():
    # Arrange
    expected = TypeEnum.REAL
    env = TypeEnv()

    # Act
    env = env.bind("graph_num", TypeEnum.NAT)
    env = env.bind("weight_sum", TypeEnum.REAL)
    env = env.bind("node_x", TypeEnum.NODE)

    actual = env.lookup("weight_sum")

    # Assert
    assert actual is not None, "Binding not found"
    assert actual == expected, f"actual -> {actual.name} == {expected.name} <- expected"

def test_type_env_binding_not_found():
    # Arrange
    expected = TypeEnum.UNKNOWN
    env = TypeEnv()

    # Act
    env = env.bind("graph_num", TypeEnum.NAT)
    env = env.bind("weight_sum", TypeEnum.REAL)
    env = env.bind("node_x", TypeEnum.NODE)

    actual = env.lookup("edges")

    # Assert
    assert actual is expected, "Binding found"
