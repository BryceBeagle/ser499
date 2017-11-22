NUM_TEMPS = 10

# def create_tac(pt):
#
#     for stmt in pt['stmt_list']:
#         if stmt['token_type'] == 'assign_stmt':
#             get_tacs(stmt)
#         elif stmt['token_type'] == 'func_def':
#             print(f"Label: {stmt['name']}")
#             create_tac(stmt)
#             print()
#         elif stmt['token_type'] == 'for_stmt':
#             print("FOR STATEMENTS NOT IMPLEMENTED")
#         else:
#             print(stmt)
#
#
# def get_tacs(stmt, level=0):
#
#     # TODO: Negatives (0 - val)
#
#     value = stmt
#     name = f"t{level - 1}"
#
#     if 'value' in stmt:
#         value = stmt['value']
#         if 'name' in stmt:
#             name = stmt['name']
#
#     if not isinstance(value, dict):
#         if stmt['token_type'] == 'value':
#             return value, level - 1
#
#         else:
#             print(f"{name} = {value}")
#
#     elif value['token_type'] == 'expr':
#         if 'operator' in value:
#             left , level = get_tacs(value['value_left' ], level + 1)
#             right, level = get_tacs(value['value_right'], level + 1)
#             op    = value['operator']
#             print(f"{name} = {left} {op} {right}")
#         else:
#             print(f"Expr Value: {value}")
#
#     elif value['token_type'] in ['list', 'tuple']:
#         # TODO: Expressions in lists use negative temp vars....?
#         level += 1
#         pointer = f"t{level}"
#         level += 1
#         address = f"t{level}"
#         print(f"{pointer} = &{name}")
#         for i, item in enumerate(value['item_list']):
#             val, level = get_tacs(item)
#             print(f"{address} = {pointer} + {i * 8}")
#             print(f"*{address} = {val}")
#
#     return name, level


def printt(string):
    print(f"\t{string}")


def init_registers():

    print()
    print("// INIT REGISTERS")

    print()
    printt("// Pointers")
    printt("int *SP = 0x00")
    printt("int *FP = 0x00")

    print()
    printt("// Temp Registers")
    for i in range(NUM_TEMPS):
        printt(f"int *T{i} = 0x00")


def init_function():

    print()
    printt("// Initializing SP and FP for function")

    printt("*SP = FP")
    printt("SP = SP + 1")
    printt("FP = SP")


def finish_function():

    print()
    printt("//Restoring SP and FP after function")

    printt("SP = FP")
    printt("*FP = SP")
    printt("T0 = *SP")
    printt("SP = SP - 1")
    printt("goto T0")


def init_local_var_space(scope):

    print()
    print("//INIT LOCAL VARIABLE SPACE")

    offset = 1
    for var in scope:
        if isinstance(scope[var], dict):
            continue

        printt(f"SP = SP + 1  // {var}")

        # Store offset in symbol table
        scope[var][2] = offset
        offset += 1


def push_temps():

    print()
    printt("// Saving temp registers to stack")

    for temp in range(NUM_TEMPS):
        printt(f"*SP = T{temp}")
        printt("SP = SP + 1")


def pop_temps():

    print()
    printt("// Restoring temp registers from stack")

    for temp in range(NUM_TEMPS):
        printt("SP = SP - 1")
        printt(f"T{temp} = *SP")


def push_params(st, params):

    print()
    printt("// Saving parameters to stack")

    for i, param in enumerate(params):

        value = param['value']

        # Value is a variable
        if isinstance(value, str) and value[0] != '"':

            # Get location of variable on stack  # TODO: Use register table
            offset = st[value][2]
            printt(f"T0 = FP + {offset}  // {value}")
            value = "TO"

        printt(f"*SP = {value}")
        printt("SP = SP + 1")


def pop_params(params):

    print()
    printt("// Popping params from stack")

    for param in params:
        printt("SP = SP - 1")


def save_return_label(name):

    # TODO: Return address instead of label?
    print()
    printt("Saving return address")

    label = f"{name}_1"
    printt(f"*SP = {label}")
    printt("SP = SP + 1")

    return label


def goto_and_return(func, label):

    print()
    printt("Jump to func and return point")

    printt(f"goto {func}_0")
    print()
    printt(f"{label}:")


def tac_expr(expr, temp_level=0):
    return

    # if 'value' in expr:
    #     value = expr['value']
    #     if not isinstance(value, str) or not value[0] != '"':
    #         return value, temp_level - 1
    #
    # if 'operator' in expr:
    #
    #     left , temp_level = tac_expr(expr['value_left' ], temp_level + 1)
    #     right, temp_level = tac_expr(expr['value_right'], temp_level + 2)
    #     printt(f"T{temp_level} = {left} + {right}")
    #
    # print(value)


def tac_stmt(stmt, func_name, st):

    name = stmt['name']
    value = stmt['value']  # TODO: Non-literal values
    offset = st[name][2]

    if isinstance(value, dict):
        if value['token_type'] == "func":
            func = value['func']

            push_temps()
            push_params(st, value["parameters"])
            label = save_return_label(func_name)
            goto_and_return(func, label)

            pop_params(value["parameters"])
            pop_temps()

            value = "*RA"

            print()

        elif value['token_type'] == 'expr':
            tac_expr(value)

    printt(f"TO = FP + {offset}  // {name}")
    printt(f"*TO = {value}")


def tac_function(func, st):

    print()

    func_name = func['name']
    print(f"{func_name}_0:")

    init_function()
    print()

    funcs = []

    for stmt in func['stmt_list']:
        if stmt['token_type'] == 'func_def':
            funcs.append(stmt)

        if stmt['token_type'] == 'assign_stmt':
            tac_stmt(stmt, func_name, st)

    for func in funcs:
        name = func['name']
        tac_function(func, st[name])

    finish_function()

def create_tac_2(pt, st):
    init_registers()
    init_local_var_space(st)
    tac_function(pt, st)

