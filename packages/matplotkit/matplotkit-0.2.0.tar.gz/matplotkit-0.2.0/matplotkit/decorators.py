#!/usr/bin/env python 3.11.0
# -*-coding:utf-8 -*-
# @Author  : Shuang (Twist) Song
# @Contact   : SongshGeo@gmail.com
# GitHub   : https://github.com/SongshGeo
# Website: https://cv.songshgeo.com/

from functools import wraps
from typing import Callable, Optional, Tuple

import matplotlib.pyplot as plt


def with_axes(
    decorated_func: Optional[Callable] = None, figsize: Tuple[int, int] = (6, 4)
) -> Callable:
    """Decorator to add a default axes to the decorated function.

    Args:
        decorated_func:
            The function to be decorated.
        figsize:
            The size of the figure.

    Returns:
        The decorated function.
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            ax = kwargs.get("ax", None)
            if ax is None:
                _, ax = plt.subplots(figsize=figsize)
                kwargs["ax"] = ax
                result = func(*args, **kwargs)
                return result
            else:
                return func(*args, **kwargs)

        return wrapper

    # 检查是否有参数传递给装饰器，若没有则返回装饰器本身
    return decorator(decorated_func) if decorated_func else decorator
