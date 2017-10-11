import ply.yacc as yacc


def p_start(p):
    """start : NEWLINE
             | simple_stmt
             | compound_stmt NEWLINE"""
    p[0] = ("START", p[1])


def p_simple_stmt(p):
    """simple_stmt : small_stmt NEWLINE
                   | small_stmt SEMICOLON small_stmt
                   | simple_stmt SEMICOLON NEWLINE"""


def p_small_stmt(p):  # TODO: import_stmt removed
    """small_stmt : expr_stmt
                  | del_stmt
                  | pass_stmt
                  | flow_stmt
                  | global_stmt
                  | nonlocal_stmt
                  | assert_stmt"""


def p_expr_stmt(p):
    """expr_stmt : testlist_star_expr""" # TODO
    pass


def p_del_stmt(p):
    """del_stmt : DEL expr_list""" # TODO: expr_list
    p[0] = (p[1], p[2])


def p_pass_stmt(p):
    """pass_stmt : PASS"""
    p[0] = (p[1],)  # One element tuple


def p_flow_stmt(p):
    """flow_stmt : break_stmt
                 | continue_stmt
                 | return_stmt
                 | raise_stmt
                 | yield_stmt"""
    p[0] = p[1]


def p_break_stmt(p):
    """break_stmt : BREAK"""
    p[0] = (p[1],)  # One element tuple


def p_continue_stmt(p):
    """continue_stmt : CONTINUE"""
    p[0] = (p[1],)  # One element tuple


def p_return_stmt(p):
    """return : RETURN
              | RETURN testlist"""  # TODO: testlist
    if len(p) == 2:
        p[0] = (p[1],)  # One element tuple
    if len(p) == 3:
        p[0] = (p[1], p[2])


def p_yield_stmt(p):  # TODO: yield_expr
    """yield_stmt : yield_expr"""
    p[0] = p[1]


def p_raise_stmt(p):  # TODO: test
    """raise_stmt : RAISE
                  | RAISE test
                  | RAISE test FROM test"""
    if len(p) == 2:
        p[0] = (p[1],)  # One element tuple
    if len(p) == 3:
        p[0] = (p[1], p[2])
    if len(p) == 4:
        p[0] = (p[1], p[2], p[3])  # TODO: Is this the proper way with FROM?

# def p_import_stmt(p):
#     """import_stmt : import_name
#                    | import_from"""
#     p[0] = p[1]
#
#
# def p_import_name(p):
#     """import_name : IMPORT dotted_names"""
#     p[0] = (p[1], p[2])
#
#
# def p_import_from(p):  # TODO:
#     raise NotImplementedError
#
#
# def p_import_as_name(p):
#     """import_as_name : NAME
#                       | NAME AS NAME"""
#     if len(p) == 2:
#         p[0] = (p[1],)  # One element tuple
#     if len(p) == 3:
#         p[0] = (p[2],)  # One element tuple
#
#
# def p_dotted_as_name(p):
#     """dotted_as_name : dotted_name
#                       | dotted_name AS NAME"""
#     if len(p) == 2:
#         p[0] = (p[1],)  # One element tuple
#     if len(p) == 3:
#         p[0] = (p[2],)  # One element tuple
#
#
# def p_import_as_names(p):
#     """import_as_names : import_as_name COMMA
#                        | import_as_name COMMA import_as_name"""
#     p[0] = tuple(p[1::2])  # Every import_as_name ignoring commas
#
#
# def p_dotted_as_names(p):
#     """dotted_as_names : dotted_name
#                        | dotted_name COMMA dotted_name"""
#     p[0] = tuple(p[1::2])  # Every dotted_name ignoring commas
#
#
# def p_dotted_name(p):  # TODO: PERIOD
#     """dotted_name : NAME
#                    | NAME PERIOD NAME"""
#


def p_global_stmt(p):  # TODO:
    """global_stmt : GLOBAL NAME
                   | GLOBAL NAME COMMA NAME"""  # TODO: Klein star?
    raise NotImplementedError


def p_nonlocal_stmt(p):  # TODO:
    """nonlocal_stmt : NONLOCAL NAME
                     | NONLOCAL NAME COMMA NAME""" # TODO: Klein star?
    raise NotImplementedError


def p_assert_stmt(p):  # TODO: test
    """assert_stmt : ASSERT test
                   | ASSERT test COMMA test"""
    if len(p) == 2:
        p[0] = (p[1],)  # One element tuple
    if len(p) == 3:
        p[0] = (p[1], p[3])


def p_compount_stmt(p):  # TODO: while_stmt, for_stmt, try_stmt, with_stmt, funcdef, class_def, decorated
    """compound_stmt : if_stmt
                     | while_stmt
                     | for_stmt
                     | try_stmt
                     | with_stmt
                     | funcdef
                     | classdef
                     | decorated
                     | async_stmt"""
    p[0] = p[1]


def p_async_stmt(p):  # TODO: funcdef, with_stmt, for_stmt
    """async_stmt : ASYNC funcdef
                  | ASYNC with_stmt
                  | ASYNC for_stmt"""
    p[0] = (p[1], p[2])


def p_if_stmt(p):  # TODO: test, suite, elif_stmt, else_stmt
    """if_stmt : IF test COLON suite
               | IF test COLON suite elif_stmt
               | IF test COLON suite else_stmt
               | IF test COLON suite elif_stmt else_stmt"""
    raise NotImplementedError  # TODO:


def p_while_stmt(p):  # TODO: test, suite, else_stmt
    """while_stmt : WHILE test COLON suite
                  | WHILE test COLON suite else_stmt"""
    raise NotImplementedError  # TODO:


def p_for_stmt(p):  # TODO: exprlist, testlist, suite, else_stmt
    """for_stmt : FOR exprlist IN testlist COLON suite
                | FOR exprlist IN testlist COLON suite else_stmt"""
    raise NotImplementedError  # TODO:


# def p_try_stmt(p):  # TODO: how do
#     """try_stmt : TRY suite FINALLY suite
#                 | TRY suite except_clauses """

def p_with_stmt(p):  # TODO: with_item
    """with_stmt : WITH with_item COLON suite
                 | WITH with_items COLON suite"""  # TODO: How do
    raise NotImplementedError  # TODO:


def p_with_item(p):  # TODO: test, expr
    """with_item : test
                 | test AS expr"""
    if len(p) == 2:
        p[0] = p[1]
    if len(p) == 3:
        p[0] = (p[1], p[2])


def p_except_clause(p):
    """except_clause : EXCEPT
                     | EXCEPT test
                     | EXCEPT test AS NAME"""
    if len(p) == 2:
        p[0] = p[1]
    if len(p) == 3:
        p[0] = (p[1], p[2])
    if len(p) == 4:
        p[0] = (p[1], p[2], p[3])
