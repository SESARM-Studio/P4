from parser.ast_builder import *
from evaluator.functions import *
from copy import deepcopy

import evaluator.categories.expression
import evaluator.categories.statement


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

def test_expression_lit_nat():
    # Arrange
    term = make_term("NATURAL_NUMBER", "18")
    env_graph = dict()
    env_var = dict()
    env_algo = dict()
    loc = Location()
    graph_object = Graph()
    store = dict()

    # Act
    return_object = evaluator.categories.expression.execute_expression(term, env_graph, env_var, env_algo, loc, graph_object, store)

    # Assert
    assert return_object.v == 18
    assert return_object.modified_store == store


# ********* Literal Expressions ********* 
 
def test_expression_lit_int():
    # Arrange
    term = make_term("INTEGER_NUMBER", "-18")
    env_graph = dict()
    env_var = dict()
    env_algo = dict()
    loc = Location()
    graph_object = Graph()
    store = dict()

    # Act
    return_object = evaluator.categories.expression.execute_expression(term, env_graph, env_var, env_algo, loc, graph_object, store)

    # Assert
    assert return_object.v == -18
    assert return_object.modified_store == store

def test_expression_lit_real():
    # Arrange
    term = make_term("REAL_NUMBER", "-18.9")
    env_graph = dict()
    env_var = dict()
    env_algo = dict()
    loc = Location()
    graph_object = Graph()
    store = dict()

    # Act
    return_object = evaluator.categories.expression.execute_expression(term, env_graph, env_var, env_algo, loc, graph_object, store)

    # Assert
    assert return_object.v == -18.9
    assert return_object.modified_store == store

def test_expression_lit_text():
    # Arrange
    term = make_term("TEXT", "\"kdsfbibqoqenq fdsf !¤!¤/Y!N131288__:!321\"")
    env_graph = dict()
    env_var = dict()
    env_algo = dict()
    loc = Location()
    graph_object = Graph()
    store = dict()

    # Act
    return_object = evaluator.categories.expression.execute_expression(term, env_graph, env_var, env_algo, loc, graph_object, store)

    # Assert
    assert return_object.v == "kdsfbibqoqenq fdsf !¤!¤/Y!N131288__:!321"
    assert return_object.modified_store == store

def test_expression_lit_bool():
    # Arrange
    term = make_term("BOOL_VALUE", "true")
    env_graph = dict()
    env_var = dict()
    env_algo = dict()
    loc = Location()
    graph_object = Graph()
    store = dict()

    # Act
    return_object = evaluator.categories.expression.execute_expression(term, env_graph, env_var, env_algo, loc, graph_object, store)

    # Assert
    assert return_object.v == True
    assert return_object.modified_store == store
    

# ********* Identifier ********* 

def test_expression_id():
    # Arrange
    term = make_term("IDENTIFIER", "a")
    env_graph = dict()
    env_var = dict()
    env_algo = dict()
    loc = Location()
    graph_object = Graph()
    store = dict()
    
    env_var.update({"a": loc})
    store.update({loc: 484000.2})

    # Act
    return_object = evaluator.categories.expression.execute_expression(term, env_graph, env_var, env_algo, loc.next_location(), graph_object, store)

    # Assert
    assert return_object.v == 484000.2
    assert return_object.modified_store == store

def test_expression_idg():
    # Arrange
    term = make_term("IDENTIFIER", "a")
    env_graph = dict()
    env_var = dict()
    env_algo = dict()
    loc = Location()
    graph_object = Graph()
    store = dict()
    
    graph_object.create_graph("graph")
    graph_object.add_node("a")

    env_var.update({"a": loc})
    store.update({loc: "a"})

    # Act
    return_object = evaluator.categories.expression.execute_expression(term, env_graph, env_var, env_algo, loc.next_location(), graph_object, store)

    # Assert
    assert return_object.v == "a"
    assert return_object.modified_store == store


# ********* Identifier access ********* 
# Waiting for implementation to be done


# ********* And / Or *********

def test_expression_and1():
    # Arrange
    arg1 = make_term("BOOL_VALUE", "true")
    arg2 = make_term("BOOL_VALUE", "false")

    expression = make_expression("and", arg1, arg2)

    env_graph = dict()
    env_var = dict()
    env_algo = dict()
    loc = Location()
    graph_object = Graph()
    store = dict()

    # Act
    return_object = evaluator.categories.expression.execute_expression(expression, env_graph, env_var, env_algo, loc, graph_object, store)

    # Assert
    assert return_object.v == False

