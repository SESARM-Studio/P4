import pytest

from parser.gsl_parser import *
from parser.ast_builder import *

def test_base_case_recursive():
    # Arrange
    input_string = "Grandfather Father Son Grandson"
    terminal = gsl_parser.Terminal("Granddad", 0,11)
    ast = AbstractSyntaxTreeBuilder(input_string)
    stack = [terminal]
    expected_type = ASTNode

    # Act
    return_node = ast.build_tree(stack)

    # Assert
    assert isinstance(return_node, expected_type), f"expected: {expected_type} actual: {return_node.__class__.__name__}"
    assert terminal.name == return_node.token
    assert ast.characters(terminal.getBegin(), terminal.getEnd()) == return_node.value
    assert len(return_node.children) == 0

def test_nonterminal_recursive():
    # Arrange
    input_string = "Parent Son Daughter Stepson"
    terminal1 = gsl_parser.Terminal("Son", 12, 14)
    terminal2 = gsl_parser.Terminal("Daughter", 16, 23)
    terminal3 = gsl_parser.Terminal("Stepson", 25, 31)
    nonterminal = gsl_parser.Nonterminal("Parent", 0, 10, [terminal1, terminal2, terminal3])

    ast = AbstractSyntaxTreeBuilder(input_string)
    stack = [nonterminal]
    expected_type = ASTNode

    # Act
    return_node = ast.build_tree(stack)

    # Assert
    assert isinstance(return_node, expected_type), f"expected: {expected_type} actual: {return_node.__class__.__name__}"
    assert len(return_node.children) == 3

def test_has_skip_children():
    # Arrange
    input_string = "Bob James, (Angela)"
    terminal5 = gsl_parser.Terminal("')'", 18,19)
    terminal4 = gsl_parser.Terminal("Daughter", 12,17)
    terminal3 = gsl_parser.Terminal("'('", 11,12)
    terminal2 = gsl_parser.Terminal("','", 9,10)
    terminal1 = gsl_parser.Terminal("Son", 4,8)
    non_terminal = gsl_parser.Nonterminal("Parent",0,2, [terminal1, terminal2, terminal3, terminal4, terminal5])

    ast = AbstractSyntaxTreeBuilder(input_string)
    stack = [non_terminal]

    # Act
    return_node = ast.build_tree(stack)

    # Assert
    assert 2 == len(return_node.children)

def test_only_skip_children():
    # Arrange
    input_string = "Bob, ()"
    terminal3 = gsl_parser.Terminal("')'", 6,7)
    terminal2 = gsl_parser.Terminal("'('", 5,6)
    terminal1 = gsl_parser.Terminal("','", 3,4)
    non_terminal = gsl_parser.Nonterminal("Parent",0,2, [terminal1,terminal2,terminal3])

    ast = AbstractSyntaxTreeBuilder(input_string)
    stack = [non_terminal]

    # Act
    return_node = ast.build_tree(stack)

    # Assert
    assert 0 == len(return_node.children)

def test_replace_parent():
    # Arrange
    input_string = "Grandfather Father Son Grandson"
    
    terminal1 = gsl_parser.Terminal("Grandchild", 23, 31)
    nonterminal1 = gsl_parser.Nonterminal("Junior", 19, 21, [terminal1])
    nonterminal2 = gsl_parser.Nonterminal("Dad", 12, 17, [nonterminal1])
    nonterminal3 = gsl_parser.Nonterminal("Granddad", 0, 10, [nonterminal2])
    
    ast = AbstractSyntaxTreeBuilder(input_string)
    stack = [nonterminal3]
    expected_type = ASTNode

    # Act
    return_node = ast.build_tree(stack)

    # Assert
    assert isinstance(return_node, expected_type), f"expected: {expected_type} actual: {return_node.__class__.__name__}"
    assert len(return_node.children) == 0
    assert return_node.value == "Grandson"

