def max_sub_array(array):

    # Best known start/stop indices
    max_start  = 0
    max_end    = 0

    # Best known size
    max_sum    = -99999

    # Current subarray sum
    cum_sum    = 0
    start      = 0

    for i, item in enumerate(array): # TODO: Enumerate not yacc'd correctly

        cum_sum += item

        # New max subarray?
        if cum_sum > max_sum:
            max_sum = cum_sum
            max_start = start
            max_end = i

        # Reset current sum if a negative is found
        elif cum_sum < 0:
            start = i + 1
            cum_sum = 0

    print("Max sum         {}".format(max_sum))
    print("Max start index {}".format(max_start))
    print("Max end index   {}".format(max_end))

# a = 5
# b = 7
# a = -b
#
# d  = "test string"

c = [10, 4, 6, -3, 4, -5, -2, 6]

max_sub_array(c)
