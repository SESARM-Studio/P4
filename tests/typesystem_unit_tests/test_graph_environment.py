from typesystem.type_env import GraphEnv
from typesystem.data_types import TypeEnum

def test_graph_environment_update_node_set_current_environment():
    # Arrange
    expected = { "node1", "node2" }
    env = GraphEnv()

    # Act
    env = env.bind("graph1", (TypeEnum.GRAPH, TypeEnum.INT, { "node1" }))
    env = env.update_node_set("graph1", { "node2" })

    actual = env.lookup("graph1")

    # Assert
    assert actual is not TypeEnum.UNKNOWN, "Binding not found"
    node_set = actual[2]
    assert node_set == expected, f"actual -> {node_set} == {expected} <- expected"

def test_graph_environment_update_node_set_current_branch():
    # Arrange
    expected = { "node1" }
    graph_id = "graph1"
    env = GraphEnv()
    env = env.bind("graph1", (TypeEnum.GRAPH, TypeEnum.INT, { "node1" }))
    env1 = env
    env2 = env

    # Act
    # then branch:
    env1 = env1.enter_scope()
    env1 = env1.update_node_set(graph_id, { "node2" })
    # else branch:
    env2 = env2.enter_scope()
    not_updated = env2.lookup(graph_id)
    env2 = env2.update_node_set(graph_id, { "node3" })

    # Assert
    node_set = not_updated[2]
    assert node_set == expected, "env1 updates env2"

def test_graph_environment_merge():
    # Arrange
    expected = { "node1", "node2", "node3" }
    graph_id = "graph1"
    env = GraphEnv()
    env = env.bind("graph1", (TypeEnum.GRAPH, TypeEnum.INT, { "node1" }))
    env1 = env
    env2 = env

    # Act
    env1 = env1.enter_scope()
    env2 = env2.enter_scope()
    env1 = env1.update_node_set(graph_id, { "node2" })
    env2 = env2.update_node_set(graph_id, { "node3" })
    env1 = env1.exit_scope()
    env2 = env2.exit_scope()

    merged_env = GraphEnv.merge(env1.current_scope, env2.current_scope)
    actual = merged_env.lookup("graph1")

    # Assert
    assert actual is not TypeEnum.UNKNOWN, f"'{graph_id}' not bound"
    node_set = actual[2]
    assert node_set == expected, f"actual -> {node_set} == {expected} <- expected"
