# -*- coding: utf-8 -*-
"""
---------------------------------------------
Created on 2025/5/26 20:12
@author: ZhangYundi
@email: yundi.xxii@outlook.com
---------------------------------------------
"""

import functools
import inspect


class DelayedFunction:

    def __init__(self, func):
        self.func = func
        self._fn_params_k = inspect.signature(self.func).parameters.keys()
        self.stored_kwargs = self._get_default_args(func)
        if hasattr(func, 'stored_kwargs'):
            self.stored_kwargs.update(func.stored_kwargs)

    def _get_default_args(self, func):
        signature = inspect.signature(func)
        return {
            k: v.default
            for k, v in signature.parameters.items()
            if v.default is not inspect.Parameter.empty
        }

    def __call__(self, *args, **kwargs):
        def delayed(*args, **_kwargs):
            new_kwargs = {k: v for k, v in self.stored_kwargs.items()}
            for k, v in _kwargs.items():
                if k not in self._fn_params_k:
                    continue
                new_kwargs[k] = v
            return self.func(*args, **new_kwargs)

        self._stored_kwargs(**kwargs)
        new_fn = functools.wraps(self.func)(delayed)
        new_fn.stored_kwargs = self.stored_kwargs
        return new_fn

    def _stored_kwargs(self, **kwargs):
        for k, v in kwargs.items():
            if k not in self._fn_params_k:
                continue
            self.stored_kwargs[k] = v


def delay(func):
    """
    延迟执行
    Parameters
    ----------
    func: Callable
        需要延迟执行的对象, 必须是一个Callable对象

    Returns
    -------
    DelayedFunction
        将预先设置好的参数包装进原始的Callable对象中

    Examples
    --------

    场景1：基本使用

    >>> fn = delay(lambda a, b: a+b)(a=1, b=2)
    >>> fn()
    3

    场景2: 逐步传递参数

    >>> fn1 = delay(lambda a, b, c: a+b+c)(a=1)
    >>> fn2 = delay(fn1)(b=2)
    >>> fn2(c=3)
    6

    场景3: 参数更改

    >>> fn1 = delay(lambda a, b, c: a+b+c)(a=1, b=2)
    >>> fn2 = delay(fn1)(c=3, b=5)
    >>> fn2()
    9
    """
    return DelayedFunction(func)