def test_if_statement_wo_else():
    # Arrange
    expected = IfStatement("IfStatement")
    input_string = "if a > 0 then @NEWLINE @INDENT b := 10 @NEWLINE @DEDENT $"
    b = gsl_parser.ParseTreeBuilder()
    parser = gsl_parser(input_string, b)
    ast = AbstractSyntaxTreeBuilder(input_string)
    parser.parse_Program()
    rex_if_node = b.stack[0].children[0].children[0] # Program -> Statement -> IfStatement

    # Act
    result = ast.recursive_builder(rex_if_node)

    # Assert
    assert type(result) == type(expected)
    assert result.condition is not None
    assert result.then_statements != []
    assert result.else_statements == []

def test_if_statement_w_else():
    # Arrange
    expected = IfStatement("IfStatement")
    input_string = "if a = 100 then @NEWLINE @INDENT subtraction(a,b) @NEWLINE @DEDENT else @NEWLINE @INDENT a := a + 1 @NEWLINE @DEDENT $"
    b = gsl_parser.ParseTreeBuilder()
    parser = gsl_parser(input_string, b)
    ast = AbstractSyntaxTreeBuilder(input_string)
    parser.parse_Program()
    rex_if_node = b.stack[0].children[0].children[0] # Program -> Statement -> IfStatement

    # Act
    result = ast.recursive_builder(rex_if_node)

    # Assert
    assert type(result) == type(expected)
    assert result.condition is not None
    assert result.then_statements != []
    assert result.else_statements != []

def test_while_statement():
    # Arrange
    expected = WhileStatement("WhileStatement")
    input_string = "while a > 0 then @NEWLINE @INDENT a := a - 1 @NEWLINE @DEDENT $"
    b = gsl_parser.ParseTreeBuilder()
    parser = gsl_parser(input_string, b)
    ast = AbstractSyntaxTreeBuilder(input_string)
    parser.parse_Program()
    rex_while_node = b.stack[0].children[0].children[0] # Program -> Statement -> WhileStatement

    # Act
    result = ast.recursive_builder(rex_while_node)

    # Assert
    assert type(result) == type(expected)
    assert result.condition is not None
    assert result.statements != []

def test_repeat_statement():
    # Arrange
    expected = RepeatStatement("RepeatStatement")
    input_string = "repeat 5 times @NEWLINE @INDENT display 5 @NEWLINE @DEDENT $"
    b = gsl_parser.ParseTreeBuilder()
    parser = gsl_parser(input_string, b)
    ast = AbstractSyntaxTreeBuilder(input_string)
    parser.parse_Program()
    rex_repeat_node = b.stack[0].children[0].children[0] # Program -> Statement -> RepeatStatement

    # Act
    result = ast.recursive_builder(rex_repeat_node)

    # Assert
    assert type(result) == type(expected)
    assert result.repeat_expression is not None
    assert result.repeat_statements != []

def test_for_each_normal_statement():
    # Arrange
    expected = ForEachNormal("ForEachNormal")
    input_string = "for each x in [1,2,3] @NEWLINE @INDENT display x @NEWLINE @DEDENT $"
    b = gsl_parser.ParseTreeBuilder()
    parser = gsl_parser(input_string, b)
    ast = AbstractSyntaxTreeBuilder(input_string)
    parser.parse_Program()
    rex_for_each_normal_node = b.stack[0].children[0].children[0] # Program -> Statement -> ForEachNormal

    # Act
    result = ast.recursive_builder(rex_for_each_normal_node)

    # Assert
    assert type(result) == type(expected)
    assert result.loop_identifier == "x"
    assert result.iterable is not None
    assert result.statements != []

