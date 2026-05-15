from parser.ast_builder import *
from evaluator.functions import *
from copy import deepcopy

import evaluator.categories.algorithm

### AST tree helpers ###
def make_term(_type=None, value=None, children=None, token="Term"):
    term = Term(token)
    term.type = _type
    term.value = value
    term.children = children
    return term

def make_expression(operator=None, arg1=None, arg2=None, token="Expression"):
    expr = Expression(token)
    expr.operator = operator
    expr.arg1 = arg1
    expr.arg2 = arg2
    return expr

########################


def test_algorithm():
    
    ## Arrange
    env_graph = dict()
    env_var = dict()
    env_algo = dict()
    loc = Location()
    graph_object = Graph()
    store = dict()

    # Algorithm parameters
    par1 = Parameter("Parameter")
    par1.identifier = "a"
    par1.type = "nat"

    par2 = Parameter("Parameter")
    par2.identifier = "b"
    par2.type = "nat"

    # Algorithm statement (body)
    arg1 = make_term("IDENTIFIER", "a")
    arg2 = make_term("IDENTIFIER", "b")
    body_expression = make_expression("/", arg1, arg2)

    body_statement = ReturnStatement("ReturnStatement")
    body_statement.expression = body_expression

    algorithm_node = Algorithm("Algorithm")
    algorithm_node.identifier = "f"
    algorithm_node.parameters = [par1, par2]
    algorithm_node.statements = [body_statement]

    ## Act
    env_algo = evaluator.categories.algorithm.execute_algorithm(algorithm_node, env_graph, env_var, env_algo, loc, graph_object, store)

    ## Assert
    parameters, statements, env_graph_old, env_var_old, env_algo_old = env_algo.get("f")

    # Check parameters
    assert parameters[0].identifier == "a" and parameters[0].type == "nat"
    assert parameters[1].identifier == "b" and parameters[1].type == "nat"

    # Check body
    assert isinstance(statements[0], ReturnStatement)
    assert statements[0].expression.operator == "/"
    assert statements[0].expression.arg1.type == "IDENTIFIER" and statements[0].expression.arg1.value == "a"
    assert statements[0].expression.arg2.type == "IDENTIFIER" and statements[0].expression.arg2.value == "b"

def test_algorithm_return_type():
    
    ## Arrange
    env_graph = dict()
    env_var = dict()
    env_algo = dict()
    loc = Location()
    graph_object = Graph()
    store = dict()

    # Algorithm parameters
    par1 = Parameter("Parameter")
    par1.identifier = "a"
    par1.type = "nat"

    par2 = Parameter("Parameter")
    par2.identifier = "b"
    par2.type = "nat"

    # Algorithm statement (body)
    arg1 = make_term("IDENTIFIER", "a")
    arg2 = make_term("IDENTIFIER", "b")
    body_expression = make_expression("/", arg1, arg2)

    body_statement = ReturnStatement("ReturnStatement")
    body_statement.expression = body_expression

    algorithm_node = Algorithm("Algorithm")
    algorithm_node.identifier = "f"
    algorithm_node.parameters = [par1, par2]
    algorithm_node.statements = [body_statement]
    algorithm_node.return_type = "real"

    ## Act
    env_algo = evaluator.categories.algorithm.execute_algorithm(algorithm_node, env_graph, env_var, env_algo, loc, graph_object, store)

    ## Assert
    parameters, statements, env_graph_old, env_var_old, env_algo_old = env_algo.get("f")

    # Check parameters
    assert parameters[0].identifier == "a" and parameters[0].type == "nat"
    assert parameters[1].identifier == "b" and parameters[1].type == "nat"

    # Check body
    assert isinstance(statements[0], ReturnStatement)
    assert statements[0].expression.operator == "/"
    assert statements[0].expression.arg1.type == "IDENTIFIER" and statements[0].expression.arg1.value == "a"
    assert statements[0].expression.arg2.type == "IDENTIFIER" and statements[0].expression.arg2.value == "b"

