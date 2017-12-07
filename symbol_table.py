import numbers


def update(dict_, stack, value):

    if not stack:
        return value

    elem = stack.pop(0)
    dict_[elem] = update(dict_.get(elem), stack, value)
    return dict_


def det_type(value):
    if isinstance(value, dict):
        # List item, type will be whatever is first index type
        if value['token_type'] == 'list':
            return list, det_type(value['item_list'][0])
        elif value['token_type'] == 'value':
            return det_type(value['value'])
        else:
            # TODO
            pass
            # print("what now")
    if isinstance(value, numbers.Number):
        return int
    if isinstance(value, str):
        if value[0] == value[-1] == '"':
            return str
        else:
            return "var"


def create_st(ast):
    """
    Create a symbol table using the Syntax Tree
    """

    def ast_helper(dict_):

        st = {}
        for elem in dict_['stmt_list']:

            # Functions are the only thing that can create scope in Python
            # Ignoring classes
            if elem['token_type'] == 'func_def':
                func_name = elem['name']
                st[func_name] = ast_helper(elem)
                st[func_name].update(dict.fromkeys(elem['args_list']))  # Defaults to None value

            # Assign statements are only statement where a variable is created other than for and with blocks
            # Ignoring __setattr__
            elif elem['token_type'] in ['assign_stmt']:
                item_name = elem['name']
                st[item_name] = None

            # Use variables created in for loop declaration
            elif elem['token_type'] == 'for_stmt':
                st = {**ast_helper(elem), **st}
                st.update(dict.fromkeys(elem['expr_list']))

            # TODO: with
        return st

    funcs = []
    def typed_st(ast, st):
        stmt_list = ast['stmt_list']

        for stmt in stmt_list:
            if stmt['token_type'] == 'assign_stmt':
                val = stmt['value']
                type_val = [det_type(val), val, None]  # Type, value, offset
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
                    update(st, funcs + [iter_item], [{"find"}, None, None])

            else:
                # TODO
                pass
                # print(stmt['token_type'])

        return st

    symbol_table = ast_helper(ast)
    # return typed_st(ast, symbol_table)
    return symbol_table
