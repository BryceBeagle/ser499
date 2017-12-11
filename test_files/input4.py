# For loop demonstration:

# Working:

j = 1

for i in range(2, 10, 3):
    j = j + 1


# Output = 4 @ mem[1]


# Not working:
#   Using anything but range
#   Using not literals as parameters for range
#   Using a negative value (as with any other use of negatives)
#   Using the iterating value within the loop
#   Using an iterator declared before the loop
#   Nested loops
