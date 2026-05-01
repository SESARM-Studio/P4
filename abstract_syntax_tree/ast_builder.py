class ASTNode:
    def __init__(self, token, children=None, value=None):
        self.token = token
        self.value = value
        self.children = children or []
        self.parent = None

        for c in self.children:
            c.parent = self

class IfStatement(ASTNode):
    def __init__(self, token):
        super().__init__(token)
        self.if_part = None
        self.then_part = []
        self.else_part = []

class WhileStatement(ASTNode):
    def __init__(self, token):
        super().__init__(token)
        self.condition = []
        self.statements = []

class RepeatStatement(ASTNode):
    def __init__(self, token):
        super().__init__(token)
        self.repeat_expression = None
        self.repeat_statements = []

class ForEachNormal(ASTNode):
    def __init__(self, token):
        super().__init__(token)
        self.loop_variable = None
        self.iterable = []
        self.statements = []


class ForEachEdge(ASTNode):
    def __init__(self, token):
        super().__init__(token)
        self.edge = []
        self.weight_identifier = None
        self.graph_identifier = None
        self.statements = []

class GraphDecl(ASTNode):
    def __init__(self, token):
        super().__init__(token)
        self.graph_type = None
        self.variable = None
        self.weight_type = None
        self.nodes = []
        self.edges = []

class DisplayStatement(ASTNode):
    def __init__(self, token):
        super().__init__(token)
        self.expression = None

class ReturnStatement(ASTNode):
    def __init__(self, token):
        super().__init__(token)
        self.expression = None

class FunctionCall(ASTNode):
    def __init__(self, token):
        super().__init__(token)
        self.variable = None
        self.arguments = None

class AbsoluteValue(ASTNode):
    def __init__(self, token):
        super().__init__(token)
        self.operator = "|"
        self.expression = None

class Magnitude(ASTNode):
    def __init__(self, token):
        super().__init__(token)
        self.operator = "||"
        self.expression = None

class ArrayAccess(ASTNode):
    def __init__(self, token):
        super().__init__(token)
        self.variable = None
        self.indexes = []

class ExprChaining(ASTNode):
    def __init__(self, token):
        super().__init__(token)
        self.variable = None
        self.chain_part = None

class NodeDecl(ASTNode):
    def __init__(self, token):
        super().__init__(token)
        self.type = "node"
        self.variables = []
        self.assignment = None

class GraphStatment(ASTNode):
    def __init__(self, token):
        super().__init__(token)
        self.graph_variable = None
        self.operator = None
        self.argument = []

class ExprNode(ASTNode):
    def __init__(self, token):
        super().__init__(token)
        self.variable = []
        self.direction = None

class EdgeDecl(ASTNode):
    def __init__(self, token):
        super().__init__(token)
        self.type = "edge"
        self.initial_node = None
        self.nodes = []
        self.direction = None
        self.weight = []

class Algorithm(ASTNode):
    def __init__(self, token):
        super().__init__(token)
        self.variable = None
        self.parameters = []
        self.return_type = None
        self.statements = []

class Parameter(ASTNode):
    def __init__(self, token):
        super().__init__(token)
        self.type = None
        self.variable = None
        
class LoopModifier(ASTNode):
    def __init__(self, token):
        super().__init__(token)
        self.modifier = None

class Declaration(ASTNode):
    def __init__(self, token):
        super().__init__(token)
        self.variables = []
        self.type = None
        self.is_list = False
        self.dimension = None

class DeclarationInitialization(Declaration):
    def __init__(self, token):
        super().__init__(token)
        self.expression = []

class Assignment(ASTNode):
    def __init__(self, token):
        super().__init__(token)
        self.variable = None
        self.expression = None
        self.has_array_access = False
        self.array_access = None

class IdentifierAccess(ASTNode):
    def __init__(self, token):
        super().__init__(token)
        self.variable = None
        self.has_array_access = False
        self.array_access = None
        self.has_function_call = False
        self.function_call = None

class Expression(ASTNode):
    def __init__(self, token):
        super().__init__(token)
        self.operator = None
        self.arg1 = None
        self.arg2 = None

class Term(ASTNode):
    def __init__(self, token):
        super().__init__(token)
        self.type = None

