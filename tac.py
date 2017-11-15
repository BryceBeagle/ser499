

def create_tac(pt):

    for stmt in pt['stmt_list']:
        if stmt['token_type'] == 'assign_stmt':
            get_tacs(stmt)
        elif stmt['token_type'] == 'func_def':
            print(f"Label: {stmt['name']}")
            create_tac(stmt)
            print()
        elif stmt['token_type'] == 'for_stmt':
            print("FOR STATEMENTS NOT IMPLEMENTED")
        else:
            print(stmt)


def get_tacs(stmt, level=0):

    # TODO: Negatives (0 - val)

    value = stmt
    name = f"t{level - 1}"

    if 'value' in stmt:
        value = stmt['value']
        if 'name' in stmt:
            name = stmt['name']

    if not isinstance(value, dict):
        if stmt['token_type'] == 'value':
            return value, level - 1

        else:
            print(f"{name} = {value}")

    elif value['token_type'] == 'expr':
        if 'operator' in value:
            left , level = get_tacs(value['value_left' ], level + 1)
            right, level = get_tacs(value['value_right'], level + 1)
            op    = value['operator']
            print(f"{name} = {left} {op} {right}")
        else:
            print(f"Expr Value: {value}")

    elif value['token_type'] in ['list', 'tuple']:
        # TODO: Expressions in lists use negative temp vars....?
        level += 1
        pointer = f"t{level}"
        level += 1
        address = f"t{level}"
        print(f"{pointer} = &{name}")
        for i, item in enumerate(value['item_list']):
            val, level = get_tacs(item)
            print(f"{address} = {pointer} + {i * 8}")
            print(f"*{address} = {val}")

    return name, level
