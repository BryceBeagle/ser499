import ply.lex as lex

# Whitespace and tabbing methodology from GardenSnake PLY example at
# https://github.com/dabeaz/ply/blob/master/example/GardenSnake/GardenSnake.py

# TODO: This needs a lot of work
tokens = ('NUMBER'     , 'NAME'        ,

          'PLUS'       , 'MINUS'       , 'TIMES'       , 'DIVIDE'       , 'INT_DIVIDE'       , 'MOD'        , 'AT'       ,
          'PLUS_EQUALS', 'MINUS_EQUALS', 'TIMES_EQUALS', 'DIVIDE_EQUALS', 'INT_DIVIDE_EQUALS', 'MOD_EQUALS' , 'AT_EQUALS',

          'BSL'        , 'BSR'         , 'BOR'         , 'BAND'         , 'BNOT'             , 'BXOR'       ,
          'BSL_EQUALS' , 'BSR_EQUALS'  , 'BOR_EQUALS'  , 'BAND_EQUALS'  , 'BNOT_EQUALS'      , 'BXOR_EQUALS',

          'LPAREN'     , 'RPAREN'      , 'LBRACE'      , 'RBRACE'       , 'LBRACKET'         , 'RBRACKET'   ,

          'COLON'      , 'COMMA'       , 'NEWLINE'     , 'WS'           , 'DOT'              ,

          'ASSIGN'           ,
          'AND'       , 'OR'       , 'NOT',
          'AND_EQUALS', 'OR_EQUALS', 'NOT_EQUALS',
          'POWER_EQUALS',
          'GT'       , 'LT',
          'GT_EQUALS', 'LT_EQUALS',
          'EQUALS', 'IS',
          'IN', 'NOT_IN',
          'IF', 'ELIF', 'ELSE',
          'INDENT', 'DEDENT',
          'DEF',
          'FOR',
          'WHILE',
          'WITH',
          'STRING',
          'NONE',
          'TRUE', 'FALSE',
          'ENDMARKER',

          'RETURN')

keywords = {'if'     : 'IF'    ,
            'else'   : 'ELSE'  ,
            'elif'   : 'ELIF'  ,
            'while'  : 'WHILE' ,
            'for'    : 'FOR'   ,
            'True'   : 'TRUE'  ,
            'False'  : 'FALSE' ,
            'def'    : 'DEF'   ,
            'pass'   : 'PASS'  ,
            'in'     : 'IN'    ,
            'return' : 'RETURN'}

# Regex rules
t_PLUS        = r"\+"
t_PLUS_EQUALS = r"\+="
t_MINUS       = r"-"
t_TIMES       = r"\*"
t_DIVIDE      = r"\/"
t_INT_DIVIDE  = r"\/\/"
t_MOD         = "\%"
t_AT          = "@"
t_GT          = "\>"
t_LT          = "\<"
t_GT_EQUALS   = "\>="
t_LT_EQUALS   = "\<="
t_DOT         = r"\."
t_EQUALS      = r"=="
t_ASSIGN      = r"="
t_LBRACKET    = r"\["
t_RBRACKET    = r"\]"
t_LBRACE      = r"\{"
t_RBRACE      = r"\}"
t_COLON       = r":"
t_COMMA       = r","
t_ENDMARKER   = "\u0004"
# t_ID     = r"[a-zA-Z_][a-zA-Z_0-9]*"


def t_WS(t):
    r"[ ]+"
    if t.lexer.at_line_start:  # and t.lexer.paren_count == 0:
        return t


def t_LPAREN(t):
    r"\("
    # t.lexer.paren_count += 1
    return t


def t_RPAREN(t):
    r"\)"
    # t.lexer.paren_count -= 1
    return t


def t_NAME(t):
    r"[a-zA-Z_][a-zA-Z_0-9]*"
    t.type = keywords.get(t.value, 'NAME')
    return t


def t_NUMBER(t):
    r"\d+"
    t.value = int(t.value)
    return t


def t_NEWLINE(t):
    r"\n+"
    t.lexer.lineno += len(t.value)
    # if t.lexer.paren_count == 0:
    return t


