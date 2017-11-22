import ply.yacc as     yacc
from   pprint   import pprint

# noinspection PyUnresolvedReferences
from lex import tokens, IndentLexer


def p_program(p):
    """program : stmt
               | stmt_list ENDMARKER"""
    if p[1]['token_type'] == 'stmt_list':
        p[0] = {'token_type' : "PROGRAM"        ,
                'stmt_list'  : p[1]['stmt_list'],
                'name'       : "main"           }
    else:
        p[0] = {'token_type' : "PROGRAM",
                'stmt_list'  : p[1]     ,
                'name'       : "main"   }


def p_stmt_list(p):
    """stmt_list : stmt
                 | stmt_list stmt_list"""
    if len(p) == 3:
        p[0] = p[1]
        for stmt in p[2]['stmt_list']:
            p[0]['stmt_list'].append(stmt)
            pass
        # p[0]['stmt_list'].append(p[2]['stmt_list'])
    if isinstance(p[1], str) or p[1]['token_type'] == 'stmt':
        p[0] = {'token_type' : 'stmt_list',
                'stmt_list'  : [p[1]['stmt']]     }


def p_stmt(p):
    """stmt : stmt NEWLINE
            | assign_stmt
            | augassign_stmt
            | func_def
            | for_stmt
            | if_stmt
            | expr
            | return"""
    if p[1]['token_type'] == 'stmt':
        p[0] = p[1]
    else:
        p[0] = {'token_type' : 'stmt',
                'stmt'       : p[1]  }


def p_assign_stmt(p):
    """assign_stmt : NAME ASSIGN expr"""
    if p[3]['token_type'] == "value":
        value  = p[3]['value' ]
        negate = p[3]['negate']
    else:
        value  = p[3]
        negate = False
    p[0] = {'token_type' : 'assign_stmt',
            'name'       : p[1]         ,
            'value'      : value        ,
            'negate'     : negate       }


def p_expr(p):
    """expr : value
            | PLUS expr
            | MINUS expr
            | expr bin_op expr
            | LPAREN expr RPAREN"""
    if len(p) == 2 or p[1] == '(':
        if p[1] == '(':  # Cheaty way to ignore the parentheses
            p[1] = p[2]
        p[0] = {'token_type' : 'value',
                'value'      : p[1]   ,
                'negate'     : False  }
    elif len(p) == 3:
        negate = True if p[1] == '-' else False
        p[0] = {'token_type' : 'value'                 ,
                'value'      : p[2]['value']           ,
                'negate'     : negate != p[2]['negate']}  # Negatives cancel out
    else:
        p[0] = {'token_type' : 'expr',
                'operator'   : p[2]  ,
                'value_left' : p[1]  ,
                'value_right': p[3]  }


def p_value(p):
    """value : atom
             | value trailer"""
    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = p[2]
        p[0]['func'] = p[1]


def p_bin_op(p):
    """bin_op : PLUS
              | MINUS
              | TIMES
              | DIVIDE
              | INT_DIVIDE
              | MOD
              | AT
              | BSL
              | BSR
              | BOR
              | BAND
              | BNOT
              | BXOR"""
    p[0] = p[1]


def p_augassign_stmt(p):
    """augassign_stmt : NAME augassign expr"""
    p[0] = {'token_type' : 'assign_stmt'                   ,
            'name'       : p[1]                            ,
            'value'      : {'token_type' : 'p_expr'        ,
                            'operator'   : p[2].rstrip('='),
                            'value_left' : p[1]            ,
                            'value_right': p[3]            }}


def p_augassign(p):
    """augassign : PLUS_EQUALS
                 | MINUS_EQUALS
                 | TIMES_EQUALS
                 | AT_EQUALS
                 | DIVIDE_EQUALS
                 | MOD_EQUALS
                 | AND_EQUALS
                 | OR_EQUALS
                 | NOT_EQUALS
                 | BSL_EQUALS
                 | BSR_EQUALS
                 | POWER_EQUALS
                 | INT_DIVIDE_EQUALS"""
    p[0] = p[1]


def p_func_def(p):
    """func_def : DEF NAME parameters COLON suite"""
    p[0] = {'token_type' : 'func_def'       ,
            'name'       : p[2]             ,
            'args_list'  : p[3]['args_list'],
            'stmt_list'  : p[5]['stmt_list']}


def p_parameters(p):
    """parameters : LPAREN args_list RPAREN"""
    p[0] = p[2]


def p_args_list(p):
    """args_list : NAME
                 | args_list COMMA args_list"""
    if len(p) == 2:
        p[0] = {'token_type' : 'args_list',
                'args_list'  : [p[1]]     }
    else:
        p[0] = p[1]
        p[0]['args_list'] += p[3]['args_list']


def p_suite(p):
    """suite : stmt
             | NEWLINE INDENT stmt_list DEDENT"""
    if len(p) == 2:
        p[0] = {'token_type' : 'stmt_list',
                'stmt_list'  : [p[1]]     }
    else:
        p[0] = p[3]


