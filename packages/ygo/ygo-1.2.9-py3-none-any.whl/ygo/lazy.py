# -*- coding: utf-8 -*-
"""
---------------------------------------------
Copyright (c) 2025 ZhangYundi
Licensed under the MIT License. 
Created on 2025/6/29 10:36
Email: yundi.xxii@outlook.com
Description:
---------------------------------------------
"""

from typing import Any
from .utils import locate

class LazyImport:
    def __init__(self, full_name: str):
        self._full_name = full_name
        self._obj = None

    def _load(self) -> Any:
        if self._obj is None:
            self._obj = locate(self._full_name)
        return self._obj

    def __getattr__(self, attr: str) -> Any:
        obj = self._load()
        return getattr(obj, attr)

    def __dir__(self) -> list[str]:
        obj = self._load()
        return dir(obj)

    def __call__(self, *args, **kwargs) -> Any:
        obj = self._load()
        if isinstance(obj, type):
            return obj(*args, **kwargs)
        elif callable(obj):
            return obj(*args, **kwargs)
        else:
            raise TypeError(f"The target `{self._full_name}` is not callable or instantiable.")

    def __str__(self):
        return self._full_name

    def __repr__(self):
        return self._full_name

def lazy_import(full_name: str):
    """实现模块和方法的懒加载"""
    return LazyImport(full_name)