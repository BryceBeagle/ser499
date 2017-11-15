

def create_tac(pt):

    for stmt in pt['stmt_list']:
        if stmt['token_type'] == 'assign_stmt':
            get_tacs(stmt)


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

    return name, level
    # if level > 0:
    #     pass
