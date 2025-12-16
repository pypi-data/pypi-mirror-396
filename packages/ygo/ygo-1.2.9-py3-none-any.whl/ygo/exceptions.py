# -*- coding: utf-8 -*-
"""
---------------------------------------------
Created on 2024/12/18 下午7:01
@author: ZhangYundi
@email: yundi.xxii@outlook.com
---------------------------------------------
"""

from dataclasses import dataclass

class WarnException(Exception):
    """自定义异常类，仅用于警告"""
    def __init__(self, message):
        super().__init__(message)  # 调用父类的构造函数

@dataclass
class FailTaskError:
    task_name: str
    error: Exception

    def __str__(self):
        return f"""
[失败任务]: {self.task_name}
[错误信息]: \n{self.error}
"""

    def __repr__(self):
        return self.__str__()