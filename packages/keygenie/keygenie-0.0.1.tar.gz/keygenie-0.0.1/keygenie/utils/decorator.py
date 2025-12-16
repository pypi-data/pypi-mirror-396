"""装饰器工具模块"""

import time
from typing import Callable, TypeVar, Dict, Type, Any

T = TypeVar("T")
F = TypeVar("F", bound=Callable[..., Any])


def get_run_time(func: F) -> F:
    """
    打印方法的耗时

    Args:
        func: 要装饰的函数

    Returns:
        装饰后的函数，会在执行前后打印耗时信息
    """

    def call_func(*args: Any, **kwargs: Any) -> Any:
        begin_time = time.time()
        ret = func(*args, **kwargs)
        end_time = time.time()
        run_time = end_time - begin_time
        print(
            "function {}, args={}, kwargs={}, time = {}".format(
                func.__name__, args, kwargs, run_time
            )
        )
        return ret

    return call_func  # type: ignore


def singleton(cls: Type[T]) -> Type[T]:
    """
    单例装饰器

    确保类只有一个实例，多次实例化返回同一个对象。

    Args:
        cls: 要装饰的类

    Returns:
        装饰后的类，保证单例模式
    """
    _instance: Dict[Type[T], T] = {}

    def inner(*args: Any, **kwargs: Any) -> T:
        if cls not in _instance:
            _instance[cls] = cls(*args, **kwargs)
        return _instance[cls]

    return inner  # type: ignore