def test_for_each_edge_wo_weight_statement():
    # Arrange
    expected = ForEachEdge("ForEachEdge")
    input_string = "for each edge x --- y in G @NEWLINE @INDENT display x @NEWLINE display y @NEWLINE @DEDENT $"
    b = gsl_parser.ParseTreeBuilder()
    parser = gsl_parser(input_string, b)
    ast = AbstractSyntaxTreeBuilder(input_string)
    parser.parse_Program()
    rex_for_each_edge_node = b.stack[0].children[0].children[0] # Program -> Statement -> ForEachEdge

    # Act
    result = ast.recursive_builder(rex_for_each_edge_node)

    # Assert
    assert type(result) == type(expected)
    assert result.edge is not None
    assert result.weight_identifier is None
    assert result.graph_identifier == "G"
    assert result.statements != []

def test_for_each_edge_w_weight_statement():
    # Arrange
    expected = ForEachEdge("ForEachEdge")
    input_string = "for each edge u --- v with weight w in H @NEWLINE @INDENT display u @NEWLINE display v @NEWLINE display w @NEWLINE @DEDENT $"
    b = gsl_parser.ParseTreeBuilder()
    parser = gsl_parser(input_string, b)
    ast = AbstractSyntaxTreeBuilder(input_string)
    parser.parse_Program()
    rex_for_each_edge_node = b.stack[0].children[0].children[0] # Program -> Statement -> ForEachEdge

    # Act
    result = ast.recursive_builder(rex_for_each_edge_node)

    # Assert
    assert type(result) == type(expected)
    assert result.edge is not None
    assert result.weight_identifier == "w"
    assert result.graph_identifier == "H"
    assert result.statements != []

def test_for_each_edge_w_weight_statement():
    # Arrange
    expected = ForEachEdge("ForEachEdge")
    input_string = "for each edge u --- v with weight w in H @NEWLINE @INDENT display u @NEWLINE display v @NEWLINE display w @NEWLINE @DEDENT $"
    b = gsl_parser.ParseTreeBuilder()
    parser = gsl_parser(input_string, b)
    ast = AbstractSyntaxTreeBuilder(input_string)
    parser.parse_Program()
    rex_for_each_edge_node = b.stack[0].children[0].children[0] # Program -> Statement -> ForEachEdge

    # Act
    result = ast.recursive_builder(rex_for_each_edge_node)

    # Assert
    assert type(result) == type(expected)
    assert result.edge is not None
    assert result.weight_identifier == "w"
    assert result.graph_identifier == "H"
    assert result.statements != []

def test_graph_decl_wo_weight_wo_nodes_wo_edges():
    # Arrange
    expected = GraphDecl("GraphDecl")
    input_string = "graph G @NEWLINE $"
    b = gsl_parser.ParseTreeBuilder()
    parser = gsl_parser(input_string, b)
    ast = AbstractSyntaxTreeBuilder(input_string)
    parser.parse_Program()
    rex_graph_decl_node = b.stack[0].children[0].children[0] # Program -> Statement -> GraphDecl

    # Act
    result = ast.recursive_builder(rex_graph_decl_node)

    # Assert
    assert type(result) == type(expected)
    assert result.graph_type == "graph"
    assert result.identifier == "G"
    assert result.weight_type is None
    assert result.nodes == []
    assert result.edges == []

def test_digraph_decl_wo_weight_wo_nodes_wo_edges():
    # Arrange
    expected = GraphDecl("GraphDecl")
    input_string = "digraph G @NEWLINE $"
    b = gsl_parser.ParseTreeBuilder()
    parser = gsl_parser(input_string, b)
    ast = AbstractSyntaxTreeBuilder(input_string)
    parser.parse_Program()
    rex_graph_decl_node = b.stack[0].children[0].children[0] # Program -> Statement -> GraphDecl

    # Act
    result = ast.recursive_builder(rex_graph_decl_node)

    # Assert
    assert type(result) == type(expected)
    assert result.graph_type == "digraph"
    assert result.identifier == "G"
    assert result.weight_type is None
    assert result.nodes == []
    assert result.edges == []

