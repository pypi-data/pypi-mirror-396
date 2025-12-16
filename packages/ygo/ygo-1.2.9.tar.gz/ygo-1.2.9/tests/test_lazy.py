# -*- coding: utf-8 -*-
"""
---------------------------------------------
Copyright (c) 2025 ZhangYundi
Licensed under the MIT License. 
Created on 2025/6/29 10:49
Email: yundi.xxii@outlook.com
Description: 
---------------------------------------------
"""

import ygo

def test_import_module():
    import os
    os_path = ygo.lazy_import("os.path")
    assert os_path.join("a", "b") == os.path.join("a", "b")

def test_import_function():
    from os.path import join
    assert ygo.lazy_import("os.path.join")("a", "b") == join("a", "b")
