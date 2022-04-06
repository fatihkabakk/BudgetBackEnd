from core.logging import Logger
from functools import wraps


logger = Logger(__file__, 'Cache.log')
mem_cache = {}


@logger.log
def cache(func):
    @wraps(func)
    def wrapper(*args):
        cache_name = func.__name__ + f"({', '.join(str(i) for i in args)})"
        if cache_name in mem_cache.keys():
            data = mem_cache[cache_name]
        else:
            data = func(*args)
            if data:
                mem_cache[cache_name] = data
        return data
    return wrapper


@logger.log
def del_from_cache(_cache_name):
    def clear_cache(func):
        @wraps(func)
        def wrapper(*args):
            func(*args)
            for i in mem_cache.copy().keys():
                if _cache_name in i:
                    del mem_cache[i]
        return wrapper
    return clear_cache


def test():
    @cache
    def x(a: 'int | float'):
        return a + 2

    @del_from_cache('x')
    def manipulate():
        pass

    print(x(3))
    print(mem_cache)
    manipulate()
    print(mem_cache)


if __name__ == '__main__':
    test()