def t_STRING(t):
    r"\".*\""
    return t


def t_COMMENT(t):
    r"\#.*"
    pass


def t_error(t):
    print("Illegal character {}".format(t.value[0]))
    t.lexer.skip(1)


class IndentLexer(object):

    def __init__(self):
        self.lexer = lex.lex()
        self.token_stream = None

    def input(self, s):
        self.lexer.parent_count = 0
        self.lexer.input(s)
        self.token_stream = self.filter()

    # Returns element from generator
    def token(self):
        return next(self.token_stream, None)

    def filter(self):
        tokens = iter(self.lexer.token, None)
        tokens = self.track_tokens_filter(tokens)

        for token in self.indentation_filter(tokens):
            yield token

    def track_tokens_filter(self, tokens):

        NO_INDENT   = 0
        MAY_INDENT  = 1
        MUST_INDENT = 2

        self.lexer.at_line_start = at_line_start = True
        indent = NO_INDENT

        for token in tokens:

            # Assume token is at start of line initially
            token.at_line_start = at_line_start

            if token.type == "COLON":

                # Token must not be at start of line
                at_line_start = False

                # Indent is possible
                indent = MAY_INDENT

                token.must_indent = False

            elif token.type == "NEWLINE":

                # Keep only one new line
                token.value = '\n'

                # Token must be at start of line after a NEWLINE token
                at_line_start = True

                # If indent was possible before, it is now required
                if indent == MAY_INDENT:
                    indent = MUST_INDENT

                # Doesn't need an indent just yet (next token)
                token.must_indent = False

            elif token.type == "WS":

                # White space token should only occur at start of line
                assert token.at_line_start is True
                at_line_start = True

                # If we have a WS token, some amount of indenting has been performed
                token.must_indent = False

            # "Real" token
            else:

                if indent == MUST_INDENT:
                    # Indent required for this token
                    token.must_indent = True
                else:
                    token.must_indent = False

                # Real tokens will not be at start of line
                at_line_start = False
                self.lexer.at_line_start = False

                # Clear indent tracker
                indent = NO_INDENT

            yield token
            self.lexer.at_line_start = at_line_start

    def indentation_filter(self, tokens):

        levels = [0]  # Stores stack of indentations (in spaces)
        depth = 0     # Current unprocessed indentation depth
        prev_was_ws = False

        for token in tokens:

            if token.type == "WS":
                assert depth == 0
                depth = len(token.value)  # Number of spaces
                prev_was_ws = True
                continue

            if token.type == "NEWLINE":
                depth = 0

                # Ignore blank lines
                if prev_was_ws or token.at_line_start:
                    continue

                yield token
                continue

            prev_was_ws = False

            if token.must_indent:

                # Current depth must be larger than previous level
                if not (depth > levels[-1]):
                    raise IndentationError("Expected indented block")

                levels.append(depth)
                yield self._new_token("INDENT", token.lineno, token.lexpos)

            elif token.at_line_start:

                # Current depth (defined above) must be same level or one of previous levels
                if depth == levels[-1]:
                    # Same
                    pass
                elif depth > levels[-1]:
                    raise IndentationError("Unexpected indentation increase")
                else:
                    # Smaller indentation. Attempt to back up to previous value
                    try:
                        i = levels.index(depth)
                    except ValueError:
                        raise IndentationError("Inconsistent indentation")
                    # Create DEDENT tokens until indentation matches
                    for _ in range(i + 1, len(levels)):
                        yield self._new_token("DEDENT", token.lineno, token.lexpos)
                        levels.pop()

            yield token

    @staticmethod
    def _new_token(type, lineno, lexpos):
        class NewClass(lex.LexToken): pass
        NewClass.__name__ = type
        NewClass.type = type
        NewClass.value = None
        NewClass.lineno = lineno
        NewClass.lexpos = lexpos
        return NewClass()


lexer = IndentLexer()

if __name__ == "__main__":
    with open("input.py") as fi:
        s = "".join(fi.readlines()) + "\u0004"
    # s = "x = 3 * 4 + 5"
    lexer.input(s)
    tok = True
    while tok:
        tok = lexer.token()
        print(tok)
