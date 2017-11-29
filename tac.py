NUM_TEMPS = 10

counter = 1
func_count = {}


def println(string):
    global counter

    print(f"{counter:04d}  {string}")
    counter += 1


def printcm(string=""):
    print(f"----  {string}")


def init_memory(size):

    printcm()
    printcm("// Initializing Memory")

    println(f"int mem[{size}];")


def init_registers():

    printcm()
    printcm("// Initializing Registers")

    printcm()
    printcm("// Pointers")
    println("int sp = 0;")
    println("int fp = 0;")

    printcm()
    printcm("// Temp Registers")
    for i in range(NUM_TEMPS):
        println(f"int t{i};")


def init_function():

    printcm()
    printcm("// Initializing SP and FP for function")

    println("mem[sp] = fp")
    println("sp = sp + 1;")
    println("fp = sp;")


def finish_function(address=None, parent_func=None, parent_level=0):

    # Main does not go anywhere at completion TODO
    if parent_func is None:
        return

    printcm()
    printcm("//Restoring SP and FP after function")

    println("sp = fp")
    println("mem[fp] = sp")
    println("t0 = mem[sp]")
    println("sp = sp - 1")

    if address:
        println("jump t0")
    else:
        println(f"goto {parent_func}_{parent_level}")


def init_local_var_space(scope):

    printcm()
    printcm("// Initialize local variable space")

    offset = 1
    for var in scope:
        if isinstance(scope[var], dict):
            continue

        println(f"sp = sp + 1;  // {var}")

        # Store offset in symbol table
        scope[var][2] = offset
        offset += 1


def push_temps():

    printcm()
    printcm("// Saving temp registers to stack")

    for temp in range(NUM_TEMPS):
        println(f"*sp = t{temp}")
        println("sp = sp + 1")


def pop_temps():

    printcm()
    printcm("// Restoring temp registers from stack")

    for temp in range(NUM_TEMPS):
        println("sp = sp - 1")
        println(f"t{temp} = mem[sp]")


def push_params(params, st):

    printcm()
    printcm("// Saving parameters to stack")

    for i, param in enumerate(params):

        value = param['value']

        # Value is a variable
        if isinstance(value, str) and value[0] != '"':

            # Get location of variable on stack  # TODO: Use register table
            offset = st[value][2]
            println(f"t0 = fp + {offset}  // {value}")
            value = "t0"

        println(f"mem[sp] = {value}")
        println("sp = sp + 1")

    print(1)


def pop_params(params):

    printcm()
    printcm("// Popping params from stack")

    for param in params:
        println("sp = sp - 1")


def save_return_label(name):

    global counter

    # TODO: Return address instead of label?
    printcm()
    printcm("// Saving return address")

    label = f"{name}_1"
    println(f"mem[sp] = {counter + 3}")  # +3: Current line, sp pop, goto
    println("sp = sp + 1")

    return label


def goto_and_return(func, label):

    printcm()
    printcm("// Jump to func and return point")

    println(f"goto {func}_0")
    printcm()
    println(f"{label}:")


def tac_expr(expr, st, temp_count=0):

    if 'value' in expr:
        value = expr['value']
        if not isinstance(value, str) or value[0] == '"':
            return value
        elif isinstance(value, str):
            offset = "OFFSET"  # TODO: st[value][2]
            println(f"t{temp_count} = fp + {offset}  // {value}")
            println(f"t{temp_count} = mem[fp]")

    if 'operator' in expr:

        left  = tac_expr(expr['value_left' ], st, temp_count)
        right = tac_expr(expr['value_right'], st, temp_count + 1)
        println(f"t{temp_count} = {left} + {right}")

    return f"t{temp_count}"


def tac_stmt(stmt, func_name, st):

    name = stmt['name']
    value = stmt['value']  # TODO: Non-literal values
    offset = st[name][2]

    if isinstance(value, dict):
        if value['token_type'] == "func":
            func = value['func']

            push_temps()
            push_params(value["parameters"], st)
            label = save_return_label(func_name)
            goto_and_return(func, label)

            pop_params(value["parameters"])
            pop_temps()

            value = "*RA"

            printcm()

        elif value['token_type'] == 'expr':
            value = tac_expr(value, st)

    println(f"t9 = fp + {offset}  // {name}")  # TODO: Be smart about the temp variable here
    println(f"mem[t9] = {value}")


def tac_function(func, st, parent_func=None, parent_level=0):

    printcm()

    func_name = func['name']

    if func_name in func_count:
        level = func_count[func_name]
        func_count[func_name] += 1
    else:
        func_count[func_name] = 0
        level = 0

    println(f"{func_name}_{level}:")

    init_function()
    printcm()

    funcs = []

    for stmt in func['stmt_list']:
        if stmt['token_type'] == 'func_def':
            funcs.append(stmt)

        if stmt['token_type'] == 'assign_stmt':
            tac_stmt(stmt, func_name, st)

    for func in funcs:
        name = func['name']
        tac_function(func, st[name], parent_func=func_name,
                                     parent_level=level)

    finish_function(parent_func=parent_func,
                    parent_level=parent_level)


def create_tac(pt, st):
    init_memory(1000)
    init_registers()
    init_local_var_space(st)
    tac_function(pt, st)