def p_for_stmt(p):
    """for_stmt : FOR expr_list IN expr COLON suite
                | FOR expr_list IN expr COLON suite else_stmt"""
    p[0] = {'token_type' : 'for_stmt'       ,
            'expr_list'  : p[2]['expr_list'],
            'iterator'   : p[4]             ,
            'stmt_list'  : p[6]['stmt_list']}
    if len(p) == 8:
        p[0]['else_stmt_list'] = p[8]['stmt_list']


def p_expr_list(p):
    """expr_list : NAME
                 | expr_list COMMA expr_list"""
    if len(p) == 2:
        p[0] = {'token_type' : 'expr_list',
                'expr_list'  : [p[1]]     }
    else:
        p[0] = p[1]
        p[0]['expr_list'] += p[3]['expr_list']


def p_item_list(p):
    """item_list : expr
                 | item_list COMMA item_list"""
    if len(p) == 2:
        p[0] = {'token_type' : 'item_list',
                'item_list'  : [p[1]]}
    else:
        p[0] = p[1]
        p[0]['item_list'] += p[3]['item_list']


def p_atom(p):
    """atom : NAME
            | NUMBER
            | STRING
            | NONE
            | TRUE
            | FALSE
            | list
            | tuple
            | dict"""
    p[0] = p[1]


def p_list(p):
    """list : LBRACKET item_list RBRACKET"""
    p[0] = {'token_type' : 'list'           ,
            'item_list'  : p[2]['item_list']}


def p_tuple(p):
    """tuple : LPAREN item_list RPAREN"""
    p[0] = {'token_type' : 'tuple'          ,
            'item_list'  : p[2]['item_list']}


def p_dict(p):
    """dict : LBRACE dict_list RBRACE"""
    p[0] = {'token_type' : 'dict',
            'item_list'  : p[2]  }


def p_dict_list(p):
    """dict_list : expr COLON expr
                 | dict_list COMMA dict_list
                 | dict_list COMMA NEWLINE dict_list"""

    if p[2] == ':':
        p[0] = {p[1] : p[3]}
    else:
        p[0] = {**p[1], **p[-1]}  # Merge the dict_lists


def p_else_stmt(p):
    """else_stmt : ELSE COLON suite"""
    p[0] = {'token_type' : 'else_stmt'      ,
            'stmt_list'  : p[3]['stmt_list']}


def p_if_stmt(p):
    """if_stmt : IF test COLON suite
               | IF test COLON suite elif_stmt_list
               | IF test COLON suite else_stmt
               | IF test COLON suite elif_stmt_list else_stmt"""
    p[0] = {'token_type' : 'if_stmt'        ,
            'test'       : p[2]             ,
            'stmt_list'  : p[4]['stmt_list']}
    if len(p) > 5:
        if p[5]['token_type'] == 'elif_stmt_list':
            p[0]['elif_stmt_list'] = p[5]['elif_stmt_list']
        elif p[5]['token_type'] == 'else_stmt':
            p[0]['else_stmt'] = p[-1]


def p_test(p):
    """test : expr
            | comparison"""
    p[0] = {'token_type' : 'test',
            'test'       : p[1]  }


def p_comparison(p):
    """comparison : test comparison_op test"""
    p[0] = {'token_type' : p[2],
            'test_left'  : p[1],
            'test_right' : p[3]}


def p_comparison_op(p):
    """comparison_op : EQUALS
                     | GT
                     | GT_EQUALS
                     | LT
                     | LT_EQUALS
                     | NOT_EQUALS
                     | IS
                     | IN
                     | NOT_IN"""
    p[0] = p[1]


def p_elif_stmt_list(p):
    """elif_stmt_list : elif_stmt
                  | elif_stmt_list NEWLINE elif_stmt_list"""
    if len(p) == 2:
        p[0] = {'token_type'     : 'elif_stmt_list',
                'elif_stmt_list' : [p[1]]      }
    else:
        p[0] = p[1]
        p[0]['elif_stmt_list'] += p[3]['elif_stmt_list']


def p_elif_stmt(p):
    """elif_stmt : ELIF test COLON suite"""
    p[0] = {'token_type' : 'elif_stmt'      ,
            'test'       : p[2]             ,
            'stmt_list'  : p[4]['stmt_list']}


def p_not(p):
    """not : NOT test"""
    p[0] = {'token_type' : 'not',
            'test'       : p[1] }


def p_trailer(p):
    """trailer : DOT NAME
               | tuple
               | list"""
    if len(p) == 3:
        p[0] = {'token_type' : "dot",
                'name'       : p[2] }
    elif p[1]["token_type"] == 'tuple':
        p[0] = {'token_type' : "func",
                'parameters' : p[1]['item_list']}
    elif p[1]["token_type"] == 'list':
        p[0] = {'token_type' : "get_attr",
                'parameters' : p[1]['item_list']}


def p_return(p):
    """return : RETURN value"""
    p[0] = {'token_type' : "return",
            'value'      : p[2]    }


def getParseTree():
    lexer = IndentLexer()
    parser = yacc.yacc()

    try:

        with open("input2.py") as fi:
            s = "\n".join(fi.readlines()) + "\u0004"
        # result = parser.parse(s, lexer=lexer, debug=True)
        result = parser.parse(s, lexer=lexer)
        return result

    except EOFError:
        pass


if __name__ == "__main__":
    print(getParseTree())