def test_graph_decl_w_weight_wo_nodes_wo_edges():
    # Arrange
    expected = GraphDecl("GraphDecl")
    input_string = "graph G with int weight @NEWLINE $"
    b = gsl_parser.ParseTreeBuilder()
    parser = gsl_parser(input_string, b)
    ast = AbstractSyntaxTreeBuilder(input_string)
    parser.parse_Program()
    rex_graph_decl_node = b.stack[0].children[0].children[0] # Program -> Statement -> GraphDecl

    # Act
    result = ast.recursive_builder(rex_graph_decl_node)

    # Assert
    assert type(result) == type(expected)
    assert result.graph_type == "graph"
    assert result.identifier == "G"
    assert result.weight_type == "int"
    assert result.nodes == []
    assert result.edges == []

def test_graph_decl_wo_weight_w_nodes_wo_edges():
    # Arrange
    expected = GraphDecl("GraphDecl")
    input_string = "graph G @NEWLINE @INDENT node a,b,c @NEWLINE @DEDENT $"
    b = gsl_parser.ParseTreeBuilder()
    parser = gsl_parser(input_string, b)
    ast = AbstractSyntaxTreeBuilder(input_string)
    parser.parse_Program()
    rex_graph_decl_node = b.stack[0].children[0].children[0] # Program -> Statement -> GraphDecl

    # Act
    result = ast.recursive_builder(rex_graph_decl_node)

    # Assert
    assert type(result) == type(expected)
    assert result.graph_type == "graph"
    assert result.identifier == "G"
    assert result.weight_type is None
    assert result.nodes != []
    assert result.edges == []

def test_graph_decl_wo_weight_wo_nodes_w_edges():
    # Arrange
    expected = GraphDecl("GraphDecl")
    input_string = "graph G @NEWLINE @INDENT edge a---b @NEWLINE @DEDENT $"
    b = gsl_parser.ParseTreeBuilder()
    parser = gsl_parser(input_string, b)
    ast = AbstractSyntaxTreeBuilder(input_string)
    parser.parse_Program()
    rex_graph_decl_node = b.stack[0].children[0].children[0] # Program -> Statement -> GraphDecl

    # Act
    result = ast.recursive_builder(rex_graph_decl_node)

    # Assert
    assert type(result) == type(expected)
    assert result.graph_type == "graph"
    assert result.identifier == "G"
    assert result.weight_type is None
    assert result.nodes == []
    assert result.edges != []

def test_graph_decl_w_weight_w_nodes_w_edges():
    # Arrange
    expected = GraphDecl("GraphDecl")
    input_string = "graph G with nat weight @NEWLINE @INDENT node x,y,z @NEWLINE edge x---y weight 10 @NEWLINE edge y---z weight 20 @NEWLINE @DEDENT $"
    b = gsl_parser.ParseTreeBuilder()
    parser = gsl_parser(input_string, b)
    ast = AbstractSyntaxTreeBuilder(input_string)
    parser.parse_Program()
    rex_graph_decl_node = b.stack[0].children[0].children[0] # Program -> Statement -> GraphDecl

    # Act
    result = ast.recursive_builder(rex_graph_decl_node)

    # Assert
    assert type(result) == type(expected)
    assert result.graph_type == "graph"
    assert result.identifier == "G"
    assert result.weight_type == "nat"
    assert result.nodes != []
    assert result.edges != []

def test_display_statement():
    # Arrange
    expected = DisplayStatement("DisplayStatement")
    input_string = "display 1 @NEWLINE $"
    b = gsl_parser.ParseTreeBuilder()
    parser = gsl_parser(input_string, b)
    ast = AbstractSyntaxTreeBuilder(input_string)
    parser.parse_Program()
    rex_display_node = b.stack[0].children[0].children[0] # Program -> Statement -> DisplayStatement

    # Act
    result = ast.recursive_builder(rex_display_node)

    # Assert
    assert type(result) == type(expected)
    assert result.expression is not None

