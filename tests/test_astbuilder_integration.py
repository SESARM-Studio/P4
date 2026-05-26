from exceptions.preprocessor_exception import PreprocessorException
from preprocessor.preprocessor import preprocessor
from preprocessor.source_map import SourceMap
from parser.gsl_parser import *
from parser.ast_builder import *
from exceptions.parser_exception import ParseException

def IntegratedASTBuilder(inp_file):
    sm = SourceMap()
    try:
        preprocessed_contents = preprocessor(inp_file, sm)
    except PreprocessorException as pe:
        sm.print_error(pe.message, pe.span[0], pe.span[1], processed=False)
        sys.exit(1)

    tree_builder = gsl_parser.ParseTreeBuilder()
    parser = gsl_parser(preprocessed_contents, tree_builder)
    try:
        parser.parse_Program()
    except ParseException as pe:
            sm.print_error(parser.getErrorMessage(pe), pe.getBegin(), pe.getEnd())
            sys.exit(1)
    
    ast_builder = AbstractSyntaxTreeBuilder(preprocessed_contents)
    tree = ast_builder.build_tree(tree_builder.stack)
    return tree

INPUT_FILES = "tests/astbuilder_integration/"

def test_bellman_ford_AST_builder_integration(tmp_path):
    # Arrange
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
    abstract_syntax_tree = IntegratedASTBuilder(input_file)

    # Assert
    assert abstract_syntax_tree.token == "Program"
    assert len(abstract_syntax_tree.children) == 4
    assert isinstance(abstract_syntax_tree.children[0], GraphDecl)
    assert isinstance(abstract_syntax_tree.children[1], Algorithm)
    assert isinstance(abstract_syntax_tree.children[2], DeclarationInit)
    assert isinstance(abstract_syntax_tree.children[3], ASTNode) # EOF $ object