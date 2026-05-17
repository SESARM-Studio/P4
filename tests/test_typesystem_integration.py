from preprocessor.prepro import preprocessor
from parser.ast_builder import AbstractSyntaxTreeBuilder, print_ast
from parser.gsl_parser import gsl_parser
from typesystem.type_checker import TypeChecker

######### Integration of typesystem

def IntegratedTypesystem(inp_file: str) -> bool:
    preprocessed_contents = preprocessor(inp_file)

    tree_builder = gsl_parser.ParseTreeBuilder()
    parser = gsl_parser(preprocessed_contents, tree_builder)
    try:
        parser.parse_Program()
    except gsl_parser.ParseException as e:
       raise Exception(f"Error in earlier stage of interpreter: {parser.getErrorMessage(e)}") from e
    ast_builder = AbstractSyntaxTreeBuilder(preprocessed_contents)
    tree = ast_builder.build_tree(tree_builder.stack)

    type_checker = TypeChecker(ast=tree)
    return type_checker.check()

######### (Helper function)


#########
#
# Test steps:
#
#########

INPUT_FILES = "tests/typesystem_integration/"

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
algo another_one(t in nat) return real
    display t
    """
    input_file.write_text(file_contents)

    # Act
    well_formed_program = IntegratedTypesystem(input_file)

    # Assert
    assert well_formed_program == True, "Program was not well formed"
