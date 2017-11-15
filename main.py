from pprint       import pprint

from yacc         import getParseTree
from symbol_table import create_st

parse_tree = getParseTree()
st = create_st(parse_tree)

pprint(st)
