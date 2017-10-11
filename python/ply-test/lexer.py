import ply.lex_complete as lex

# tokens = tuple(tokenize.tok_name.values())
tokens = ('NUMBER',
          'ID'    ,
          'EQUALS',
          'PLUS'  ,
          'MINUS' ,
          'TIMES' ,
          'DIVIDE',
          'LPAREN',
          'RPAREN'
          )

keywords = {
    'if'   : 'IF'   ,
    'else' : 'ELSE' ,
    'elif' : 'ELIF' ,
    'while': 'WHILE',
    'for'  : 'FOR'  ,
}

# Regex rules
t_PLUS   = r"\+"
t_MINUS  = r"-"
t_TIMES  = r"\*"
t_DIVIDE = r"/"
t_LPAREN = r"\("
t_RPAREN = r"\)"
t_EQUALS = r"="
# t_ID     = r"[a-zA-Z_][a-zA-Z_0-9]*"


def t_ID(t):
    r"[a-zA-Z_][a-zA-Z_0-9]*"
    print("ID: {}".format(t.value))
    t.type = keywords.get(t.value, 'ID')
    return t


def t_NUMBER(t):
    r"\d+"
    print("Number: {}".format(t.value))
    t.value = int(t.value)
    return t


def t_NEWLINE(t):
    r"\n+"
    t.lexer.lineno += len(t.value)


def t_COMMENT(t):
    r"\#.*"
    pass


t_ignore = " \t"


def t_error(t):
    print("Illegal character {}".format(t.value[0]))
    t.lexer.skip(1)


lexer = lex.lex()

if __name__ == "__main__":
    lexer.input("x = 3 * 4 + 5")
    while True:
        tok = lexer.token()
        if not tok: break
        print(tok)
