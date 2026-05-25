from preprocessor.prepro import preprocessor
from preprocessor.prepro import preprocessor, SourceMap
from parser.gsl_parser import gsl_parser
from typesystem.type_checker import TypeChecker
from parser.ast_builder import AbstractSyntaxTreeBuilder
from preprocessor.source_map import SourceMap
from exceptions.parser_exception import ParseException
from exceptions.evaluator_exception import EvaluatorException
from evaluator.evaluator import traverse_program
import sys

######### Integration of typesystem

def IntegratedEvaluator(inp_file: str) -> bool:
    sm = SourceMap()
    preprocessed_contents = preprocessor(inp_file, sm)

    tree_builder = gsl_parser.ParseTreeBuilder()
    parser = gsl_parser(preprocessed_contents, tree_builder)

    try:
        parser.parse_Program()
        ast_builder = AbstractSyntaxTreeBuilder(preprocessed_contents)
        tree = ast_builder.build_tree(tree_builder.stack)
        type_checker = TypeChecker(tree, sm)
        type_checker.check()
        program_result = traverse_program(tree)
    except ParseException as pe:
        sm.print_error(parser.getErrorMessage(pe), pe.getBegin(), pe.getEnd())
        sys.exit(1)
    except EvaluatorException as ee:
        sm.print_error(ee.message, ee.span[0], ee.span[1], error_type="Evaluator")
        sys.exit(1)
    
    return program_result

######### (Helper function)

INPUT_FILES = "tests/typesystem_integration/"

def test_bellman_ford(tmp_path): # tmp:path is from pytest that creates a tmp path for the test run
    ## Arrange
    # the '/' is overloaded for path objects that concats the two paths with '/' or '\' depending on system
    input_dir = tmp_path / INPUT_FILES
    input_dir.mkdir(parents=True)
    input_file = input_dir / "bellman_ford.gsl"

    file_contents = """// file:
digraph G with int weight
    node s, y, z, t, x

    edge s --> t, y weight 6, 7
    edge y --> z weight 9
    edge y --> x weight -3
    edge z --> s, x weight 2, 7
    edge t --> y, z weight 8, -4
    edge t --> x weight 5
    edge x --> t weight -2

node NIL
INF in int := 99999999

algo initializeSingleSource(node s)
    // Adding attributes: nodeX.addAttribute(datatype, attributeName)
    G.nodes.addAttribute("int", SPE) // shortest Path Estimate
    G.nodes.addAttribute("node", pi)

    for each v in G.nodes
        v.SPE := INF
        v.pi := NIL
    s.SPE := 0

algo relax(node x1, node x2, w in int)
    if x2.SPE > x1.SPE + w then
        x2.SPE := x1.SPE + w
        x2.pi := x1

algo bellmanFord(node s) returns bool

    initializeSingleSource(s)

    // '||v||' is magnitude of v
    repeat ||G.nodes|| - 1 times
        for each edge x1 --> x2 with weight w in G
            relax(x1, x2, w)

    for each edge x1 --> x2 with weight w in G
        if x2.SPE > x1.SPE + w then
            return false
    return true

bool result := bellmanFord(G.s)
    """
    input_file.write_text(file_contents)

    ## Act
    store, env_var, env_algo, env_graph, v, loc = IntegratedEvaluator(input_file)

    ## Assert
    # Check Bellman-Ford returns true (result is correct)
    location = env_var.get("result")
    assert store.get(location) == True, "Bellman-Ford does not return true!"

def test_algorithm(tmp_path):
    ## Arrange
    input_dir = tmp_path / INPUT_FILES
    input_dir.mkdir(parents=True)
    input_file = input_dir / "algorithm.gsl"

    file_contents = """// file:
s in real
graph x_times
algo helper(x_times in int, node s)
    y 1d list in int := [1,2,3]
    repeat ||y|| - 1 times
        display s

text t
algo another_one(t in nat) returns real
    display t
    """
    input_file.write_text(file_contents)

    ## Act
    store, env_var, env_algo, env_graph, v, loc = IntegratedEvaluator(input_file)

    ## Assert
    # Check that declared variables and algorithms exists
    assert "s" in env_var
    assert "x_times" in env_graph
    assert "helper" in env_algo
    assert "t" in env_var
    assert "another_one" in env_algo

    # Check local list does not exist in global scope
    assert "y" not in env_var

