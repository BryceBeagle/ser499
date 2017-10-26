from pprint import pprint

from yacc   import getParseTree


def iterAST(dict_):
    """
    Create a symbol table using the Syntax Tree

    Not sure how to approach storing values at the moment.
    Does that even go in the Symbol Table until run time (excluding constant propagation)?
    """
    st = {}
    for elem in dict_['stmt_list']:

        # Functions are the only thing that can create scope in Python
        # Ignoring classes
        if elem['token_type'] == 'func_def':
            func_name = elem['name']
            st[func_name] = iterAST(elem)
            st[func_name].update(dict.fromkeys(elem['args_list']))  # Defaults to None value

        # Assign statements are only statement where a variable is created
        # Ignoring __setattr__
        elif elem['token_type'] in ['assign_stmt']:
            item_name = elem['name']

            # TODO: Need initial values
            st[item_name] = None

        # Use variables created in for loop declaration
        elif elem['token_type'] == 'for_stmt':
            st = {**iterAST(elem), **st}
            st.update(dict.fromkeys(elem['expr_list']))
    return st


ast = getParseTree()
symbol_table = iterAST(ast)
pprint(symbol_table)