def test_expression_and2():
    # Arrange
    arg1 = make_term("BOOL_VALUE", "true")
    arg2 = make_term("BOOL_VALUE", "true")

    expression = make_expression("and", arg1, arg2)

    env_graph = dict()
    env_var = dict()
    env_algo = dict()
    loc = Location()
    graph_object = Graph()
    store = dict()

    # Act
    return_object = evaluator.categories.expression.execute_expression(expression, env_graph, env_var, env_algo, loc, graph_object, store)

    # Assert
    assert return_object.v == True

def test_expression_or1():
    # Arrange
    arg1 = make_term("BOOL_VALUE", "true")
    arg2 = make_term("BOOL_VALUE", "false")

    expression = make_expression("or", arg1, arg2)

    env_graph = dict()
    env_var = dict()
    env_algo = dict()
    loc = Location()
    graph_object = Graph()
    store = dict()

    # Act
    return_object = evaluator.categories.expression.execute_expression(expression, env_graph, env_var, env_algo, loc, graph_object, store)

    # Assert
    assert return_object.v == True    

def test_expression_or2():
    # Arrange
    arg1 = make_term("BOOL_VALUE", "false")
    arg2 = make_term("BOOL_VALUE", "false")

    expression = make_expression("or", arg1, arg2)

    env_graph = dict()
    env_var = dict()
    env_algo = dict()
    loc = Location()
    graph_object = Graph()
    store = dict()

    # Act
    return_object = evaluator.categories.expression.execute_expression(expression, env_graph, env_var, env_algo, loc, graph_object, store)

    # Assert
    assert return_object.v == False  


# ********* Equality *********

def test_expression_eq1():
    # Arrange
    arg1 = make_term("IDENTIFIER", "a")
    arg2 = make_term("IDENTIFIER", "b")

    expression = make_expression("=", arg1, arg2)

    env_graph = dict()
    env_var = dict()
    env_algo = dict()
    loc = Location()
    graph_object = Graph()
    store = dict()

    env_var.update({"a": loc})
    store.update({loc: 484000.2})

    loc2 =  loc.next_location()
    env_var.update({"b": loc2})
    store.update({loc2: 484000.2})

    loc3 = loc2.next_location()

    # Act
    return_object = evaluator.categories.expression.execute_expression(expression, env_graph, env_var, env_algo, loc3, graph_object, store)

    # Assert
    assert return_object.v == True

def test_expression_eq2():
    # Arrange
    arg1 = make_term("IDENTIFIER", "a")
    arg2 = make_term("IDENTIFIER", "b")

    expression = make_expression("=", arg1, arg2)

    env_graph = dict()
    env_var = dict()
    env_algo = dict()
    loc = Location()
    graph_object = Graph()
    store = dict()

    env_var.update({"a": loc})
    store.update({loc: 484000.2})

    loc2 =  loc.next_location()
    env_var.update({"b": loc2})
    store.update({loc2: -4840.3})

    loc3 = loc2.next_location()

    # Act
    return_object = evaluator.categories.expression.execute_expression(expression, env_graph, env_var, env_algo, loc3, graph_object, store)

    # Assert
    assert return_object.v == False

def test_expression_neq1():
    # Arrange
    arg1 = make_term("IDENTIFIER", "a")
    arg2 = make_term("IDENTIFIER", "b")

    expression = make_expression("!=", arg1, arg2)

    env_graph = dict()
    env_var = dict()
    env_algo = dict()
    loc = Location()
    graph_object = Graph()
    store = dict()

    env_var.update({"a": loc})
    store.update({loc: 484000.2})

    loc2 =  loc.next_location()
    env_var.update({"b": loc2})
    store.update({loc2: 484000.2})

    loc3 = loc2.next_location()

    # Act
    return_object = evaluator.categories.expression.execute_expression(expression, env_graph, env_var, env_algo, loc3, graph_object, store)

    # Assert
    assert return_object.v == False

