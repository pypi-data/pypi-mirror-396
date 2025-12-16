from functools import wraps


def cache_decorator(cache):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if args in cache:
                return cache[args]
            result = func(*args, **kwargs)
            cache[args] = result
            return result

        return wrapper

    return decorator
