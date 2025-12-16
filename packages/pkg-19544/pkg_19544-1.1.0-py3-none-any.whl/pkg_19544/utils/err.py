from functools import wraps
from logging import ERROR, basicConfig, getLogger


basicConfig(level=ERROR, format="Error: %(message)s")
logger = getLogger(__name__)


def raise_on_false(exception_type=ValueError, message="Function returned False"):
    """
    A decorator that raises an exception if the decorated function returns False.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            if result is False:
                logger.error(f'{message}', stacklevel=2)
                raise exception_type(message)
            return result
        return wrapper
    return decorator
