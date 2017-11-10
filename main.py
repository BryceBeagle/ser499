from   pprint  import pprint
import numbers

from   yacc    import getParseTree


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

        # Assign statements are only statement where a variable is created other than for and with blocks
        # Ignoring __setattr__
        elif elem['token_type'] in ['assign_stmt']:
            item_name = elem['name']

            # TODO: Need initial values
            value = elem['value']

            if 'negate' in elem and elem['negate'] is True:
                if isinstance(value, numbers.Number):
                    value = -value
                else:
                    value = {'value'  : value,
                             'negate' : True }

            st[item_name] = value

        # Use variables created in for loop declaration
        elif elem['token_type'] == 'for_stmt':
            st = {**iterAST(elem), **st}
            st.update(dict.fromkeys(elem['expr_list']))

        # TODO: with
    return st


ast = getParseTree()
symbol_table = iterAST(ast)
pprint(symbol_table)