def print_ast(node, prefix="", is_last=True):
    connector = "└── " if is_last else "├── "

    print(prefix + connector + node.token)
    new_prefix = prefix + ("    " if is_last else "│   ")

    for key, value in vars(node).items():
        if isinstance(value, ASTNode):
            if key == "parent":
                continue
            print_ast(getattr(node, key), new_prefix)
            continue
        if isinstance(value, list) and not getattr(node, key):
            continue
        if isinstance(value, list) and isinstance(value[0], ASTNode):
            if len(getattr(node, key)) > 1:
                for index, child in enumerate(getattr(node, key)):
                    if index == len(getattr(node, key))-1:
                        print_ast(child, new_prefix, True)
                    else:
                        print_ast(child, new_prefix, False)
            else:
                for child in getattr(node, key):
                    print_ast(child, new_prefix, True)
            continue
        if isinstance(value, list) and not isinstance(value[0], ASTNode):
            print(prefix + "    " + connector + str(getattr(node, key)))
            continue
        else:
            if value == None or value == node.token:
                continue
            print(prefix + "    " + connector + str(value))


# Class for the abstract syntax
class AbstractSyntaxTreeBuilder:
    def __init__(self, input_string):
        self.input = input_string

    # After parsing completes successfully, the single remaining node in the stack is the non-terminal representing the start symbol.
    # Therefore, the AST is build on the single element in the stack.
    def build_tree(self, stack):
        if not stack:
            exit("Stack is empty")
        if len(stack) > 1:
            exit("Stack should only contain 1 element")
        program = stack[0]
        return self.recursive_builder(program)

    # Splices the input_string from begin to end index, and returns that string.
    def characters(self, b, e):
        return self.input[b:e]
    
    # Recursive function, which builds the AST from last non-terminal of the stack, in the ASTNode format.
    def recursive_builder(self, symbol):
        symbol_children = []
        accepted_children = []

        # Base case: If symbol does not have attribute children, it is a terminal.
        if hasattr(symbol, "children") is False:
            return ASTNode(symbol.name, [], self.characters(symbol.getBegin(), symbol.getEnd()))

        # Creates a new array of the symbols children, and reduces redundant tokens.
        for child in symbol.children:
            if child.name not in self.SKIP_WORDS:
                symbol_children.append(child)

        match symbol.name:
            case "IfStatement":
                if_statement = IfStatement(symbol.name)
                if_index = then_index = else_index = None
                for index, child in enumerate(symbol_children):
                    match child.name:
                        case "'if'":
                            if_index = index
                        case "'then'":
                            then_index = index
                        case "'else'":
                            else_index = index
                for child in symbol_children[if_index+1:then_index]:
                    if_statement.if_part = self.recursive_builder(child)
                if else_index is not None:
                    for child in symbol_children[then_index+1:else_index]:
                        if_statement.then_part.append(self.recursive_builder(child))
                    for child in symbol_children[else_index+1:]:
                        if_statement.else_part.append(self.recursive_builder(child))
                else:
                    for child in symbol_children[then_index+1:]:
                        if_statement.then_part.append(self.recursive_builder(child))
                return if_statement
            case "WhileStatement":
                while_statement = WhileStatement(symbol.name)
                for child in symbol_children:
                    match child.name:
                        case "Expression":
                            while_statement.condition = self.recursive_builder(child)
                        case "Statement":
                            while_statement.statements.append(self.recursive_builder(child))
                return while_statement
            case "ForEachNormal":
                for_each_normal = ForEachNormal(symbol.name)
                for child in symbol_children:
                    match child.name:
                        case "IDENTIFIER":
                            for_each_normal.loop_variable = self.characters(child.begin, child.end)
                        case "Expression":
                            for_each_normal.iterable = self.recursive_builder(child)
                        case "Statement":
                            for_each_normal.statements.append(self.recursive_builder(child))
                return for_each_normal
            case "ForEachEdge":
                for_each_edge = ForEachEdge(symbol.name)
                for index, child in enumerate(symbol_children):
                    match child.name:
                        case "EdgeDecl":
                            for_each_edge.edge.append(self.recursive_builder(child))
                        case "'with weight'":
                            for_each_edge.weight_identifier = self.characters(symbol_children[index+1].begin, symbol_children[index+1].end)
                        case "'in'":
                            for_each_edge.graph_identifier = self.characters(symbol_children[index+1].begin, symbol_children[index+1].end)
                        case "Statement":
                            for_each_edge.statements.append(self.recursive_builder(child))
                return for_each_edge
            case "RepeatStatement":
                repeat_statement = RepeatStatement(symbol.name)
                for child in symbol_children:
                    match child.name:
                        case "Expression":
                            repeat_statement.repeat_expression = self.recursive_builder(child)
                        case "Statement":
                            repeat_statement.repeat_statements.append(self.recursive_builder(child))
                return repeat_statement
            case "GraphDecl":
                graph_decl = GraphDecl(symbol.name)
                for child in symbol_children:
                    match child.name:
                        case "TYPE_GRAPH":
                            graph_decl.graph_type = self.characters(child.begin, child.end)
                        case "IDENTIFIER":
                            graph_decl.variable = self.characters(child.begin, child.end)
                        case "TYPE_ARITH":
                            graph_decl.weight_type = self.characters(child.begin, child.end)
                        case "NodeDecl":
                            graph_decl.nodes.append(self.recursive_builder(child))
                        case "EdgeDecl":
                            graph_decl.edges.append(self.recursive_builder(child))
                return graph_decl
            case "DisplayStatement":
                display_statement = DisplayStatement(symbol.name)
                for child in symbol_children:
                    if child.name == "Expression":
                        display_statement.expression = self.recursive_builder(child)
                return display_statement
            case "ReturnStatement":
                return_statement = ReturnStatement(symbol.name)
                for child in symbol_children:
                    if child.name == "Expression":
                        return_statement.expression = self.recursive_builder(child)
                return return_statement
            case "Expression":
                expression = Expression(symbol.name)
                for index, child in enumerate(symbol_children):
                    match child.name:
                        case "ExprAnd":
                            if index == 0:
                                expression.arg1 = self.recursive_builder(child)
                            else:
                                expression.arg2 = self.recursive_builder(child)
                        case "'or'":
                            expression.operator = self.characters(child.begin, child.end)
                        case "'weight of'":
                            expression.operator = self.characters(child.begin, child.end)
                            argument_str = ""
                            for child1 in symbol_children[index+1:]:
                                argument_str += self.characters(child1.begin, child1.end)
                            expression.arg1 = argument_str
                return expression
            case "ExprAnd":
                if len(symbol_children) > 1:
                    expr_and = Expression(symbol.name)
                for index, child in enumerate(symbol_children):
                    match child.name:
                        case "ExprEq":
                            if len(symbol_children) == 1:
                                return self.recursive_builder(child)
                            if index == 0 and len(symbol_children) > 1:
                                expr_and.arg1 = self.recursive_builder(child)
                            else:
                                expr_and.arg2 = self.recursive_builder(child)
                        case "'and'":
                            expr_and.operator = self.characters(child.begin, child.end)
                return expr_and
            case "ExprEq":
                if len(symbol_children) > 1:
                    expr_eq = Expression(symbol.name)
                for index, child in enumerate(symbol_children):
                    match child.name:
                        case "ExprRel":
                            if len(symbol_children) == 1:
                                return self.recursive_builder(child)
                            if index == 0 and len(symbol_children) > 1:
                                expr_eq.arg1 = self.recursive_builder(child)
                            else:
                                expr_eq.arg2 = self.recursive_builder(child)
                        case "'='" | "!=":
                            expr_eq.operator = self.characters(child.begin, child.end)
                return expr_eq
            case "ExprRel":
                if len(symbol_children) > 1:
                    expr_rel = Expression(symbol.name)
                for index, child in enumerate(symbol_children):
                    match child.name:
                        case "ExprPlus":
                            if len(symbol_children) == 1:
                                return self.recursive_builder(child)
                            if index == 0 and len(symbol_children) > 1:
                                expr_rel.arg1 = self.recursive_builder(child)
                            else:
                                expr_rel.arg2 = self.recursive_builder(child)
                        case "'<'" | "'>'" | "'<='" | "'>='":
                            expr_rel.operator = self.characters(child.begin, child.end)
                return expr_rel
            case "ExprPlus":
                if len(symbol_children) > 1:
                    expr_plus = Expression(symbol.name)
                for index, child in enumerate(symbol_children):
                    match child.name:
                        case "ExprMult":
                            if len(symbol_children) == 1:
                                return self.recursive_builder(child)
                            if index == 0 and len(symbol_children) > 1:
                                expr_plus.arg1 = self.recursive_builder(child)
                            else:
                                expr_plus.arg2 = self.recursive_builder(child)
                        case "'+'" | "'-'":
                            expr_plus.operator = self.characters(child.begin, child.end)
                return expr_plus
            case "ExprMult":
                if len(symbol_children) > 1:
                    expr_mult = Expression(symbol.name)
                for index, child in enumerate(symbol_children):
                    match child.name:
                        case "ExprExp":
                            if len(symbol_children) == 1:
                                return self.recursive_builder(child)
                            if index == 0 and len(symbol_children) > 1:
                                expr_mult.arg1 = self.recursive_builder(child)
                            else:
                                expr_mult.arg2 = self.recursive_builder(child)
                        case "'*'" | "'/'" | "'%'":
                            expr_mult.operator = self.characters(child.begin, child.end)
                return expr_mult
            case "ExprExp":
                if len(symbol_children) > 1:
                    expr_exp = Expression(symbol.name)
                for index, child in enumerate(symbol_children):
                    match child.name:
                        case "ExprNot":
                            if len(symbol_children) == 1:
                                return self.recursive_builder(child)
                            if index == 0 and len(symbol_children) > 1:
                                expr_exp.arg1 = self.recursive_builder(child)
                            else:
                                expr_exp.arg2 = self.recursive_builder(child)
                        case "'^'":
                            expr_exp.operator = self.characters(child.begin, child.end)
                return expr_exp
            case "ExprNot":
                if len(symbol_children) > 1:
                    expr_not = Expression(symbol.name)
                for child in symbol_children:
                    match child.name:
                        case "ExprCall":
                            if len(symbol_children) == 1:
                                return self.recursive_builder(child)
                            if len(symbol_children) > 1:
                                expr_not.arg1 = self.recursive_builder(child)
                        case "'-'" | "'neg'":
                            expr_not.operator = self.characters(child.begin, child.end)
                return expr_not
            case "ExprCall":
                for child in symbol_children:
                    return self.recursive_builder(child)
            case "AbsoluteValue":
                absolute_value = AbsoluteValue(symbol.name)
                for child in symbol_children:
                    if child.name == "Expression":
                        absolute_value.expression = self.recursive_builder(child)
                return absolute_value
            case "Magnitude":
                magnitude = Magnitude(symbol.name)
                for child in symbol_children:
                    if child.name == "Expression":
                        magnitude.expression = self.recursive_builder(child)
                return magnitude
            case "ExprChaining":
                expr_chaining = ExprChaining(symbol.name)
                variable_str = ""
                chain_part = []
                for child in symbol_children:
                    match child.name:
                        case "IDENTIFIER" | "'.'":
                            variable_str += self.characters(child.begin, child.end)
                        case "ExprCall":
                            chain_part.append(self.recursive_builder(child))
                expr_chaining.variable = variable_str
                expr_chaining.chain_part = chain_part
                return expr_chaining
            case "Term":
                term = Term(symbol.name)
                for child in symbol_children:
                    term.type = child.name
                    term.value = self.characters(child.begin, child.end)
                return term
            case "NodeDecl":
                node_decl = NodeDecl(symbol.name)
                for child in symbol_children:
                    if child.name == "IDENTIFIER":
                        node_decl.variables.append(self.characters(child.begin, child.end))
                    if child.name == "Expression":
                        node_decl.assignment = self.recursive_builder(child)
                return node_decl
            case "GraphStatement":
                expr_graph = GraphStatment(symbol.name)
                for index, child in enumerate(symbol_children):
                    if index == 0 and child.name == "IDENTIFIER":
                        expr_graph.graph_variable = self.characters(child.begin, child.end)
                    if index == 1 and child.name in ["'add'", "'remove'" ]:
                        expr_graph.operator = self.characters(child.begin, child.end)
                    if child.name == "'node'":
                        node = Declaration("Declaration")
                        node.type = self.characters(child.begin, child.end)
                        node.variables.append(self.characters(symbol_children[index+1].begin, symbol_children[index+1].end))
                        expr_graph.argument.append(node)
                    if child.name == "EdgeDecl":
                        expr_graph.argument.append(self.recursive_builder(child))
                return expr_graph
            case "ExprNode":
                expr_node = ExprNode(symbol.name)
                for child in symbol_children:
                    if child.name == "Expression":
                        expr_node.variable = self.recursive_builder(child)
                    else:
                        expr_node.direction = self.characters(child.begin, child.end).strip(")")
                return expr_node
            case "EdgeDecl":
                helper_counter = 0
                edge_decl = EdgeDecl(symbol.name)
                for child in symbol_children:
                    if child.name == "IdentifierAccess":
                        variable = self.variable_access_helper_function(child)
                        if helper_counter == 0:
                            edge_decl.initial_node = variable
                            helper_counter += 1
                        else:
                            edge_decl.nodes.append(variable)
                    if child.name in ["'-->'", "'<--'", "'<->'", "'---'"]:
                        edge_decl.direction = child.name.strip("'")
                    if child.name == "Expression":
                        edge_decl.weight.append(self.recursive_builder(child))
                return edge_decl
            case "Algorithm":
                algorithm = Algorithm(symbol.name)
                for child in symbol_children:
                    match child.name:
                        case "IDENTIFIER":
                            algorithm.variable = self.characters(child.begin, child.end)
                        case "Parameter":
                            algorithm.parameters.append(self.recursive_builder(child))
                        case "TYPE":
                            algorithm.return_type = self.characters(child.begin, child.end)
                        case "Statement":
                            algorithm.statements.append(self.recursive_builder(child))
                return algorithm
            case "Parameter":
                parameter = Parameter(symbol.name)
                for child in symbol_children:
                    match child.name:
                        case "TYPE_ARITH" | "TYPE_OTHER" | "TYPE_GRAPH" | "'node'":
                            parameter.type = self.characters(child.begin, child.end)
                        case "IDENTIFIER":
                            parameter.variable = self.characters(child.begin, child.end)
                return parameter
            case "LoopModifier":
                loop_modifier = LoopModifier(symbol.name)
                loop_modifier.modifier = self.characters(symbol.begin, symbol.end)
                return loop_modifier
            case "Declaration":
                declaration = Declaration(symbol.name)
                for child in symbol_children:
                    match child.name:
                        case "IDENTIFIER":
                            declaration.variables.append(self.characters(child.begin, child.end))
                        case "TYPE_ARITH" | "TYPE_OTHER" | "TYPE":
                            declaration.type = self.characters(child.begin, child.end)
                        case "'list'":
                            declaration.is_list = True
                        case "DIMENSION":
                            declaration.dimension = self.characters(child.begin, child.end)
                return declaration
            case "DeclarationInitialization":
                decl_init = DeclarationInitialization(symbol.name)
                for child in symbol_children:
                    match child.name:
                        case "IDENTIFIER":
                            decl_init.variables.append(self.characters(child.begin, child.end))
                        case "TYPE_ARITH" | "TYPE_OTHER" | "TYPE":
                            decl_init.type = self.characters(child.begin, child.end)
                        case "'list'":
                            decl_init.is_list = True
                        case "DIMENSION":
                            decl_init.dimension = self.characters(child.begin, child.end)
                        case "Expression" | "ListExpression":
                            decl_init.expression.append(self.recursive_builder(child))
                return decl_init
            case "ListExpression":
                for child in symbol_children:
                    match child.name:
                        case "ListExpression":
                            self.recursive_builder(child)
                        case "Expression":
                            self.recursive_builder(child)
            case "Assignment":
                assignment = Assignment(symbol.name)
                for child in symbol_children:
                    match child.name:
                        case "AssignmentVariable": #Når variable er G.array[0] så er .variable = G. og .arrayaccess = ArrayAccess Class 
                            self.variable_helper_function(child, assignment)
                        case "Expression":
                            assignment.expression = self.recursive_builder(child)
                return assignment
            case "FunctionCall":
                function_call = FunctionCall(symbol.name)
                for child in symbol_children:
                    match child.name:
                        case "IDENTIFIER":
                            function_call.variable = self.characters(child.begin, child.end)
                        case "ArgList":
                            function_call.arguments = self.recursive_builder(child)
                return function_call
            case "ArgList":
                arguments = []
                for child in symbol_children:
                    arguments.append(self.recursive_builder(child))
                return arguments
            case "ArrayAccess":
                array_access = ArrayAccess(symbol.name)
                for child in symbol_children:
                    match child.name:
                        case "IDENTIFIER":
                            array_access.variable = self.characters(child.begin, child.end)
                        case "Expression":
                            array_access.indexes.append(self.recursive_builder(child))
                return array_access

        if len(symbol_children) == 1:
            return self.recursive_builder(symbol_children[0])

        for child in symbol_children:
            accepted_children.append(self.recursive_builder(child))

        # Return the non-terminal as a ASTNode with the array of ASTNode children.
        return ASTNode(symbol.name, accepted_children)


    SKIP_WORDS = [
        "'('", "')'", "','", "'@NEWLINE'", "'@INDENT'", "'@DEDENT'"
    ]

    def variable_access_helper_function(self, node):
        variable_str = ""

        identifier_access = IdentifierAccess(node.name)

        for child in node.children:
            match child.name:
                case "IDENTIFIER" | "'.'":
                    variable_str += self.characters(child.begin, child.end)
                case "ArrayAccess":
                    identifier_access.has_array_access = True
                    identifier_access.array_access = self.recursive_builder(child)
                case "FunctionCall":
                    identifier_access.has_function_call = True
                    identifier_access.function_call = self.recursive_builder(child)
        identifier_access.variable = variable_str
        return identifier_access

    
    def variable_helper_function(self, node, assignment_class):
        variable_str = ""
        for child in node.children:
            match child.name:
                case "IDENTIFIER" | "'.'":
                    variable_str += self.characters(child.begin, child.end)
                case "ArrayAccess":
                    assignment_class.has_array_access = True
                    assignment_class.array_access = self.recursive_builder(child)
        assignment_class.variable = variable_str
        return assignment_class