def test_expression_neq1():
    # Arrange
    arg1 = make_term("IDENTIFIER", "a")
    arg2 = make_term("IDENTIFIER", "b")

    expression = make_expression("!=", arg1, arg2)

    env_graph = dict()
    env_var = dict()
    env_algo = dict()
    loc = Location()
    graph_object = Graph()
    store = dict()

    env_var.update({"a": loc})
    store.update({loc: 484000.2})

    loc2 =  loc.next_location()
    env_var.update({"b": loc2})
    store.update({loc2: -4840.3})

    loc3 = loc2.next_location()

    # Act
    return_object = evaluator.categories.expression.execute_expression(expression, env_graph, env_var, env_algo, loc3, graph_object, store)

    # Assert
    assert return_object.v == True


# ********* Comparison *********

def test_expression_lt1():
    # Arrange
    arg1 = make_term("IDENTIFIER", "a")
    arg2 = make_term("IDENTIFIER", "b")

    expression = make_expression("<", arg1, arg2)

    env_graph = dict()
    env_var = dict()
    env_algo = dict()
    loc = Location()
    graph_object = Graph()
    store = dict()

    env_var.update({"a": loc})
    store.update({loc: 484000.2})

    loc2 =  loc.next_location()
    env_var.update({"b": loc2})
    store.update({loc2: 484000.2})

    loc3 = loc2.next_location()

    # Act
    return_object = evaluator.categories.expression.execute_expression(expression, env_graph, env_var, env_algo, loc3, graph_object, store)

    # Assert
    assert return_object.v == False

def test_expression_lt2():
    # Arrange
    arg1 = make_term("IDENTIFIER", "a")
    arg2 = make_term("IDENTIFIER", "b")

    expression = make_expression("<", arg1, arg2)

    env_graph = dict()
    env_var = dict()
    env_algo = dict()
    loc = Location()
    graph_object = Graph()
    store = dict()

    env_var.update({"a": loc})
    store.update({loc: 484})

    loc2 =  loc.next_location()
    env_var.update({"b": loc2})
    store.update({loc2: 484000.2})

    loc3 = loc2.next_location()

    # Act
    return_object = evaluator.categories.expression.execute_expression(expression, env_graph, env_var, env_algo, loc3, graph_object, store)

    # Assert
    assert return_object.v == True

def test_expression_gt1():
    # Arrange
    arg1 = make_term("IDENTIFIER", "a")
    arg2 = make_term("IDENTIFIER", "b")

    expression = make_expression(">", arg1, arg2)

    env_graph = dict()
    env_var = dict()
    env_algo = dict()
    loc = Location()
    graph_object = Graph()
    store = dict()

    env_var.update({"a": loc})
    store.update({loc: 484000.2})

    loc2 =  loc.next_location()
    env_var.update({"b": loc2})
    store.update({loc2: 484000.2})

    loc3 = loc2.next_location()

    # Act
    return_object = evaluator.categories.expression.execute_expression(expression, env_graph, env_var, env_algo, loc3, graph_object, store)

    # Assert
    assert return_object.v == False

def test_expression_gt2():
    # Arrange
    arg1 = make_term("IDENTIFIER", "a")
    arg2 = make_term("IDENTIFIER", "b")

    expression = make_expression(">", arg1, arg2)

    env_graph = dict()
    env_var = dict()
    env_algo = dict()
    loc = Location()
    graph_object = Graph()
    store = dict()

    env_var.update({"a": loc})
    store.update({loc: 484000.2})

    loc2 =  loc.next_location()
    env_var.update({"b": loc2})
    store.update({loc2: 484})

    loc3 = loc2.next_location()

    # Act
    return_object = evaluator.categories.expression.execute_expression(expression, env_graph, env_var, env_algo, loc3, graph_object, store)

    # Assert
    assert return_object.v == True

def test_expression_leq1():
    # Arrange
    arg1 = make_term("IDENTIFIER", "a")
    arg2 = make_term("IDENTIFIER", "b")

    expression = make_expression("<=", arg1, arg2)

    env_graph = dict()
    env_var = dict()
    env_algo = dict()
    loc = Location()
    graph_object = Graph()
    store = dict()

    env_var.update({"a": loc})
    store.update({loc: 484})

    loc2 =  loc.next_location()
    env_var.update({"b": loc2})
    store.update({loc2: 484000.2})

    loc3 = loc2.next_location()

    # Act
    return_object = evaluator.categories.expression.execute_expression(expression, env_graph, env_var, env_algo, loc3, graph_object, store)

    # Assert
    assert return_object.v == True

