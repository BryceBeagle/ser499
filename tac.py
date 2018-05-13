"""
Layout of stack

       +-------------------+
       | saved temps       |
       | parameters        |
       | return address    |
       | saved FP          | <-+
       | local variables   |   |
       +-------------------+   |
       | saved temps       |   |
       | parameters        |   |  (FP - k)
       | return address    |   |
FP --> | saved FP          | --+
SP --> | local variables   |      (FP + k)
       +-------------------+
       | Unused            |
       | Unused            |
       | Unused            |
       | Unused            |
       | ...               |
       +-------------------+

"""


file = "c-output/output.c"
open(file, "w+").close()


NUM_TEMPS = 10

counter = 1

def println(string="", tab=True):
    global counter

    open(file, 'a+').write(tab * "    " + string + "\n")
    print(f"{counter:04d}  {string}")
    counter += 1


def printcm(string="", tab=True):

    open(file, 'a+').write(tab * "    " + string + "\n")
    print(f"----  {string}")


def init_c_main():
    println("")
    println("int main() {", tab=False)


def close_c_main():
    printcm()
    println("main_0r: ;")
    println("}", tab=False)


def init_memory(size):

    printcm()
    printcm("// Initializing Memory", tab=False)

    println(f"int mem[{size}];", tab=False)


def init_registers():

    printcm()
    printcm("// Initializing Registers", tab=False)

    printcm()
    printcm("// Pointers", tab=False)
    println("int sp = 0;", tab=False)
    println("int fp = 0;", tab=False)

    printcm()
    printcm("// Temp Registers", tab=False)
    for i in range(NUM_TEMPS):
        println(f"int t{i};", tab=False)


def init_function():

    printcm()
    printcm("// Initializing SP and FP for function")

    println("mem[sp] = fp;")
    println("fp = sp;")
    println("sp = sp + 1;")


def finish_function(calling_func, instance):

    # Main does not go anywhere at completion TODO
    if calling_func is None:
        return

    printcm()
    printcm("//Restoring SP and FP after function")

    println("sp = fp;")
    println("fp = mem[sp];")
    # println("sp = sp - 1;")

    printcm()
    println(f"goto {calling_func}_{instance}r;", tab=False)


def init_local_var_space(scope):

    printcm()
    printcm("// Initialize local variable space")

    offset = 1  # Can't use enumerate because of ignored elements
    for var in scope:

        # Ignore vars who already have an offset (params)
        if isinstance(scope[var], dict) or scope[var] is not None:
            continue

        scope[var] = offset
        offset += 1

        println(f"sp = sp + 1;  // {var}")


def push_temps():

    printcm()
    printcm("// Saving temp registers to stack")

    for temp in range(NUM_TEMPS):
        println(f"mem[sp] = t{temp};")
        println("sp = sp + 1;")


def pop_temps():

    printcm()
    printcm("// Restoring temp registers from stack")

    for temp in range(NUM_TEMPS):
        println("sp = sp - 1;")
        println(f"t{temp} = mem[sp];")


def push_params(params, st):
    """Push parameters onto stack. Use st to refer to local variable offsets"""

    printcm()
    printcm("// Saving parameters to stack")

    for i, param in enumerate(params):

        value = param['value']

        # Value is a variable
        if isinstance(value, str) and value[0] != '"':

            # Get location of variable on stack  # TODO: Use register table
            offset = st[value]
            sign = '+' if offset >= 0 else '-'

            println(f"t0 = fp {sign} {abs(offset)};  // {value}")
            println("t0 = mem[t0];")
            value = "t0"

        println(f"mem[sp] = {value};")
        println("sp = sp + 1;")


def pop_params(params):

    printcm()
    printcm("// Popping params from stack")

    for param in params:
        println("sp = sp - 1;")


def pop_return():

    printcm("// Popping returned value")
    println("sp = sp - 1;")
    println("t0 = mem[sp];")
    return "t0"


def return_space_and_label(name, count):

    printcm()
    printcm("// Space for returned value")

    label = f"{name}_{count}"
    println("sp = sp + 1;")

    return label


def goto_and_return(label):

    printcm()
    printcm("// Jump to func and create return point", tab=False)

    println(f"goto {label};", tab=False)
    printcm()
    println(f"{label}r:", tab=False)


def func_endpoint(name, level):

    printcm()
    printcm("// Label to jump around new func definitions")

    println(f"{name}_{level}: ;")


def tac_expr(expr, st, temp_count=0):

    if 'value' in expr:
        value = expr['value']
        if not isinstance(value, str) or value[0] == '"':
            return value
        elif isinstance(value, str):
            offset = st[value]  # TODO: st[value]
            sign = '+' if offset >= 0 else '-'
            println(f"t{temp_count} = fp {sign} {abs(offset)};  // {value}")
            println(f"t{temp_count} = mem[t{temp_count}];")

    if 'operator' in expr:

        left  = tac_expr(expr['value_left' ], st, temp_count)
        right = tac_expr(expr['value_right'], st, temp_count + 1)

        op = expr['operator']

        println(f"t{temp_count} = {left} {op} {right};")

    return f"t{temp_count}"


