from parser.gsl_parser import gsl_parser

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
        self.condition = None
        self.then_statements = []
        self.else_statements = []

class WhileStatement(ASTNode):
    def __init__(self, token):
        super().__init__(token)
        self.condition = None
        self.statements = []

class RepeatStatement(ASTNode):
    def __init__(self, token):
        super().__init__(token)
        self.repeat_expression = None
        self.repeat_statements = []

class ForEachNormal(ASTNode):
    def __init__(self, token):
        super().__init__(token)
        self.loop_identifier = None
        self.iterable = None
        self.statements = []

class ForEachEdge(ASTNode):
    def __init__(self, token):
        super().__init__(token)
        self.edge = None
        self.weight_identifier = None
        self.graph_identifier = None
        self.statements = []

class GraphDecl(ASTNode):
    def __init__(self, token):
        super().__init__(token)
        self.graph_type = None
        self.identifier = None
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

class NodeDecl(ASTNode):
    def __init__(self, token):
        super().__init__(token)
        self.identifiers = []
        self.assignment = None
        self.is_list = False
        self.type = 'NODE'

class GraphStatement(ASTNode):
    def __init__(self, token):
        super().__init__(token)
        self.graph_identifier = None
        self.operator = None
        self.argument = None

class EdgeDecl(ASTNode):
    def __init__(self, token):
        super().__init__(token)
        self.initial_node = None
        self.nodes = []
        self.direction = None
        self.weight = []

class Algorithm(ASTNode):
    def __init__(self, token):
        super().__init__(token)
        self.identifier = None
        self.parameters = []
        self.return_type = None
        self.statements = []

class Parameter(ASTNode):
    def __init__(self, token):
        super().__init__(token)
        self.type = None
        self.identifier = None
        
class LoopModifier(ASTNode):
    def __init__(self, token):
        super().__init__(token)
        self.modifier = None

class Declaration(ASTNode):
    def __init__(self, token):
        super().__init__(token)
        self.identifiers = []
        self.type = None
        self.is_list = False
        self.dimension = None

class DeclarationInit(Declaration):
    def __init__(self, token):
        super().__init__(token)
        self.expression = []

class Assignment(ASTNode):
    def __init__(self, token):
        super().__init__(token)
        self.identifiers = []
        self.expression = None

class Expression(ASTNode):
    def __init__(self, token):
        super().__init__(token)
        self.operator = None
        self.arg1 = None
        self.arg2 = None

class Term(Expression):
    def __init__(self, token):
        super().__init__(token)
        self.type = None

class IdentifierAccess(Expression):
    def __init__(self, token):
        super().__init__(token)
        self.identifiers = []

class AbsoluteValue(Expression):
    def __init__(self, token):
        super().__init__(token)
        self.expression = None

class Magnitude(Expression):
    def __init__(self, token):
        super().__init__(token)
        self.expression = None

class ListExpression(Expression):
    def __init__(self, token):
        super().__init__(token)
        self.expressions = []

class AlgorithmCall(Expression):
    def __init__(self, token):
        super().__init__(token)
        self.identifier = None
        self.arguments = None

class ArrayAccess(Expression):
    def __init__(self, token):
        super().__init__(token)
        self.identifier = None
        self.indexes = []

class ExprNode(Expression):
    def __init__(self, token):
        super().__init__(token)
        self.expression = None
        self.direction = None