def test_expression_leq2():
    # Arrange
    arg1 = make_term("IDENTIFIER", "a")
    arg2 = make_term("IDENTIFIER", "b")

    expression = make_expression("<=", arg1, arg2)

    env_graph = dict()
    env_var = dict()
    env_algo = dict()
    loc = Location()
    graph_object = Graph()
    store = dict()

    env_var.update({"a": loc})
    store.update({loc: 484000.2})

    loc2 =  loc.next_location()
    env_var.update({"b": loc2})
    store.update({loc2: 484000.2})

    loc3 = loc2.next_location()

    # Act
    return_object = evaluator.categories.expression.execute_expression(expression, env_graph, env_var, env_algo, loc3, graph_object, store)

    # Assert
    assert return_object.v == True

def test_expression_leq3():
    # Arrange
    arg1 = make_term("IDENTIFIER", "a")
    arg2 = make_term("IDENTIFIER", "b")

    expression = make_expression("<=", arg1, arg2)

    env_graph = dict()
    env_var = dict()
    env_algo = dict()
    loc = Location()
    graph_object = Graph()
    store = dict()

    env_var.update({"a": loc})
    store.update({loc: 484000.2})

    loc2 =  loc.next_location()
    env_var.update({"b": loc2})
    store.update({loc2: 484})

    loc3 = loc2.next_location()

    # Act
    return_object = evaluator.categories.expression.execute_expression(expression, env_graph, env_var, env_algo, loc3, graph_object, store)

    # Assert
    assert return_object.v == False

def test_expression_geq1():
    # Arrange
    arg1 = make_term("IDENTIFIER", "a")
    arg2 = make_term("IDENTIFIER", "b")

    expression = make_expression(">=", arg1, arg2)

    env_graph = dict()
    env_var = dict()
    env_algo = dict()
    loc = Location()
    graph_object = Graph()
    store = dict()

    env_var.update({"a": loc})
    store.update({loc: 484000.2})

    loc2 =  loc.next_location()
    env_var.update({"b": loc2})
    store.update({loc2: 484})

    loc3 = loc2.next_location()

    # Act
    return_object = evaluator.categories.expression.execute_expression(expression, env_graph, env_var, env_algo, loc3, graph_object, store)

    # Assert
    assert return_object.v == True

def test_expression_geq2():
    # Arrange
    arg1 = make_term("IDENTIFIER", "a")
    arg2 = make_term("IDENTIFIER", "b")

    expression = make_expression(">=", arg1, arg2)

    env_graph = dict()
    env_var = dict()
    env_algo = dict()
    loc = Location()
    graph_object = Graph()
    store = dict()

    env_var.update({"a": loc})
    store.update({loc: 484000.2})

    loc2 =  loc.next_location()
    env_var.update({"b": loc2})
    store.update({loc2: 484000.2})

    loc3 = loc2.next_location()

    # Act
    return_object = evaluator.categories.expression.execute_expression(expression, env_graph, env_var, env_algo, loc3, graph_object, store)

    # Assert
    assert return_object.v == True

def test_expression_geq3():
    # Arrange
    arg1 = make_term("IDENTIFIER", "a")
    arg2 = make_term("IDENTIFIER", "b")

    expression = make_expression(">=", arg1, arg2)

    env_graph = dict()
    env_var = dict()
    env_algo = dict()
    loc = Location()
    graph_object = Graph()
    store = dict()

    env_var.update({"a": loc})
    store.update({loc: 484})

    loc2 =  loc.next_location()
    env_var.update({"b": loc2})
    store.update({loc2: 484000.2})

    loc3 = loc2.next_location()

    # Act
    return_object = evaluator.categories.expression.execute_expression(expression, env_graph, env_var, env_algo, loc3, graph_object, store)

    # Assert
    assert return_object.v == False


# ********* Arithmetic *********

def test_expression_add():
    # Arrange
    arg1 = make_term("INTEGER_NUMBER", "-3")
    arg2 = make_term("INTEGER_NUMBER", "7")

    expression = make_expression("+", arg1, arg2)

    env_graph = dict()
    env_var = dict()
    env_algo = dict()
    loc = Location()
    graph_object = Graph()
    store = dict()

    # Act
    return_object = evaluator.categories.expression.execute_expression(expression, env_graph, env_var, env_algo, loc, graph_object, store)

    # Assert
    assert return_object.v == 4

