from preprocessor.preprocessor import preprocessor
from parser.ast_builder import AbstractSyntaxTreeBuilder
from parser.gsl_parser import gsl_parser
from typesystem.type_checker import TypeChecker
from preprocessor.source_map import SourceMap
from exceptions.parser_exception import ParseException

######### Integration of typesystem

def IntegratedTypesystem(inp_file: str) -> bool:
    sm = SourceMap()
    preprocessed_contents = preprocessor(inp_file, sm)

    tree_builder = gsl_parser.ParseTreeBuilder()
    parser = gsl_parser(preprocessed_contents, tree_builder)
    try:
        parser.parse_Program()
    except ParseException as e:
       raise Exception(f"Error in earlier stage of interpreter: {parser.getErrorMessage(e)}") from e
    ast_builder = AbstractSyntaxTreeBuilder(preprocessed_contents)
    tree = ast_builder.build_tree(tree_builder.stack)

    type_checker = TypeChecker(ast=tree, source_map=sm)
    return type_checker.check()

######### (Helper function)

INPUT_FILES = "tests/typesystem_integration/"

def test_bellman_ford(tmp_path): # tmp:path is from pytest that creates a tmp path for the test run
    # Arrange
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

algo bellmanFord(node s) returns bool
    G.nodes.addAttribute("int", SPE) // shortest Path Estimate
    G.nodes.addAttribute("node", pi)

    // Initialize single source sub-algorithm
    node NIL
    for each v in G.nodes
        v.SPE := 999
        v.pi := NIL
    G.s.SPE := 0

    repeat ||G.nodes|| - 1 times
        for each edge x1 --> x2 with weight w in G
            if x2.SPE > x1.SPE + w then // Relax sub-algorithm
                x2.SPE := x1.SPE + w
                x2.pi := x1

    for each edge x1 --> x2 with weight w in G
        if x2.SPE > x1.SPE + w then
            return false
    return true

bool result := bellmanFord(G.s)
    """
    input_file.write_text(file_contents)

    # Act
    well_formed_program = IntegratedTypesystem(input_file)

    # Assert
    assert well_formed_program == True, "Program was not well formed"


def test_lists(tmp_path):
    # Arrange
    input_dir = tmp_path / INPUT_FILES
    input_dir.mkdir(parents=True)
    input_file = input_dir / "lists.gsl"

    file_contents = """// file:
i 3d list in int := [[[-1,1],[2,2]],[[0,0],[-1,-1]]]
display ||i||

i := [[[1], [-1]], [[1], [1]]]
x in int := i[1][1][1]

y 1d list in real
y := i[1][1]

y[1] = 2.3
    """
    input_file.write_text(file_contents)

    # Act
    well_formed_program = IntegratedTypesystem(input_file)

    # Assert
    assert well_formed_program == True, "Program was not well formed"

def test_algorithm(tmp_path):
    # Arrange
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

    # Act
    well_formed_program = IntegratedTypesystem(str(input_file))

    # Assert
    assert well_formed_program == True, "Program was not well formed"

def test_sorta_dfs(tmp_path):
    # Arrange
    input_dir = tmp_path / INPUT_FILES
    input_dir.mkdir(parents=True)
    input_file = input_dir / "bellman_ford.gsl"

    file_contents = """// file:
node start
visited list in node := [start]
algo DFS(node n)
    display n
    visited[1] := n

    for each neighbor in visited
        DFS(neighbor)
    """
    input_file.write_text(file_contents)

    # Act
    well_formed_program = IntegratedTypesystem(input_file)

    # Assert
    assert well_formed_program == True, "Program was not well formed"