def tac_stmt(stmt, func_name, st, func_count_parent):

    if 'name' in stmt:
        assign_name = stmt['name']
        offset = st[assign_name]
    else:
        assign_name = None
    value = stmt['value']  # TODO: Non-literal values

    if isinstance(value, dict):
        if value['token_type'] == "func":

            func = value['func']

            # Start keeping track of instance count for function
            if func not in func_count_parent:
                func_count_parent[func] = [stmt, 0]

            printcm()
            printcm(f"// ---> {stmt['value']['func']}()")

            push_temps()
            push_params(value["parameters"], st)
            label = return_space_and_label(func, func_count_parent[func][1])
            goto_and_return(label)

            value_ = pop_return()

            if assign_name is not None:
                println(f"t9 = fp + {offset};  // {assign_name}")
                println(f"mem[t9] = {value_};")  # _ is dumb

            pop_params(value["parameters"])
            pop_temps()

            printcm()

            func_count_parent[func][1] += 1

            return

        elif value['token_type'] == 'expr':
            value = tac_expr(value, st)

        else:
            raise NotImplementedError

    if assign_name is not None:
        println(f"t9 = fp + {offset};  // {assign_name}")  # TODO: Be smart about the temp variable here
        println(f"mem[t9] = {value};")


def tac_for(stmt, func_name, st, func_count_scope):

    printcm()

    var_list  = stmt['expr_list']
    iterator  = stmt['iterator']['value']
    stmt_list = stmt['stmt_list']

    if len(var_list) > 1:
        raise NotImplementedError
    else:
        var = var_list[0]

    # Not iterating over a variable
    if isinstance(iterator, dict):

        if iterator['token_type'] == 'func':

            params = []
            for param in iterator['parameters']:
                value = param['value']

                # Function calls and variables not supported here yet
                if not isinstance(value, int):
                    raise NotImplementedError
                else:
                    params.append(value)

            if iterator['func'] == 'range':

                min_ = 0             if len(params) == 1 else params[0]
                max_ = params[1] - 1 if len(params)  > 1 else params[0] - 1
                step = params[2]     if len(params) == 3 else 1

                # TODO: Nested for statements
                # TODO: Descreasing loops (ie. step < 0)
                # TODO: Iterator declared before loop
                printcm("// For loop")
                println(f"int {var} = {min_};")
                printcm()
                println("for_0:")
                println(f"if ({var} > {max_}) goto for_0e;")
                printcm()

                for stmt in stmt_list:
                    tac_stmt(stmt, func_name, st, func_count_scope)

                println(f"{var} = {var} + {step};")
                println("goto for_0;")
                println("for_0e:")

            else:
                raise NotImplementedError
        else:
            raise NotImplementedError
    else:
        raise NotImplementedError


def tac_print()


def tac_return(stmt, st):

    printcm()
    printcm("// Saving return value")

    offset = st[stmt['value']]
    println(f"t0 = fp + {offset};")
    println("t0 = mem[t0];")
    println("t1 = fp - 1;")
    println("mem[t1] = t0;")


def tac_function(func, st, instance=0, func_count_parent={}):

    printcm()

    # Parameter offsets in st
    if 'args_list' in func:
        for i, param in enumerate(func['args_list'][:: -1]):
            st[param] = -i - 2

    if func in ['print']:
        tac_print(instance)
        return
    func_name = func['name']

    println(f"{func_name}_{instance}:", tab=False)

    init_function()
    init_local_var_space(st)
    printcm()

    func_count_scope = {}
    for stmt in func['stmt_list']:
        if stmt['token_type'] == 'func_def':
            name = stmt['name']
            if name not in func_count_scope:
                func_count_scope[name] = [stmt, 0]
            else:
                func_count_scope[name][1] = [stmt, func_count_parent[name][1]]

        elif stmt['token_type'] == 'assign_stmt':
            tac_stmt(stmt, func_name, st, func_count_scope)

        elif stmt['token_type'] == 'return':
            tac_return(stmt, st)

        elif stmt['token_type'] == 'for_stmt':
            tac_for(stmt, func_name, st, func_count_scope)

        elif stmt['token_type'] == 'value':
            if isinstance(stmt, dict):
                tac_stmt(stmt, func_name, st, func_count_scope)
            else:
                raise NotImplementedError
        else:
            raise NotImplementedError

    # Rewind stack
    finish_function(func_name, instance)

    # goto_endpoint(func_name)

    # Generate function TACs
    for func_name in func_count_scope:
        if func_name in func_count_parent:
            start = func_count_parent[func_name][1]
        else:
            func_count_parent[func_name] = [func, 0]
            start = 0
        end = func_count_scope[func_name][1]
        for instance in range(start, end):
            if func_name in ['print']:
                stmt_child = 'print'
                st_child   = {'_print' : 1}
            else:
                stmt_child = func_count_scope[func_name][0]
                st_child   = st[func_name]
            tac_function(stmt_child, st_child, instance)
        func_count_parent[func_name][1] = end


    #
    # func_endpoint(func_name, start_level + 1)


def create_tac(pt, st):
    init_memory(1000)
    init_registers()
    init_c_main()
    tac_function(pt, st)
    close_c_main()
