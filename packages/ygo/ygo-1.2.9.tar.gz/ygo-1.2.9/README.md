# ygo
一个轻量级 Python 工具包，底层基于 joblib 和 tqdm 、loguru 实现，支持
- 并发执行（带进度条）
- 延迟调用
- 链式绑定参数
- 函数信息获取
- 模块/函数动态加载...
- 并结合 ylog 提供日志记录能力

### 安装
```shell
pip install -U ygo
```

### 🧰 功能概览

| 模块   | 功能                                                         |
| :----- | :----------------------------------------------------------- |
| `ygo`  | 支持并发执行（带进度条）、延迟调用、函数信息获取以及模块/函数动态加载等功能 |
| `ylog` | 日志模块，提供统一的日志输出接口                             |

### 示例

```
├── a
│   ├── __init__.py
│   └── b
│       ├── __init__.py
│       └── c.py
└── test.py

c.py 中定义了目标函数
def test_fn(a, b=2):
    return a+b
```

#### 场景1: 并发执行

```python
import ygo
import ylog
from a.b.c import test_fn

with ygo.pool(n_jobs=5, show_progress=True) as go:
    for i in range(10):
        go.submit(test_fn)(a=i, b=2*i)
    for res in go.do():
        ylog.info(res)
```

#### ✅ `ygo.pool` 支持的参数

| 参数名        | 类型 | 描述                                                         |
| ------------- | ---- | ------------------------------------------------------------ |
| n_jobs        | int  | 并行任务数(<=1 表示串行)                                     |
| show_progress | bool | 是否显示进度条                                               |
| backend       | str  | 执行后端（默认 'threading'，可选 'multiprocessing' 或 'loky'） |

#### 场景2: 延迟调用

```
>>> fn = delay(test_fn)(a=1, b=2)
>>> fn()
3
>>> # 逐步传递参数
>>> fn1 = delay(lambda a, b, c: a+b+c)(a=1)
>>> fn2 = delay(fn1)(b=2)
>>> fn2(c=3)
6
>>> # 参数更改
>>> fn1 = delay(lambda a, b, c: a+b+c)(a=1, b=2)
>>> fn2 = delay(fn1)(c=3, b=5)
>>> fn2()
9
```

#### 场景3: 获取目标函数信息

```
>>> ygo.fn_info(test_fn)
=============================================================
    a.b.c.test_fn(a, b=2)
=============================================================
    def test_fn(a, b=2):
    return a+b
```

#### 🔍 其他函数信息工具

| 方法名                    | 描述                                     |
| ------------------------- | ---------------------------------------- |
| `fn_params(fn)`           | 获取函数实参                             |
| `fn_signature_params(fn)` | 获取函数定义的所有参数名                 |
| `fn_code(fn)`             | 获取函数源码字符串                       |
| `fn_path(fn)`             | 获取函数所属模块路径                     |
| `fn_from_str(s)`          | 根据字符串导入函数（如 "a.b.c.test_fn"） |
| `module_from_str(s)`      | 根据字符串导入模块                       |

#### 场景4: 通过字符串解析函数并执行

```
>>> ygo.fn_from_str("a.b.c.test_fn")(a=1, b=5)
6
```