def test_return_statement():
    # Arrange
    expected = ReturnStatement("ReturnStatement")
    input_string = "return x @NEWLINE $"
    b = gsl_parser.ParseTreeBuilder()
    parser = gsl_parser(input_string, b)
    ast = AbstractSyntaxTreeBuilder(input_string)
    parser.parse_Program()
    rex_return_node = b.stack[0].children[0].children[0] # Program -> Statement -> ReturnStatement

    # Act
    result = ast.recursive_builder(rex_return_node)

    # Assert
    assert type(result) == type(expected)
    assert result.expression is not None

def test_graph_statement_add_node():
    # Arrange
    expected = GraphStatement("GraphStatement")
    input_string = "G add node a @NEWLINE $"
    b = gsl_parser.ParseTreeBuilder()
    parser = gsl_parser(input_string, b)
    ast = AbstractSyntaxTreeBuilder(input_string)
    parser.parse_Program()
    rex_graph_statement_node = b.stack[0].children[0].children[0] # Program -> Statement -> GraphStatement

    # Act
    result = ast.recursive_builder(rex_graph_statement_node)

    # Assert
    assert type(result) == type(expected)
    assert result.graph_identifier == "G"
    assert result.operator == "add"
    assert result.argument is not None

def test_graph_statement_add_edge():
    # Arrange
    expected = GraphStatement("GraphStatement")
    input_string = "G add edge a---b @NEWLINE $"
    b = gsl_parser.ParseTreeBuilder()
    parser = gsl_parser(input_string, b)
    ast = AbstractSyntaxTreeBuilder(input_string)
    parser.parse_Program()
    rex_graph_statement_node = b.stack[0].children[0].children[0] # Program -> Statement -> GraphStatement

    # Act
    result = ast.recursive_builder(rex_graph_statement_node)

    # Assert
    assert type(result) == type(expected)
    assert result.graph_identifier == "G"
    assert result.operator == "add"
    assert result.argument is not None

def test_graph_statement_remove_node():
    # Arrange
    expected = GraphStatement("GraphStatement")
    input_string = "G remove node a @NEWLINE $"
    b = gsl_parser.ParseTreeBuilder()
    parser = gsl_parser(input_string, b)
    ast = AbstractSyntaxTreeBuilder(input_string)
    parser.parse_Program()
    rex_graph_statement_node = b.stack[0].children[0].children[0] # Program -> Statement -> GraphStatement

    # Act
    result = ast.recursive_builder(rex_graph_statement_node)

    # Assert
    assert type(result) == type(expected)
    assert result.graph_identifier == "G"
    assert result.operator == "remove"
    assert result.argument is not None

def test_graph_statement_remove_edge():
    # Arrange
    expected = GraphStatement("GraphStatement")
    input_string = "G remove edge a---b @NEWLINE $"
    b = gsl_parser.ParseTreeBuilder()
    parser = gsl_parser(input_string, b)
    ast = AbstractSyntaxTreeBuilder(input_string)
    parser.parse_Program()
    rex_graph_statement_node = b.stack[0].children[0].children[0] # Program -> Statement -> GraphStatement

    # Act
    result = ast.recursive_builder(rex_graph_statement_node)

    # Assert
    assert type(result) == type(expected)
    assert result.graph_identifier == "G"
    assert result.operator == "remove"
    assert result.argument is not None

def test_edge_decl_undirected_to_1node_wo_weight():
    # Arrange
    expected = EdgeDecl("EdgeDecl")
    input_string = "edge a---b @NEWLINE $"
    b = gsl_parser.ParseTreeBuilder()
    parser = gsl_parser(input_string, b)
    ast = AbstractSyntaxTreeBuilder(input_string)
    parser.parse_Program()
    rex_edge_decl_node = b.stack[0].children[0].children[0] # Program -> Statement -> EdgeDecl

    # Act
    result = ast.recursive_builder(rex_edge_decl_node)

    # Assert
    assert type(result) == type(expected)
    assert result.initial_node == "a"
    assert result.nodes == ["b"]
    assert result.direction == "---"
    assert result.weight == []

