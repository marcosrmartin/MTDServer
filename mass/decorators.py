import time
import functools
from .config import logger

def timing_decorator(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        elapsed_time = end_time - start_time
        logger.debug(f"Method {func.__name__} execution took: {elapsed_time:.6f} seconds.")
        return result
    return wrapper

def apply_timing_to_methods(decorator):
    def decorate(cls):
        for attr in dir(cls):
            if attr.startswith("__") and attr.endswith("__"):
                continue
            original_method = getattr(cls, attr)
            if callable(original_method):
                decorated_method = decorator(original_method)
                setattr(cls, attr, decorated_method)
        return cls
    return decorate
