import sys

from evaluator.evaluator import traverse_program
from exceptions.preprocessor_exception import PreprocessorException
from exceptions.parser_exception import ParseException
from exceptions.evaluator_exception import EvaluatorException
from preprocessor.preprocessor import preprocessor, SourceMap
from parser.ast_builder import AbstractSyntaxTreeBuilder, print_ast
from parser.gsl_parser import gsl_parser
from typesystem.type_checker import TypeChecker

def read(arg):
  if arg.startswith("{") and arg.endswith("}"):
    return arg[1:len(arg) - 1]
  else:
    source_map = SourceMap()
    try:
        content = preprocessor(arg, source_map)
    except PreprocessorException as pe:
        source_map.print_error(pe.message, pe.span[0], pe.span[1], processed=False)
        sys.exit(1)

    if len(content) > 0 and content[0] == "\ufeff":
      content = content[1:]
    return content, source_map

def main(args):
    debug = False
    for arg in args[1:]:
        if arg == "-debug":
           debug = True
           continue
        b = gsl_parser.ParseTreeBuilder()
        inputString, source_map = read(arg)
        parser = gsl_parser(inputString, b)
        ast = AbstractSyntaxTreeBuilder(inputString)
        try:
           parser.parse_Program()
           tree = ast.build_tree(b.stack)
           if debug is True:
              print_ast(tree)
           type_checker = TypeChecker(tree, source_map)
           type_checker.check()
           traverse_program(tree)
        except ParseException as pe:
            source_map.print_error(parser.getErrorMessage(pe), pe.getBegin(), pe.getEnd())
            sys.exit(1)
        except EvaluatorException as ee:
            source_map.print_error(ee.message, ee.span[0], ee.span[1], error_type="Evaluator")
            sys.exit(1)

if __name__ == '__main__':
  sys.exit(main(sys.argv))
