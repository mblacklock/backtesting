def hello_world():
    return 'hello world'

def create_num_list(n):
    return range(n)

def custom_func_x(x, c, p):
    return c * x ** p

def custom_non_lin_num_list(length, const, power):
    return [custom_func_x(x, const, power) for x in range(length)]