def test_algorithm_static_var():
    
    ## Arrange
    env_graph = dict()
    env_var = dict()
    env_algo = dict()
    loc = Location()
    graph_object = Graph()
    store = dict()

    # Algorithm parameters
    par1 = Parameter("Parameter")
    par1.identifier = "a"
    par1.type = "nat"

    par2 = Parameter("Parameter")
    par2.identifier = "b"
    par2.type = "nat"

    # Algorithm statement (body)
    arg1 = make_term("IDENTIFIER", "a")
    arg2 = make_term("IDENTIFIER", "b")
    body_expression = make_expression("/", arg1, arg2)

    body_statement = ReturnStatement("ReturnStatement")
    body_statement.expression = body_expression

    algorithm_node = Algorithm("Algorithm")
    algorithm_node.identifier = "f"
    algorithm_node.parameters = [par1, par2]
    algorithm_node.statements = [body_statement]
    algorithm_node.return_type = "real"

    ## Act
    env_algo = evaluator.categories.algorithm.execute_algorithm(algorithm_node, env_graph, env_var, env_algo, loc, graph_object, store)

    # Add new variable to variable environment
    env_var.update({"k": loc})
    loc = loc.next_location()

    ## Assert
    parameters, statements, env_graph_old, env_var_old, env_algo_old = env_algo.get("f")

    # Check newly declared variable is not in algorithm's saved
    assert "k" not in env_var_old

def test_algorithm_static_graph():
    
    ## Arrange
    env_graph = dict()
    env_var = dict()
    env_algo = dict()
    loc = Location()
    graph_object = Graph()
    store = dict()

    # Algorithm parameters
    par1 = Parameter("Parameter")
    par1.identifier = "a"
    par1.type = "nat"

    par2 = Parameter("Parameter")
    par2.identifier = "b"
    par2.type = "nat"

    # Algorithm statement (body)
    arg1 = make_term("IDENTIFIER", "a")
    arg2 = make_term("IDENTIFIER", "b")
    body_expression = make_expression("/", arg1, arg2)

    body_statement = ReturnStatement("ReturnStatement")
    body_statement.expression = body_expression

    algorithm_node = Algorithm("Algorithm")
    algorithm_node.identifier = "f"
    algorithm_node.parameters = [par1, par2]
    algorithm_node.statements = [body_statement]
    algorithm_node.return_type = "real"

    ## Act
    env_algo = evaluator.categories.algorithm.execute_algorithm(algorithm_node, env_graph, env_var, env_algo, loc, graph_object, store)

    # Add new graph to graph environment
    env_graph.update({"G": Graph()})

    ## Assert
    parameters, statements, env_graph_old, env_var_old, env_algo_old = env_algo.get("f")

    # Check newly declared variable is not in algorithm's saved
    assert "G" not in env_graph_old

def test_algorithm_static_algo():
    
    ## Arrange
    env_graph = dict()
    env_var = dict()
    env_algo = dict()
    loc = Location()
    graph_object = Graph()
    store = dict()

    # Algorithm parameters
    par1 = Parameter("Parameter")
    par1.identifier = "a"
    par1.type = "nat"

    par2 = Parameter("Parameter")
    par2.identifier = "b"
    par2.type = "nat"

    # Algorithm statement (body)
    arg1 = make_term("IDENTIFIER", "a")
    arg2 = make_term("IDENTIFIER", "b")
    body_expression = make_expression("/", arg1, arg2)

    body_statement = ReturnStatement("ReturnStatement")
    body_statement.expression = body_expression

    algorithm_node = Algorithm("Algorithm")
    algorithm_node.identifier = "f"
    algorithm_node.parameters = [par1, par2]
    algorithm_node.statements = [body_statement]
    algorithm_node.return_type = "real"

    ## Act
    env_algo = evaluator.categories.algorithm.execute_algorithm(algorithm_node, env_graph, env_var, env_algo, loc, graph_object, store)

    # Add new algorithm to algorithm environment (filled with dummy tuple)
    env_algo.update({"h": ([], [], dict(), dict(), dict())})

    ## Assert
    parameters, statements, env_graph_old, env_var_old, env_algo_old = env_algo.get("f")

    # Check newly declared variable is not in algorithm's saved
    assert "h" not in env_algo_old
