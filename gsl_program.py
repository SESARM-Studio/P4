import sys

from evaluator.evaluator import traverse_program
from exceptions.preprocessor_exception import PreprocessorException
from exceptions.parser_exception import ParseException
from exceptions.evaluator_exception import EvaluatorException
from preprocessor.prepro import preprocessor, SourceMap
from parser.ast_builder import AbstractSyntaxTreeBuilder, print_ast
from parser.gsl_parser import gsl_parser
from typesystem.type_checker import TypeChecker

def read(arg):
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
    tree_builder = gsl_parser.ParseTreeBuilder()
    inputString, source_map = read(args[1])
    parser = gsl_parser(inputString, tree_builder)
    ast = AbstractSyntaxTreeBuilder(inputString)
    try:
      parser.parse_Program()
      tree = ast.build_tree(tree_builder.stack)
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
