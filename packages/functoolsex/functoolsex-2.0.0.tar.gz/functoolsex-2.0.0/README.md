# functools-ex

一个实用为本的 Python 函数式方言库。能看到这里的，可以自己读源码了解细节。

## 使用

只提供三个流程调度方言，可结合 for map while 等语句、表达式 及 toolz 等其它函数库使用

```python
def test_F():  # 顺序处理数据，无中间 return 不处理后续的情况，有点像 data = f1(); data = f2(); return data; 的结构。
    """It is faster than the same one in fn.
    >>> from functools import partial as P
    >>> from operator import add
    >>> F(add, 1)(2) == P(add, 1)(2)
    True
    >>> from operator import add, mul
    >>> (F(add, 1) >> P(mul, 3))(2)
    9
    """
def test_op():  # 顺序处理数据，有中间 return 但却不用返回具体错误原因，有点像 if False: return; 的结构。
    """ Option filter map and get value, like Option in fn.
    >>> from operator import add
    >>> (op_() >> op_is_value)(1)
    True
    >>> (op_() >> op_is_empty)(1)
    False
    >>> (op_() >> op_is_empty)('__functoolsex__op__empty')  # never use this string
    True
    >>> (op_() >> op_filter(lambda x: x == 1) >> op_or_else(-1))(1)
    1
    >>> (op_() >> op_filter(lambda x: x > 1) >> op_or_else(-1))(1)
    -1
    >>> (op_() >> op_filter(lambda x: x == 1) >> op_or_call(add, 0, -1))(1)
    1
    >>> (op_() >> op_filter(lambda x: x > 1) >> op_or_call(add, 0, -1))(1)
    -1
    >>> (op_() >> op_filter(lambda x: x == 1) >> op_map(lambda x: x + 1) >> op_or_else(None))(1)
    2
    >>> (op_() >> op_filter(lambda x: x > 1) >> op_map(lambda x: x + 1) >> op_or_else(-1))(1)
    -1
    """
def test_e():  # 顺序处理数据，有中间 return 且要给出出错原因，有点像 raise ValueError() 的结构。
    """Either filter map and get value, like op.
    >>> from operator import add, mul
    >>> e_ok(1)
    ('__functoolsex__e__ok', 1)
    >>> e_err(1)
    ('__functoolsex__e__err', 1)
    >>> (e_() >> e_is_ok)(1)
    True
    >>> (e_() >> e_is_err)(1)
    False
    >>> (e_() >> e_filter(lambda x: x == 1, '') >> e_is_ok)(1)
    True
    >>> (e_() >> e_filter(lambda x: x == 1, 'need eq 1'))(1)
    ('__functoolsex__e__ok', 1)
    >>> (e_() >> e_filter(lambda x: x == 1, 'need eq 1'))(2)
    ('__functoolsex__e__err', 'need eq 1')
    >>> (e_() >> e_map(lambda x: x + 1))(1)
    ('__functoolsex__e__ok', 2)
    >>> (e_() >> e_or_else(2))(1)
    ('__functoolsex__e__ok', 1)
    >>> (e_() >> e_filter(lambda x: x == 1, '') >> e_or_else(2))(3)
    ('__functoolsex__e__ok', 2)
    >>> (e_() >> e_get_or(2))(1)
    1
    >>> (e_() >> e_filter(lambda x: x == 1, '') >> e_get_or(2))(3)
    2
    >>> (e_() >> e_filter(lambda x: x == 1, '') >> e_get_or_call(mul, 1, 2))(3)
    2
    """
def test_log():
    """Print and return arg. Can be useful to debug. Can off it by env PY__FUNCTOOLSEX_LOG_OFF.
    Warn: log("It is: %s", LOGGER.info) return a function.
    >>> from operator import add, mul
    >>> (F(add, 1) >> log('add res: %s') >> P(mul, 3))(2)
    add res: 3
    9
    """
```

## 性能

### F

尽管压榨到了 CPython 的性能极限，F 这种模式仍然比表达式计算慢几十倍(但在 PyPy 中比 for func 对象 快多了, 几乎和表达式一样快)。
但 F 比 cytoolz 中的如 thread_last 这种一样功能的，却没慢那么多，也就 3、4 倍这种差距，主要是每次连接要多一个 partial。

(F(add, 1) >> P(mul, 3))(2) 在 CPython 中很蠢，在 PyPy 中虽然跟表达式一样快，但也没什么必要，就是说不要用 operator 库。

