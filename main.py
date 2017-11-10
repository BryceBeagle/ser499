import collections
from   pprint      import pprint
import numbers

from   yacc        import getParseTree


def createAST(dict_):
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
            st[func_name] = createAST(elem)
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
            st = {**createAST(elem), **st}
            st.update(dict.fromkeys(elem['expr_list']))

        # TODO: with
    return st


def update(dict_, stack, value):

    if not len(stack):
        return value

    elem = stack.pop(0)
    dict_[elem] = update(dict_.get(elem), stack, value)
    return dict_


def det_type(value):
    if isinstance(value, dict):
        # List item, type will be whatever is first index type
        if value['token_type'] == 'list':
            return list, det_type(value['item_list'][0])
        if value['token_type'] == 'value':
            return det_type(value['value'])
        else:
            pprint("what now")
    if isinstance(value, numbers.Number):
        return int
    if isinstance(value, str):
        return str


funcs = []
def typed_st(ast, st):
    stmt_list = ast['stmt_list']

    for stmt in stmt_list:
        if stmt['token_type'] == 'assign_stmt':
            val = stmt['value']
            type_val = det_type(val), val
            update(st, funcs + [stmt['name']], type_val)
        elif stmt['token_type'] == 'func_def':
            funcs.append(stmt['name'])
            typed_st(stmt, st)
            funcs.pop()
        elif stmt['token_type'] == 'for_stmt':
            iterator = stmt['iterator']['value']
            if isinstance(iterator, dict):
                if iterator['token_type'] == 'func':
                    if iterator['func'] == 'enumerate':
                        counter = stmt['expr_list'][0]
                        update(st, funcs + [counter], (int, 0))
                iter_item = stmt['expr_list'][-1]
                update(st, funcs + [iter_item], ({"find"}, None))

        else:
            print(stmt['token_type'])

    return st

print()
print()
print()
print()
print()
print()
print()
parse_tree = getParseTree()
symbol_table = createAST(parse_tree)

typed_ast = typed_st(parse_tree, symbol_table)
pprint(typed_ast)
