from functools import wraps


def debug(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        print(func.__qualname__)
        print(args, kwargs)
        return func(*args, **kwargs)
    return wrapper