import ply.yacc as yacc


# http://www.dabeaz.com/ply/PLYTalk.pdf
# http://www.dabeaz.com/ply/ply.html#ply_nn44
# https://github.com/dabeaz/ply/blob/master/example/GardenSnake/GardenSnake.py#L613

def p_program(p):
    """program : assignment
               | expression"""
    p[0] = ('PROGRAM', p[1])


def p_assignment(p):
    """assignment : ID EQUALS expression"""
    p[0] = ('ASSIGN', p[1], p[3])

def p_expression(p):
    """expression : expression PLUS term
                  | expression MINUS term"""
    p[0] = (p[2], p[1], p[3])


def p_expression_term(p):
    """expression : term
                  | ID"""
    p[0] = p[1]


def p_term(p):
    """term : term TIMES factor
            | term DIVIDE factor"""
    p[0] = (p[2], p[1], p[3])


def p_term_factor(p):
    """term : factor"""
    p[0] = p[1]


def p_factor(p):
    """factor : NUMBER"""
    p[0] = ('NUM', p[1])


def p_factor_expr(p):
    """factor : LPAREN expression RPAREN"""
    p[0] = p[2]


# def p_error(p):
#     print("Syntax error in input!")


parser = yacc.yacc()

while True:
    try:
        s = input('calc > ')
    except EOFError:
        break
    if not s: continue
    result = parser.parse(s)
    print(result)
