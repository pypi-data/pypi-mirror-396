# -*- coding: utf-8 -*-
"""
---------------------------------------------
Created on 2025/5/27 09:14
@author: ZhangYundi
@email: yundi.xxii@outlook.com
---------------------------------------------
"""

import time

import ygo


def sample_task_add(a, b):
    time.sleep(1)
    return a + b


def sample_task_sub(a, b):
    time.sleep(1)
    return a - b


def warn_task():
    raise ygo.WarnException("Test warning")


def error_task():
    raise ValueError("Test error")


def test_pool_submit_and_do():
    with ygo.pool() as go:
        go.submit(sample_task_add, "task add")(a=1, b=2)
        go.submit(sample_task_add, "task add")(a=2, b=3)
        go.submit(sample_task_sub, "task sub")(a=5, b=1)

        results = go.do()

    assert len(results) == 3
    assert results[0] == 3
    assert results[1] == 5
    assert results[2] == 4


def test_pool_error_handling():
    with ygo.pool() as go:
        go.submit(error_task, job_name="task_error")()

        results = go.do()

    assert len(results) == 1
    assert results[0] is None


def test_pool_warn_exception_handled():
    """测试 WarnException 是否被记录警告但继续执行"""
    with ygo.pool(n_jobs=1) as go:
        go.submit(warn_task, job_name="task_warn")()

        results = go.do()

        assert len(results) == 1
        assert results[0] is None  # WarnException 不中断流程


def test_pool_progress_bar_disabled():
    """测试关闭进度条时的行为"""
    with ygo.pool(n_jobs=2, show_progress=False) as go:
        go.submit(sample_task_add, "test add")(a=1, b=2)
        go.submit(sample_task_add, "test add")(a=3, b=4)

        results = go.do()

        assert len(results) == 2
        assert 3 == results[0]
        assert 7 == results[1]


def test_pool_with_one_jobs():
    """测试 n_jobs=1 时是否退化为串行执行"""
    with ygo.pool(n_jobs=1) as go:
        go.submit(sample_task_add, "test add")(a=1, b=2)
        go.submit(sample_task_add, "test add")(a=3, b=4)

        results = go.do()

        assert len(results) == 2
        assert 3 == results[0]
        assert 7 == results[1]


def test_delay_basic_usage():
    """场景1：基本使用"""
    fn = ygo.delay(lambda a, b: a + b)(a=1, b=2)
    assert fn() == 3


def test_delay_partial_kwargs():
    """场景2：逐步传递参数"""
    fn1 = ygo.delay(lambda a, b, c: a + b + c)(a=1)
    fn2 = ygo.delay(fn1)(b=2)
    assert fn2(c=3) == 6


def test_delay_override_kwargs():
    """场景3：参数更改"""
    fn1 = ygo.delay(lambda a, b, c: a + b + c)(a=1, b=2)
    fn2 = ygo.delay(fn1)(c=3, b=5)  # 修改 b 的值
    assert fn2() == 9


def test_delay_with_no_call():
    """延迟函数在未调用时不会执行"""
    called = False

    def side_effect(*args, **kwargs):
        nonlocal called
        called = True
        return None

    delayed_fn = ygo.delay(side_effect)(x=1)
    assert not called  # 还未执行
    delayed_fn()
    assert called  # 执行后标记为 True


def test_fn_signature_params():
    assert ygo.fn_signature_params(sample_task_add) == ['a', 'b']


def test_fn_params_with_defaults():
    delayed = ygo.delay(sample_task_add)(a=3)
    print(ygo.fn_params(delayed))
    assert dict(ygo.fn_params(delayed)) == {'a': 3, }


def test_fn_path_for_function():
    fn_path = ygo.fn_path(sample_task_add)
    assert 'tests.test_ygo' in fn_path or '__main__' in fn_path


def test_fn_code():
    code = ygo.fn_code(sample_task_add)
    assert "def sample_task_add(a, b):" in code
    assert "return a+b" in code


def test_fn_info():
    info = ygo.fn_info(sample_task_add)
    assert "sample_task_add(a, b)" in info
    assert "def sample_task_add(a, b):" in info


def test_fn_from_str():
    func = ygo.fn_from_str("ygo.utils.fn_from_str")
    assert func.__name__ == "fn_from_str"


def test_module_from_str():
    mod = ygo.module_from_str("ygo.utils")
    assert mod.__name__ == "ygo.utils"


def test_fn_params_with_no_defaults():
    def no_defaults(x, y):
        pass

    delayed = ygo.delay(no_defaults)()
    assert dict(ygo.fn_params(delayed)) == {}