def test_expression_sub():
    # Arrange
    arg1 = make_term("INTEGER_NUMBER", "-3")
    arg2 = make_term("INTEGER_NUMBER", "7")

    expression = make_expression("-", arg1, arg2)

    env_graph = dict()
    env_var = dict()
    env_algo = dict()
    loc = Location()
    graph_object = Graph()
    store = dict()

    # Act
    return_object = evaluator.categories.expression.execute_expression(expression, env_graph, env_var, env_algo, loc, graph_object, store)

    # Assert
    assert return_object.v == -10

def test_expression_mul():
    # Arrange
    arg1 = make_term("INTEGER_NUMBER", "-3")
    arg2 = make_term("INTEGER_NUMBER", "7")

    expression = make_expression("*", arg1, arg2)

    env_graph = dict()
    env_var = dict()
    env_algo = dict()
    loc = Location()
    graph_object = Graph()
    store = dict()

    # Act
    return_object = evaluator.categories.expression.execute_expression(expression, env_graph, env_var, env_algo, loc, graph_object, store)

    # Assert
    assert return_object.v == -21

def test_expression_div():
    # Arrange
    arg1 = make_term("REAL_NUMBER", "-24.5")
    arg2 = make_term("INTEGER_NUMBER", "7")

    expression = make_expression("/", arg1, arg2)

    env_graph = dict()
    env_var = dict()
    env_algo = dict()
    loc = Location()
    graph_object = Graph()
    store = dict()

    # Act
    return_object = evaluator.categories.expression.execute_expression(expression, env_graph, env_var, env_algo, loc, graph_object, store)

    # Assert
    assert return_object.v == -3.5

def test_expression_mod():
    # Arrange
    arg1 = make_term("INTEGER_NUMBER", "-3")
    arg2 = make_term("INTEGER_NUMBER", "7")

    expression = make_expression("%", arg1, arg2)

    env_graph = dict()
    env_var = dict()
    env_algo = dict()
    loc = Location()
    graph_object = Graph()
    store = dict()

    # Act
    return_object = evaluator.categories.expression.execute_expression(expression, env_graph, env_var, env_algo, loc, graph_object, store)

    # Assert
    assert return_object.v == 4


# ********* Exponentiation *********

def test_expression_exp():
    # Arrange
    arg1 = make_term("INTEGER_NUMBER", "-3")
    arg2 = make_term("INTEGER_NUMBER", "7")

    expression = make_expression("^", arg1, arg2)

    env_graph = dict()
    env_var = dict()
    env_algo = dict()
    loc = Location()
    graph_object = Graph()
    store = dict()

    # Act
    return_object = evaluator.categories.expression.execute_expression(expression, env_graph, env_var, env_algo, loc, graph_object, store)

    # Assert
    assert return_object.v == -2187


# ********* Exponentiation *********

def test_expression_neg1():
    # Arrange
    arg1 = make_term("BOOL_VALUE", "true")

    expression = Expression("Expression")
    expression.operator = "neg"
    expression.arg1 = arg1

    env_graph = dict()
    env_var = dict()
    env_algo = dict()
    loc = Location()
    graph_object = Graph()
    store = dict()

    # Act
    return_object = evaluator.categories.expression.execute_expression(expression, env_graph, env_var, env_algo, loc, graph_object, store)

    # Assert
    assert return_object.v == False

def test_expression_neg2():
    # Arrange
    arg1 = make_term("BOOL_VALUE", "false")

    expression = Expression("Expression")
    expression.operator = "neg"
    expression.arg1 = arg1

    env_graph = dict()
    env_var = dict()
    env_algo = dict()
    loc = Location()
    graph_object = Graph()
    store = dict()

    # Act
    return_object = evaluator.categories.expression.execute_expression(expression, env_graph, env_var, env_algo, loc, graph_object, store)

    # Assert
    assert return_object.v == True


# ********* Absolute value / Magnitude *********

def test_expression_abs():
    # Arrange
    arg1 = make_term("INTEGER_NUMBER", "-2")

    exp = Expression("Expression")
    exp.arg1 = arg1

    abs_expression = AbsoluteValue("AbsoluteValue")
    abs_expression.expression = exp

    env_graph = dict()
    env_var = dict()
    env_algo = dict()
    loc = Location()
    graph_object = Graph()
    store = dict()

    # Act
    return_object = evaluator.categories.expression.execute_expression(abs_expression, env_graph, env_var, env_algo, loc, graph_object, store)

    # Assert
    assert return_object.v == 2

