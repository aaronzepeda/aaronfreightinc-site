def add_leading_zeros(num, length):
    num_str = str(num)
    num_zeros = length - len(num_str)
    if num_zeros > 0:
        num_str = '0' * num_zeros + num_str
    return num_str