F 真正的价值在于逻辑调度，而非计算逻辑，后者使用表达式就好，慢了还可以上 numby numba。

```python
# 这段代码的核心价值是强制转换成了声明式风格。
def conv_a_data_to_dict(data: bytes) -> dict:
    def some_process(s: str) -> str:
        # do some code, like while\if\for...
        return new_s

    return (
        F(lambda x: x.decode('gbk'))
        >> (lambda x: x.upper().lower())
        >> some_process
    )(data)
```

### op_

同样的，表达式处理计算，而 op_ 处理逻辑。

```python
# 这段代码用来处理默认值
def get_conf_item(filename: str, key: str):
    def read_file(filename) -> str | OpEmpty:
        if 'no file' in filename:
            return OP_EMPTY
        return filename + 'read value'

    def conv_value_to_dict(file_value) -> dict | None:
        # 其实这里也应返回 OP_EMPTY 而不是 None，这里只作演示
        return (
            F(lambda x: x.encode())
            >> lambda x: json.loads(x) if len(x) > 1 else None
            >> ...
        )(file_value)

    return (
        op_()
        >> op_map(read_file)
        >> op_map(conv_to_dict)
        >> op_filter(lambda x: x is not None)
        >> op_map(lambda x: x.get(key, OP_EMPTY))
        >> op_or_else('a default value')
    )(filename)

```

### e_

对于后端的用户上送参数做校验时使用，就不举例子了。

不过要注意的是，在非纯函数的薄副作层代码，用 if else try except return raise 也是推荐的。

```python
def some_view(req):
    try:
        check(req.args)
    except InvalidValueError as e:
        log(e)
        raise HttpError401(process(e))
    ...
    # from redis
    # from database
    # conv to res json
    return res_json
```

## 使用建议

其实函数式是在命令式的基础上强加了一层复杂 lambda 的命名，而非只注释加代码块，虽然 def 在 CPython 中有开销。

如果是高并发快响应类型的类型：
1. 如果只能使用 fastapi 这种要单核处理成百上千并发的，就不能用函数式，用 pythoner 风格就好。
2. 如果使用 pypy flask gevent 这种，可以完全使用本方言，性能极佳。（注意pypy3.11还是要 from __future__ import annotations）

如果是普通的小脚本，没那么高的性能要求，建议体验各种函数式风格，如 fn funcy toolz。

不过，性能问题在未实测之前都不能确定是问题，只要不是那些生产上必须要极限压榨性能的项目，都可以试了再说，最后只改痛点即可。
1. 很多项目的接口痛点可能是 uuid4() 这种毫秒级的，或是 PIL 这种大动作，而不是 F lambda 这种百纳秒级的。
2. 真要做计算之类的，numpy、pandas、numba 哪个都是专业的。
3. Cython 对于一些自定义数据结构有很好的优化能力，也能确保解决单一痛点问题。

总之。
如果你不是 ins 那种级别的专家团队要面对上亿用户的项目，或者所在团队只懂写垃圾代码，就可以大胆尝试，尤其是在个人项目中。

### 三方库

pyrsistent 性能在 CPython 和 PyPy 下已足够好，虽会比原生类型慢一点，除了 fastapi 那种场景，都值得一用。

pytoolz cytoolz 普遍性能不是很好，本工程 1.0 版还专门优化替换过，但其实平时也很难用到里面的内容。
比如 get get_in 这些，很多时候用表达式造个轮子会更快也更明确，而且 它 和 pyrsistent 一起用也有 bug。

funcy 不怎么了解，但看 api 跟 toolz 差不多。不过 cytoolz 有优化，而 funcy 就不知道了。

只要不是必须要处理迭代器的场景，如内存限制等，就不要用那些包括官方可迭代库在内的三方库。
而字典和列表处理，其实 pyrsistent 中也有些内置的方法(transform相关)可用，修改也有实测高性能的 evolver 可用。


还有，很多时候，让 AI 生成 utils 的代码要方便很多，所以 toolz 和 funcy 都不是必选，但强烈推荐 pyrsistent。


## 2.0 改版

1.0 系列有大量的看上去不错却没什么大用的语法糖，2.0 只留下了这几个方言函数，并增加了注解系统，也不再支持低版 Python。


# Ignore these
```bash
# doc test
python -m doctest functoolsex/func.py

# edit tag in setup.py
git tag v0.0.1
rm dist/functoolsex-*
python setup.py sdist bdist_wheel
twine upload dist/*
```