def test_expression_mag1():
    # Arrange
    arg1 = make_term("TEXT", "\"test\"")

    exp = Expression("Expression")
    exp.arg1 = arg1

    abs_expression = Magnitude("Magnitude")
    abs_expression.expression = exp

    env_graph = dict()
    env_var = dict()
    env_algo = dict()
    loc = Location()
    graph_object = Graph()
    store = dict()

    # Act
    return_object = evaluator.categories.expression.execute_expression(abs_expression, env_graph, env_var, env_algo, loc, graph_object, store)

    # Assert
    assert return_object.v == 4

def test_expression_mag2():
    # Arrange
    arg1 = make_term("IDENTIFIER", "a")

    exp = Expression("Expression")
    exp.arg1 = arg1

    abs_expression = Magnitude("Magnitude")
    abs_expression.expression = exp

    env_graph = dict()
    env_var = dict()
    env_algo = dict()
    loc = Location()
    graph_object = Graph()
    store = dict()

    env_var.update({"a": loc})
    store.update({loc: [1,2,3]})

    # Act
    return_object = evaluator.categories.expression.execute_expression(abs_expression, env_graph, env_var, env_algo, loc.next_location(), graph_object, store)

    # Assert
    assert return_object.v == 3


# ********* Parentheses *********
# Not handled in evaluator. It is handled already by AST by creating expression subtrees


# ********* Function call *********
def test_expression_cll():
    ## Arrange

    env_graph = dict()
    env_var = dict()
    env_algo = dict()
    loc = Location()
    graph_object = Graph()
    store = dict()

    # Algorithm body statements
    arg1 = make_term("IDENTIFIER", "a")
    arg2 = make_term("IDENTIFIER", "b")
    body_expression = make_expression("+", arg1, arg2)

    body_statement = ReturnStatement("ReturnStatement")
    body_statement.expression = body_expression

    body_statements = [body_statement]

    # Algorithm parameters
    par1 = Parameter("Parameter")
    par1.identifier = "a"
    par1.type = "nat"

    par2 = Parameter("Parameter")
    par2.identifier = "b"
    par2.type = "nat"

    parameters = [par1, par2]

    # Update algorithm environment for algorithm identifier
    env_algo.update({"f": (parameters, body_statements, env_graph.copy(), deepcopy(env_var), deepcopy(env_algo))})


    # Algorithm call arguments
    arg1 = make_term("NATURAL_NUMBER", "2")
    exp1 = Expression("Expression")
    exp1.arg1 = arg1

    arg2 = make_term("NATURAL_NUMBER", "3")
    exp2 = Expression("Expression")
    exp2.arg1 = arg2

    # Algorithm call node
    algorithm_call = AlgorithmCall("AlgorithmCall")
    algorithm_call.arguments = [exp1, exp2]
    algorithm_call.identifier = "f"


    ## Act
    return_object = evaluator.categories.expression.execute_expression(algorithm_call, env_graph, env_var, env_algo, loc.next_location(), graph_object, store)

    ## Assert
    assert return_object.v == 5


# ********* List *********

def test_expression_list():
    # Arrange
    exp_inner1 = make_expression(arg1=make_term("NATURAL_NUMBER", "1"))
    exp_inner2 = make_expression(arg1=make_term("NATURAL_NUMBER", "2"))
    exp_inner3 = make_expression(arg1=make_term("NATURAL_NUMBER", "3"))
    exp_inner4 = make_expression(arg1=make_term("NATURAL_NUMBER", "4"))

    exp_list_inner1 = ListExpression("ListExpression")
    exp_list_inner1.expressions = [exp_inner1, exp_inner2]

    exp_list_inner2 = ListExpression("ListExpression")
    exp_list_inner2.expressions = [exp_inner3, exp_inner4]

    exp_outer1 = make_expression(arg1=exp_list_inner1)
    exp_outer2 = make_expression(arg1=exp_list_inner2)

    exp_list_outer = ListExpression("ListExpression")
    exp_list_outer.expressions = [exp_outer1, exp_outer2]

    exp_main = make_expression(arg1=exp_list_outer)

    env_graph = dict()
    env_var = dict()
    env_algo = dict()
    loc = Location()
    graph_object = Graph()
    store = dict()

    # Act
    return_object = evaluator.categories.expression.execute_expression(exp_main, env_graph, env_var, env_algo, loc.next_location(), graph_object, store)

    # Assert
    assert return_object.v == [[1,2],[3,4]]


