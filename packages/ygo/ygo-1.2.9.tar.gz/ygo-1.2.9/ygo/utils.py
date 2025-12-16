# -*- coding: utf-8 -*-
"""
---------------------------------------------
Created on 2025/5/26 23:31
@author: ZhangYundi
@email: yundi.xxii@outlook.com
---------------------------------------------
"""

import inspect
import os
from functools import wraps
from pathlib import Path
import warnings
from typing import Any

from .delay import delay

def deprecated(use_instead: str = None):
    """
    标记方法为弃用

    Parameters
    ----------
    use_instead: str
        推荐替代使用的方法或者类名称
    Returns
    -------

    """

    def decorator(func):
        """
        装饰器
        Parameters
        ----------
        func: callable
            被装饰的函数
        Returns
        -------

        """
        @wraps(func)
        def wrapper(*args, **kwargs):
            msg = f"`{func.__name__}` is deprecated. "
            if use_instead:
                msg += f"Please use `{use_instead}` instead."
            warnings.warn(msg, category=DeprecationWarning, stacklevel=2)
            return func(*args, **kwargs)
        return wrapper
    return decorator

def fn_params(func: callable):
    """
    获取fn的参数
    Parameters
    ----------
    func: callable
        需要获取参数的callable对象
    Returns
    -------
    list[tuple]

    """
    stored = delay(func)().stored_kwargs.items()
    return sorted(stored)


def fn_signature_params(func: callable):
    """获取fn所有定义的参数"""
    return sorted(list(inspect.signature(func).parameters.keys()))


def fn_path(fn: callable) -> str:
    """
    获取func所在的模块层级结构
    Parameters
    ----------
    fn: callable
        需要获取结构的callable对象
    Returns
    -------
    str
        用 `.` 连接各级层级
    """
    module = fn.__module__
    # 检查模块是否有 __file__ 属性
    if module.startswith('__main__'):
        if hasattr(module, '__file__'):
            module = module.__file__
        else:
            # 如果在交互式环境中，返回 None 或者一个默认值
            module = "<interactive environment>"
    if module.endswith('.py'):
        module = module.split('.py')[0].split(str(Path(__file__).parent.parent.absolute()))[-1]
        module = '.'.join(module.strip(os.sep).split(os.sep))
    return module


def fn_code(fn: callable) -> str:
    """
    返回fn具体的定义代码

    Parameters
    ----------
    fn: callable
        需要获取具体定义代码的callable对象

    Returns
    -------
    str
        以字符串封装定义代码

    Examples
    --------

    >>> def test_fn(a, b=2):
    >>>     return a+b
    >>> print(fn_code())
    def test_fn(a, b=2):
        return a+b
    """
    return inspect.getsource(fn)


def fn_info(fn: callable) -> str:
    """获取函数的fn_mod, params, code"""
    # mod = fn_path(fn)
    params = fn_params(fn)
    code = fn_code(fn)
    all_define_params = sorted(list(inspect.signature(fn).parameters.keys()))

    default_params = {k: v for k, v in params}
    params_infos = list()
    for p in all_define_params:
        if p in default_params:
            params_infos.append(f'{p}={default_params[p]}')
        else:
            params_infos.append(p)
    params_infos = ', '.join(params_infos)

    s = f"""
=============================================================
{fn.__name__}({params_infos})
=============================================================
{code}
    """
    return s

@deprecated("lazy_import")
def fn_from_str(s):
    """
    字符串导入对应fn
    s: a.b.c.func
    Parameters
    ----------
    s: str
        模块的路径，分隔符 `.`
    """
    import importlib
    *m_path, func = s.split(".")
    m_path = ".".join(m_path)
    mod = importlib.import_module(m_path)
    _callable = getattr(mod, func)
    return _callable

@deprecated("lazy_import")
def module_from_str(s):
    """字符串导入模块"""
    import importlib
    m_path = ".".join(s.split('.'))
    mod = importlib.import_module(m_path)
    return mod

def locate(path: str) -> Any:
    """
    Notes
    -----
    Copyright (c) Facebook, Inc. and its affiliates. All Rights Reserved

    Locate an object by name or dotted path, importing as necessary.
    This is similar to the pydoc function `locate`, except that it checks for
    the module from the given path from back to front.
    """
    if path == "":
        raise ImportError("Empty path")
    from importlib import import_module
    from types import ModuleType

    parts = [part for part in path.split(".")]
    for part in parts:
        if not len(part):
            raise ValueError(
                f"Error loading '{path}': invalid dotstring."
                + "\nRelative imports are not supported."
            )
    assert len(parts) > 0
    part0 = parts[0]
    try:
        obj = import_module(part0)
    except Exception as exc_import:
        raise ImportError(
            f"Error loading '{path}':\n{repr(exc_import)}"
            + f"\nAre you sure that module '{part0}' is installed?"
        ) from exc_import
    for m in range(1, len(parts)):
        part = parts[m]
        try:
            obj = getattr(obj, part)
        except AttributeError as exc_attr:
            parent_dotpath = ".".join(parts[:m])
            if isinstance(obj, ModuleType):
                mod = ".".join(parts[: m + 1])
                try:
                    obj = import_module(mod)
                    continue
                except ModuleNotFoundError as exc_import:
                    raise ImportError(
                        f"Error loading '{path}':\n{repr(exc_import)}"
                        + f"\nAre you sure that '{part}' is importable from module '{parent_dotpath}'?"
                    ) from exc_import
                except Exception as exc_import:
                    raise ImportError(
                        f"Error loading '{path}':\n{repr(exc_import)}"
                    ) from exc_import
            raise ImportError(
                f"Error loading '{path}':\n{repr(exc_attr)}"
                + f"\nAre you sure that '{part}' is an attribute of '{parent_dotpath}'?"
            ) from exc_attr
    return obj