def print_ast(node, prefix="", is_last=True):
    connector = "└── " if is_last else "├── "

    print(prefix + connector + node.token)
    new_prefix = prefix + ("    " if is_last else "│   ")

    for key, value in vars(node).items():
        if isinstance(value, ASTNode):
            if key == "parent":
                continue
            print_ast(getattr(node, key), new_prefix)
        elif isinstance(value, list) and not getattr(node, key):
            continue
        elif isinstance(value, list):
            if not any(isinstance(x, ASTNode) for x in getattr(node,key)):
                print(prefix + "    " + connector + str(getattr(node, key)))
            elif len(getattr(node, key)) > 1:
                for index, child in enumerate(getattr(node, key)):
                    if not isinstance(child, ASTNode):
                        print(prefix + "    " + connector + str(child))
                    elif index == len(getattr(node, key))-1:
                        print_ast(child, new_prefix, True)
                    else:
                        print_ast(child, new_prefix, False)
            else:
                for child in getattr(node, key):
                    if not isinstance(child, ASTNode):
                        print(prefix + "    " + connector + str(getattr(node, key)))
                    else:
                        print_ast(child, new_prefix, True)
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
                    if_statement.condition = self.recursive_builder(child)
                if else_index is not None:
                    for child in symbol_children[then_index+1:else_index]:
                        if_statement.then_statements.append(self.recursive_builder(child))
                    for child in symbol_children[else_index+1:]:
                        if_statement.else_statements.append(self.recursive_builder(child))
                else:
                    for child in symbol_children[then_index+1:]:
                        if_statement.then_statements.append(self.recursive_builder(child))
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
                            for_each_normal.loop_identifier = self.characters(child.begin, child.end)
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
                            for_each_edge.edge = self.recursive_builder(child)
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
                            graph_decl.identifier = self.characters(child.begin, child.end)
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
                            if len(symbol_children) > 3:
                                last_element = len(symbol_children)-1
                                expression.arg2 = self.recursive_builder(symbol_children[last_element])
                                expression.operator = self.characters(symbol_children[last_element-1].begin, symbol_children[last_element-1].end)
                                left_argument = gsl_parser.Nonterminal("Expression",0,0,symbol_children[:last_element-1])
                                expression.arg1 = self.recursive_builder(left_argument)
                                break
                            elif index == 0:
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
                        case "ExprNode":
                            expression.arg1 =self.recursive_builder(child)
                return expression
            
            case "ExprAnd":
                if len(symbol_children) > 1:
                    expr_and = Expression(symbol.name)
                for index, child in enumerate(symbol_children):
                    match child.name:
                        case "ExprEq":
                            if len(symbol_children) > 3:
                                last_element = len(symbol_children)-1
                                expr_and.arg2 = self.recursive_builder(symbol_children[last_element])
                                expr_and.operator = self.characters(symbol_children[last_element-1].begin, symbol_children[last_element-1].end)
                                left_argument = gsl_parser.Nonterminal("ExprAnd",0,0,symbol_children[:last_element-1])
                                expr_and.arg1 = self.recursive_builder(left_argument)
                                break
                            elif len(symbol_children) == 1:
                                return self.recursive_builder(child)
                            elif index == 0:
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
                            if len(symbol_children) > 3:
                                last_element = len(symbol_children)-1
                                expr_eq.arg2 = self.recursive_builder(symbol_children[last_element])
                                expr_eq.operator = self.characters(symbol_children[last_element-1].begin, symbol_children[last_element-1].end)
                                left_argument = gsl_parser.Nonterminal("ExprEq",0,0,symbol_children[:last_element-1])
                                expr_eq.arg1 = self.recursive_builder(left_argument)
                                break
                            elif len(symbol_children) == 1:
                                return self.recursive_builder(child)
                            elif index == 0:
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
                            if len(symbol_children) > 3:
                                last_element = len(symbol_children)-1
                                expr_rel.arg2 = self.recursive_builder(symbol_children[last_element])
                                expr_rel.operator = self.characters(symbol_children[last_element-1].begin, symbol_children[last_element-1].end)
                                left_argument = gsl_parser.Nonterminal("ExprRel",0,0,symbol_children[:last_element-1])
                                expr_rel.arg1 = self.recursive_builder(left_argument)
                                break
                            elif len(symbol_children) == 1:
                                return self.recursive_builder(child)
                            elif index == 0:
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
                            if len(symbol_children) > 3:
                                last_element = len(symbol_children)-1
                                expr_plus.arg2 = self.recursive_builder(symbol_children[last_element])
                                expr_plus.operator = self.characters(symbol_children[last_element-1].begin, symbol_children[last_element-1].end)
                                left_argument = gsl_parser.Nonterminal("ExprPlus",0,0,symbol_children[:last_element-1])
                                expr_plus.arg1 = self.recursive_builder(left_argument)
                                break
                            elif len(symbol_children) == 1:
                                return self.recursive_builder(child)
                            elif index == 0:
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
                            if len(symbol_children) > 3:
                                last_element = len(symbol_children)-1
                                expr_mult.arg2 = self.recursive_builder(symbol_children[last_element])
                                expr_mult.operator = self.characters(symbol_children[last_element-1].begin, symbol_children[last_element-1].end)
                                left_argument = gsl_parser.Nonterminal("ExprMult",0,0,symbol_children[:last_element-1])
                                expr_mult.arg1 = self.recursive_builder(left_argument)
                                break
                            elif len(symbol_children) == 1:
                                return self.recursive_builder(child)
                            elif index == 0:
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
                            if len(symbol_children) > 3:
                                last_element = len(symbol_children)-1
                                expr_exp.arg1 = self.recursive_builder(symbol_children[index])
                                expr_exp.operator = self.characters(symbol_children[index+1].begin, symbol_children[index+1].end)
                                right_argument = gsl_parser.Nonterminal("ExprExp",0,0,symbol_children[index+2:])
                                expr_exp.arg2 = self.recursive_builder(right_argument)
                                break
                            elif len(symbol_children) == 1:
                                return self.recursive_builder(child)
                            elif index == 0:
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
                            expr_not.arg1 = self.recursive_builder(child)
                        case "'neg'":
                            expr_not.operator = self.characters(child.begin, child.end)
                return expr_not
            
            case "ExprCall":
                for child in symbol_children:
                    return self.recursive_builder(child)
                
            case "AbsoluteValue":
                absolute_value = AbsoluteValue(symbol.name)
                for child in symbol_children:
                    match child.name:
                        case "Expression":
                            absolute_value.expression = self.recursive_builder(child)
                return absolute_value
            
            case "Magnitude":
                magnitude = Magnitude(symbol.name)
                for child in symbol_children:
                    match child.name:
                        case "Expression":
                            magnitude.expression = self.recursive_builder(child)
                return magnitude
            
            case "IdentifierAccess":
                identifier_access = IdentifierAccess(symbol.name)

                for child in symbol_children:
                    match child.name:
                        case "IDENTIFIER":
                            identifier_access.identifiers.append(self.characters(child.begin, child.end))
                        case "ArrayAccess":
                            identifier_access.identifiers.append(self.recursive_builder(child))
                        case "AlgorithmCall":
                            identifier_access.identifiers.append(self.recursive_builder(child))
                return identifier_access
            
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
                        node_decl.identifiers.append(self.characters(child.begin, child.end))
                    if child.name == "Expression":
                        node_decl.assignment = self.recursive_builder(child)
                return node_decl
            
            case "GraphStatement":
                graph_statement = GraphStatement(symbol.name)
                for index, child in enumerate(symbol_children):
                    if index == 0 and child.name == "IDENTIFIER":
                        graph_statement.graph_identifier = self.characters(child.begin, child.end)
                    if index == 1 and child.name in ["'add'", "'remove'" ]:
                        graph_statement.operator = self.characters(child.begin, child.end)
                    if child.name == "'node'":
                        node = Declaration("Declaration")
                        node.type = self.characters(child.begin, child.end)
                        node.identifiers.append(self.characters(symbol_children[index+1].begin, symbol_children[index+1].end))
                        graph_statement.argument = node
                    if child.name == "EdgeDecl":
                        graph_statement.argument = self.recursive_builder(child)
                return graph_statement
            
            case "ExprNode":
                expr_node = ExprNode(symbol.name)
                for child in symbol_children:
                    if child.name == "Expression":
                        expr_node.expression = self.recursive_builder(child)
                    else:
                        expr_node.direction = self.characters(child.begin, child.end).strip(")")
                return expr_node
            
            case "EdgeDecl":
                assigned_first_node = False
                edge_decl = EdgeDecl(symbol.name)
                for child in symbol_children:
                    if child.name == "IdentifierAccess":
                        identifier = self.recursive_builder(child)
                        if assigned_first_node is False:
                            edge_decl.initial_node = identifier
                            assigned_first_node = True
                        else:
                            edge_decl.nodes.append(identifier)
                    elif child.name == "IDENTIFIER":
                        if assigned_first_node is False:
                            edge_decl.initial_node = self.characters(child.begin, child.end)
                            assigned_first_node = True
                        else:
                            edge_decl.nodes.append(self.characters(child.begin, child.end))
                    elif child.name in ["'-->'", "'<--'", "'<->'", "'---'"]:
                        edge_decl.direction = child.name.strip("'")
                    elif child.name == "Expression":
                        edge_decl.weight.append(self.recursive_builder(child))
                return edge_decl
            
            case "Algorithm":
                algorithm = Algorithm(symbol.name)
                for child in symbol_children:
                    match child.name:
                        case "IDENTIFIER":
                            algorithm.identifier= self.characters(child.begin, child.end)
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
                            parameter.identifier= self.characters(child.begin, child.end)
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
                            declaration.identifiers.append(self.characters(child.begin, child.end))
                        case "TYPE_ARITH" | "TYPE_OTHER" | "TYPE":
                            declaration.type = self.characters(child.begin, child.end)
                        case "'list'":
                            declaration.is_list = True
                        case "DIMENSION":
                            term = Term("Term")
                            term.type = "NATURAL_NUMBER"
                            term.value = self.characters(child.begin, child.end).strip("d")
                            declaration.dimension = term
                return declaration
            
            case "DeclarationInit":
                decl_init = DeclarationInit(symbol.name)
                for child in symbol_children:
                    match child.name:
                        case "IDENTIFIER":
                            decl_init.identifiers.append(self.characters(child.begin, child.end))
                        case "TYPE_ARITH" | "TYPE_OTHER" | "TYPE":
                            decl_init.type = self.characters(child.begin, child.end)
                        case "'list'":
                            decl_init.is_list = True
                        case "DIMENSION":
                            term = Term("Term")
                            term.type = "NATURAL_NUMBER"
                            term.value = self.characters(child.begin, child.end).strip("d")
                            decl_init.dimension = term
                        case "Expression" | "ListExpression":
                            decl_init.expression.append(self.recursive_builder(child))
                return decl_init
            
            case "ListExpression":
                list_expr = ListExpression(symbol.name)
                for child in symbol_children:
                    match child.name:
                        case "Expression":
                            list_expr.expressions.append(self.recursive_builder(child))
                return list_expr
            
            case "Assignment":
                assignment = Assignment(symbol.name)
                for child in symbol_children:
                    match child.name:
                        case "AssignmentIdentifier": #Når identifierer G.array[0] så er .identifier= G. og .arrayaccess = ArrayAccess Class 
                            self.identifier_helper_function(child, assignment)
                        case "Expression":
                            assignment.expression = self.recursive_builder(child)
                return assignment
            
            case "AlgorithmCall":
                algorithm_call = AlgorithmCall(symbol.name)
                for child in symbol_children:
                    match child.name:
                        case "IDENTIFIER":
                            algorithm_call.identifier= self.characters(child.begin, child.end)
                        case "ArgList":
                            algorithm_call.arguments = self.recursive_builder(child)
                return algorithm_call
            
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
                            array_access.identifier= self.characters(child.begin, child.end)
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

    def identifier_helper_function(self, node, assignment_class):
        for child in node.children:
            match child.name:
                case "IDENTIFIER":
                    assignment_class.identifiers.append(self.characters(child.begin, child.end))
                case "ArrayAccess":
                    assignment_class.identifiers.append(self.recursive_builder(child))
        return assignment_class
