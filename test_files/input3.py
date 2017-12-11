# Functions with parameters demonstration
# Also uses the return value of the function


def test(a, b, c):

    x = a + b + c
    return x


d = test(1, 2, 4)

# Output = 6 @ mem[1]


# Not working:
#    Using multiple functions in one expression
#        d = test(1, 2, 3) + test(5, 6, 7)
#    Nesting functions
#        d = test(test(5, 6, 7), 2, 3)
