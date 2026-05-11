from typesystem.type_env import GraphEnv
from typesystem.data_types import TypeEnum

def test_graph_environment_update_node_set_current_environment():
    # Arrange
    expected = { "node1", "node2" }
    env = GraphEnv()

    # Act
    env.current_scope = env.current_scope.bind("graph1", (TypeEnum.GRAPH, TypeEnum.INT, { "node1" }))
    env.update_node_set("graph1", { "node2"})

    actual = env.lookup("graph1")

    # Assert
    assert actual is not TypeEnum.UNKNOWN, "Binding not found"
    node_set = actual[2]
    assert node_set == expected, f"actual -> {node_set} == {expected} <- expected"