def test_edge_decl_undirected_to_2node_wo_weight():
    # Arrange
    expected = EdgeDecl("EdgeDecl")
    input_string = "edge a---b,c @NEWLINE $"
    b = gsl_parser.ParseTreeBuilder()
    parser = gsl_parser(input_string, b)
    ast = AbstractSyntaxTreeBuilder(input_string)
    parser.parse_Program()
    rex_edge_decl_node = b.stack[0].children[0].children[0] # Program -> Statement -> EdgeDecl

    # Act
    result = ast.recursive_builder(rex_edge_decl_node)

    # Assert
    assert type(result) == type(expected)
    assert result.initial_node == "a"
    assert result.nodes == ["b", "c"]
    assert result.direction == "---"
    assert result.weight == []

def test_edge_decl_undirected_to_1node_w_weight():
    # Arrange
    expected = EdgeDecl("EdgeDecl")
    input_string = "edge a---b weight 10 @NEWLINE $"
    b = gsl_parser.ParseTreeBuilder()
    parser = gsl_parser(input_string, b)
    ast = AbstractSyntaxTreeBuilder(input_string)
    parser.parse_Program()
    rex_edge_decl_node = b.stack[0].children[0].children[0] # Program -> Statement -> EdgeDecl

    # Act
    result = ast.recursive_builder(rex_edge_decl_node)

    # Assert
    assert type(result) == type(expected)
    assert result.initial_node == "a"
    assert result.nodes == ["b"]
    assert result.direction == "---"
    assert result.weight != []

def test_edge_decl_undirected_to_2node_w_weight():
    # Arrange
    expected = EdgeDecl("EdgeDecl")
    input_string = "edge a---b,c weight 10, 15 @NEWLINE $"
    b = gsl_parser.ParseTreeBuilder()
    parser = gsl_parser(input_string, b)
    ast = AbstractSyntaxTreeBuilder(input_string)
    parser.parse_Program()
    rex_edge_decl_node = b.stack[0].children[0].children[0] # Program -> Statement -> EdgeDecl

    # Act
    result = ast.recursive_builder(rex_edge_decl_node)

    # Assert
    assert type(result) == type(expected)
    assert result.initial_node == "a"
    assert result.nodes == ["b", "c"]
    assert result.direction == "---"
    assert result.weight != []

def test_edge_decl_directed_to_1node_wo_weight():
    # Arrange
    expected = EdgeDecl("EdgeDecl")
    input_string = "edge a-->b @NEWLINE $"
    b = gsl_parser.ParseTreeBuilder()
    parser = gsl_parser(input_string, b)
    ast = AbstractSyntaxTreeBuilder(input_string)
    parser.parse_Program()
    rex_edge_decl_node = b.stack[0].children[0].children[0] # Program -> Statement -> EdgeDecl

    # Act
    result = ast.recursive_builder(rex_edge_decl_node)

    # Assert
    assert type(result) == type(expected)
    assert result.initial_node == "a"
    assert result.nodes == ["b"]
    assert result.direction == "-->"
    assert result.weight == []

def test_edge_decl_directed_to_2node_wo_weight():
    # Arrange
    expected = EdgeDecl("EdgeDecl")
    input_string = "edge a-->b,c @NEWLINE $"
    b = gsl_parser.ParseTreeBuilder()
    parser = gsl_parser(input_string, b)
    ast = AbstractSyntaxTreeBuilder(input_string)
    parser.parse_Program()
    rex_edge_decl_node = b.stack[0].children[0].children[0] # Program -> Statement -> EdgeDecl

    # Act
    result = ast.recursive_builder(rex_edge_decl_node)

    # Assert
    assert type(result) == type(expected)
    assert result.initial_node == "a"
    assert result.nodes == ["b", "c"]
    assert result.direction == "-->"
    assert result.weight == []