# ********* Indexing *********

def test_expression_indexing():
    # Arrange
    env_graph = dict()
    env_var = dict()
    env_algo = dict()
    loc = Location()
    graph_object = Graph()
    store = dict()

    env_var.update({"a": loc})
    store.update({loc: [[1,2],[3,4]]})

    exp_inner1 = make_expression(arg1=make_term("NATURAL_NUMBER", "1"))
    exp_inner2 = make_expression(arg1=make_term("NATURAL_NUMBER", "2"))

    array_access_node = ArrayAccess("ArrayAccess")
    array_access_node.identifier = "a"
    array_access_node.indexes = [exp_inner1, exp_inner2]

    exp_outer = make_expression(arg1=array_access_node)

    # Act
    return_object = evaluator.categories.expression.execute_expression(exp_outer, env_graph, env_var, env_algo, loc.next_location(), graph_object, store)

    # Assert
    assert return_object.v == 2


# ********* Weight of edges *********

def test_expression_woe1():

    # Arrange
    env_graph = dict()
    env_var = dict()
    env_algo = dict()
    loc = Location()
    graph_object = Graph()
    store = dict()

    # Arrange for declaring graph G with nodes a,b and the edge a-->b with weight 5 (nat)
    exp_weight = make_expression(arg1=make_term("NATURAL_NUMBER", "5"))

    decl_edge = EdgeDecl("EdgeDecl")
    decl_edge.initial_node = 'a'
    decl_edge.nodes = ['b']
    decl_edge.direction = "-->"
    decl_edge.weight = [exp_weight]

    decl_nodes = NodeDecl("NodeDecl")
    decl_nodes.type = "node"
    decl_nodes.identifiers = ['a', 'b']
    decl_nodes.is_list = False

    decl_graph = GraphDecl("GraphDecl")
    decl_graph.graph_type = "digraph"
    decl_graph.identifier = "G"
    decl_graph.weight_type = "nat"
    decl_graph.nodes = [decl_nodes]
    decl_graph.edges = [decl_edge]

    # Declaring the graph G
    store, env_var, env_algo, env_graph, v, loc = evaluator.categories.statement.execute_statement(decl_graph, loc, graph_object, store, env_var, env_algo, env_graph)

    # Arranging for weight of node
    exp = make_expression("weight of", arg1="G.a-->b")

    # Act
    return_object = evaluator.categories.expression.execute_expression(exp, env_graph, env_var, env_algo, loc.next_location(), graph_object, store)

    # Assert
    assert return_object.v == 5

def test_expression_woe2():

    # Arrange
    env_graph = dict()
    env_var = dict()
    env_algo = dict()
    loc = Location()
    graph_object = Graph()
    store = dict()

    # Arrange for declaring graph G with nodes a,b and the edge a-->b with weight 5 (nat)
    exp_weight = make_expression(arg1=make_term("NATURAL_NUMBER", "5"))

    decl_edge = EdgeDecl("EdgeDecl")
    decl_edge.initial_node = 'a'
    decl_edge.nodes = ['b']
    decl_edge.direction = "---"
    decl_edge.weight = [exp_weight]

    decl_nodes = NodeDecl("NodeDecl")
    decl_nodes.type = "node"
    decl_nodes.identifiers = ['a', 'b']
    decl_nodes.is_list = False

    decl_graph = GraphDecl("GraphDecl")
    decl_graph.graph_type = "graph"
    decl_graph.identifier = "G"
    decl_graph.weight_type = "nat"
    decl_graph.nodes = [decl_nodes]
    decl_graph.edges = [decl_edge]

    # Declaring the graph G
    store, env_var, env_algo, env_graph, v, loc = evaluator.categories.statement.execute_statement(decl_graph, loc, graph_object, store, env_var, env_algo, env_graph)

    # Arranging for weight of node
    exp = make_expression("weight of", arg1="G.a-->b")

    # Act
    return_object = evaluator.categories.expression.execute_expression(exp, env_graph, env_var, env_algo, loc.next_location(), graph_object, store)

    # Assert
    assert return_object.v == 5


