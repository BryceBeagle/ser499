from yacc         import getParseTree
from symbol_table import create_st
from tac          import create_tac


parse_tree = getParseTree()
st = create_st(parse_tree)

create_tac(parse_tree, st)