def test_edge_decl_directed_to_1node_w_weight():
    # Arrange
    expected = EdgeDecl("EdgeDecl")
    input_string = "edge a-->b weight 30 @NEWLINE $"
    b = gsl_parser.ParseTreeBuilder()
    parser = gsl_parser(input_string, b)
    ast = AbstractSyntaxTreeBuilder(input_string)
    parser.parse_Program()
    rex_edge_decl_node = b.stack[0].children[0].children[0] # Program -> Statement -> EdgeDecl

    # Act
    result = ast.recursive_builder(rex_edge_decl_node)

    # Assert
    assert type(result) == type(expected)
    assert result.initial_node == "a"
    assert result.nodes == ["b"]
    assert result.direction == "-->"
    assert result.weight != []

def test_edge_decl_directed_to_2node_w_weight():
    # Arrange
    expected = EdgeDecl("EdgeDecl")
    input_string = "edge a-->b,c weight 50, 100 @NEWLINE $"
    b = gsl_parser.ParseTreeBuilder()
    parser = gsl_parser(input_string, b)
    ast = AbstractSyntaxTreeBuilder(input_string)
    parser.parse_Program()
    rex_edge_decl_node = b.stack[0].children[0].children[0] # Program -> Statement -> EdgeDecl

    # Act
    result = ast.recursive_builder(rex_edge_decl_node)

    # Assert
    assert type(result) == type(expected)
    assert result.initial_node == "a"
    assert result.nodes == ["b", "c"]
    assert result.direction == "-->"
    assert result.weight != []

def test_edge_loop_undirected():
    # Arrange
    expected = EdgeLoop("EdgeLoop")
    input_string = "for each edge a---b in G @NEWLINE @INDENT display a @NEWLINE @DEDENT $"
    b = gsl_parser.ParseTreeBuilder()
    parser = gsl_parser(input_string, b)
    ast = AbstractSyntaxTreeBuilder(input_string)
    parser.parse_Program()
    rex_edge_loop_node = b.stack[0].children[0].children[0].children[1] # Program -> Statement -> ForEachEdge -> EdgeLoop

    # Act
    result = ast.recursive_builder(rex_edge_loop_node)

    # Assert
    assert type(result) == type(expected)
    assert result.initial_node == "a"
    assert result.last_node == "b"
    assert result.direction == "---"

def test_edge_loop_directed():
    # Arrange
    expected = EdgeLoop("EdgeLoop")
    input_string = "for each edge a-->b in G @NEWLINE @INDENT display a @NEWLINE @DEDENT $"
    b = gsl_parser.ParseTreeBuilder()
    parser = gsl_parser(input_string, b)
    ast = AbstractSyntaxTreeBuilder(input_string)
    parser.parse_Program()
    rex_edge_loop_node = b.stack[0].children[0].children[0].children[1] # Program -> Statement -> ForEachEdge -> EdgeLoop

    # Act
    result = ast.recursive_builder(rex_edge_loop_node)

    # Assert
    assert type(result) == type(expected)
    assert result.initial_node == "a"
    assert result.last_node == "b"
    assert result.direction == "-->"

def test_algorithm_wo_parameters_wo_returntype():
    # Arrange
    expected = Algorithm("Algorithm")
    input_string = "algo hello_world() @NEWLINE @INDENT display \"Hello World!\" @NEWLINE @DEDENT $"
    b = gsl_parser.ParseTreeBuilder()
    parser = gsl_parser(input_string, b)
    ast = AbstractSyntaxTreeBuilder(input_string)
    parser.parse_Program()
    rex_algorithm_node = b.stack[0].children[0].children[0] # Program -> Statement -> Algorithm

    # Act
    result = ast.recursive_builder(rex_algorithm_node)

    # Assert
    assert type(result) == type(expected)
    assert result.identifier == "hello_world"
    assert result.parameters == []
    assert result.return_type is None
    assert result.statements != []

