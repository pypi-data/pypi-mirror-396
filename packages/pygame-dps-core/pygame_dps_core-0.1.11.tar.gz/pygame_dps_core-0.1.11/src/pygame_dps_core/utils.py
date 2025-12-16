import functools
import pathlib
import threading
from typing import Any, Dict, Tuple


def coroutine(f):
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        pipe = f(*args, **kwargs)
        next(pipe)
        return pipe

    return wrapper


# debounce behaviour: timer after initial function call that gets reset
# on subsequent calls within the timeout window
def debounce(timeout: float):
    def decorator(func):
        if timeout <= 0:
            return func

        # should kick off a new timer if the function
        # is called with different arguments
        timers: Dict[Tuple[Any, ...], threading.Timer] = {}

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # function arguments must be hashable
            key = (*args, *kwargs.values())
            timer = timers.get(key, None)
            if timer is not None:
                timer.cancel()
            timer = threading.Timer(timeout, func, args, kwargs)
            timer.start()
            timers[key] = timer

        return wrapper

    return decorator


def normalize_path_str(path: str | pathlib.PurePath) -> pathlib.PurePath:
    """Return a platform-agnostic PurePath version of the given path"""
    p = pathlib.PureWindowsPath(path)
    return pathlib.PurePath(p.as_posix())


__all__ = [
    "debounce",
    "normalize_path_str",
]
