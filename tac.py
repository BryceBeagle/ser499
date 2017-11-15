

def create_tac(pt):

    for stmt in pt['stmt_list']:
        if stmt['token_type'] == 'assign_stmt':
            get_tacs(stmt)


def get_tacs(stmt, level=0):

    # TODO: Negatives (0 - val)

    if 'value' in stmt:
        value = stmt['value']
        if 'name' in stmt:
            name = stmt['name']
    else:
        value = stmt
        name = f"t{level - 1}"

    if not isinstance(value, dict):
        if stmt['token_type'] == 'value':
            return value

        else:
            print(f"{name} = {value}")

    elif value['token_type'] == 'expr':
        if 'operator' in value:
            left  = get_tacs(value['value_left' ], level + 1)
            right = get_tacs(value['value_right'], level + 1)
            op    = value['operator']
            print(f"{name} = {left} {op} {right}")
        else:
            print(f"Expr Value: {value}")

    if level > 0:
        return name