def test_algorithm_w_parameters_wo_returntype():
    # Arrange
    expected = Algorithm("Algorithm")
    input_string = "algo display_text(text input) @NEWLINE @INDENT display input @NEWLINE @DEDENT $"
    b = gsl_parser.ParseTreeBuilder()
    parser = gsl_parser(input_string, b)
    ast = AbstractSyntaxTreeBuilder(input_string)
    parser.parse_Program()
    rex_algorithm_node = b.stack[0].children[0].children[0] # Program -> Statement -> Algorithm

    # Act
    result = ast.recursive_builder(rex_algorithm_node)

    # Assert
    assert type(result) == type(expected)
    assert result.identifier == "display_text"
    assert result.parameters != []
    assert result.return_type is None
    assert result.statements != []

def test_algorithm_wo_parameters_w_returntype():
    # Arrange
    expected = Algorithm("Algorithm")
    input_string = "algo pi() returns real @NEWLINE @INDENT return 3.14 @NEWLINE @DEDENT $"
    b = gsl_parser.ParseTreeBuilder()
    parser = gsl_parser(input_string, b)
    ast = AbstractSyntaxTreeBuilder(input_string)
    parser.parse_Program()
    rex_algorithm_node = b.stack[0].children[0].children[0] # Program -> Statement -> Algorithm

    # Act
    result = ast.recursive_builder(rex_algorithm_node)

    # Assert
    assert type(result) == type(expected)
    assert result.identifier == "pi"
    assert result.parameters == []
    assert result.return_type == "real"
    assert result.statements != []

def test_algorithm_w_parameters_w_returntype():
    # Arrange
    expected = Algorithm("Algorithm")
    input_string = "algo addition(a in int, b in int) returns int @NEWLINE @INDENT return a+b @NEWLINE @DEDENT $"
    b = gsl_parser.ParseTreeBuilder()
    parser = gsl_parser(input_string, b)
    ast = AbstractSyntaxTreeBuilder(input_string)
    parser.parse_Program()
    rex_algorithm_node = b.stack[0].children[0].children[0] # Program -> Statement -> Algorithm

    # Act
    result = ast.recursive_builder(rex_algorithm_node)

    # Assert
    assert type(result) == type(expected)
    assert result.identifier == "addition"
    assert result.parameters != []
    assert result.return_type == "int"
    assert result.statements != []

def test_parameter():
    # Arrange
    expected = Parameter("Parameter")
    input_string = "algo display_text(text input) @NEWLINE @INDENT display input @NEWLINE @DEDENT $"
    b = gsl_parser.ParseTreeBuilder()
    parser = gsl_parser(input_string, b)
    ast = AbstractSyntaxTreeBuilder(input_string)
    parser.parse_Program()
    rex_parameter_node = b.stack[0].children[0].children[0].children[3] # Program -> Statement -> Algorithm -> Parameter

    # Act
    result = ast.recursive_builder(rex_parameter_node)

    # Assert
    assert type(result) == type(expected)
    assert result.identifier == "input"
    assert result.type == "text"

def test_loop_modifier():
    # Arrange
    expected = LoopModifier("LoopModifier")
    input_string = "stop @NEWLINE $"
    b = gsl_parser.ParseTreeBuilder()
    parser = gsl_parser(input_string, b)
    ast = AbstractSyntaxTreeBuilder(input_string)
    parser.parse_Program()
    rex_loop_modifier_node = b.stack[0].children[0].children[0] # Program -> Statement -> LoopModifier

    # Act
    result = ast.recursive_builder(rex_loop_modifier_node)

    # Assert
    assert type(result) == type(expected)
    assert result.modifier == "stop"
