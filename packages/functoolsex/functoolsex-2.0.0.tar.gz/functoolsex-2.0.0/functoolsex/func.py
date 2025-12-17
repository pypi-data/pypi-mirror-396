from __future__ import annotations

import os
from functools import partial
from typing import Callable, Literal, TypeVar, Generic, ParamSpec, TypeAlias, TypeGuard

PS = ParamSpec('PS')
BE = TypeVar("BE", bound=BaseException)

T = TypeVar('T')
R = TypeVar('R')
R2 = TypeVar('R2')


def identity(x: T) -> T:
    return x


__all__ = (
    "P", "F",
    "op_", "OpEmpty", "OP_EMPTY", "op_is_value", "op_is_empty", "op_filter", "op_map", "op_or_else", "op_or_call",
    "e_", "EitherOk", "EitherErr", "Either", "e_ok", "e_err", "e_is_ok", "e_is_err", "e_filter", "e_map",
    "e_or_else", "e_or_call", "e_get_or", "e_get_or_call",
    "log",
)

P = partial

A = TypeVar('A')
B = TypeVar('B')
C = TypeVar('C')


def _F_pipe_executor(g: Callable[[B], C], f: Callable[[A], B], x: A) -> C:
    return g(f(x))


def test_F():
    """It is faster than the same one in fn.
    >>> from functools import partial as P
    >>> from operator import add
    >>> F(add, 1)(2) == P(add, 1)(2)
    True
    >>> from operator import add, mul
    >>> (F(add, 1) >> P(mul, 3))(2)
    9
    """


class F(partial[R], Generic[R]):
    __slots__: tuple[str, ...] = ()

    def __rshift__(self, g: Callable[[R], R2]) -> "F[R2]":
        return self.__class__(_F_pipe_executor, g, self)  # pyright: ignore [reportReturnType]


def test_op():
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


OpEmpty = Literal['__functoolsex__op__empty']
__op_empty: OpEmpty = '__functoolsex__op__empty'
OP_EMPTY: OpEmpty = __op_empty


def op_() -> F[Callable[[T], T]]:
    return F(identity)


def op_is_value(val: T) -> TypeGuard[T]:
    return val != __op_empty


def op_is_empty(val: object) -> TypeGuard[OpEmpty]:
    return val == __op_empty


V = TypeVar('V')
U = TypeVar('U')


def op_filter(func: Callable[[V], bool]) -> Callable[[V | OpEmpty], V | OpEmpty]:
    def f(val: V | OpEmpty) -> V | OpEmpty:
        return val if ((val != __op_empty) and func(val)) else __op_empty

    return f


def op_map(func: Callable[[V], U]) -> Callable[[V | OpEmpty], U | OpEmpty]:
    def f(val: V | OpEmpty) -> U | OpEmpty:
        return func(val) if val != __op_empty else __op_empty

    return f


def op_or_else(else_val: U) -> Callable[[V | OpEmpty], V | U]:
    def f(val: V | OpEmpty) -> V | U:
        return else_val if val == __op_empty else val

    return f


def op_or_call(func: Callable[PS, U], *args: PS.args, **kwargs: PS.kwargs) -> Callable[[V | OpEmpty], V | U]:
    def f(val: V | OpEmpty) -> V | U:
        return func(*args, **kwargs) if val == __op_empty else val

    return f


def test_e():
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


EitherOk: TypeAlias = tuple[Literal['__functoolsex__e__ok'], V]
EitherErr: TypeAlias = tuple[Literal['__functoolsex__e__err'], U]
Either: TypeAlias = EitherOk[V] | EitherErr[U]
__e_ok: Literal['__functoolsex__e__ok'] = '__functoolsex__e__ok'
__e_err: Literal['__functoolsex__e__err'] = '__functoolsex__e__err'


def e_() -> F[EitherOk[V]]:
    return F(e_ok)


def e_ok(val: V) -> EitherOk[V]:
    return (__e_ok, val)


def e_err(val: V) -> EitherErr[V]:
    return (__e_err, val)


def e_is_err(e: Either[V, U]) -> TypeGuard[EitherErr[U]]:
    return e[0] == __e_err


def e_is_ok(e: Either[V, U]) -> TypeGuard[EitherOk[V]]:
    return e[0] == __e_ok


def e_filter(
    func: Callable[[V], bool],
    err: T,
) -> Callable[[Either[V, U]], Either[V, U] | EitherErr[T]]:
    def f(e: Either[V, U]) -> Either[V, U] | EitherErr[T]:
        if e[0] == __e_err:
            return e
        return e if func(e[1]) else (__e_err, err)

    return f


def e_map(func: Callable[[V], U]) -> Callable[[Either[V, U]], EitherOk[U] | Either[V, U]]:
    def f(e: Either[V, U]) -> EitherOk[U] | Either[V, U]:
        return (__e_ok, func(e[1])) if e[0] == __e_ok else e

    return f


def e_or_else(else_val: T) -> Callable[[Either[V, U]], EitherOk[T] | Either[V, U]]:
    def f(e: Either[V, U]) -> EitherOk[T] | Either[V, U]:
        return (__e_ok, else_val) if e[0] == __e_err else e

    return f


def e_or_call(func: Callable[[], T]) -> Callable[[Either[V, U]], EitherOk[T] | Either[V, U]]:
    def f(e: Either[V, U]) -> EitherOk[T] | Either[V, U]:
        return (__e_ok, func()) if e[0] == __e_err else e

    return f


def e_get_or(default: T) -> Callable[[Either[V, U]], T | V]:
    def f(e: Either[V, U]) -> T | V:
        return default if e[0] == __e_err else e[1]

    return f


def e_get_or_call(func: Callable[PS, T], *args: PS.args, **kwargs: PS.kwargs) -> Callable[[Either[V, U]], T | V]:
    def f(e: Either[V, U]) -> T | V:
        return func(*args, **kwargs) if e[0] == __e_err else e[1]

    return f


def test_log():
    """Print and return arg. Can be useful to debug. Can off it by env PY__FUNCTOOLSEX_LOG_OFF.
    Warn: log("It is: %s", LOGGER.info) return a function.
    >>> from operator import add, mul
    >>> (F(add, 1) >> log('add res: %s') >> P(mul, 3))(2)
    add res: 3
    9
    """


__log_is_on = 'PY__FUNCTOOLSEX_LOG_OFF' not in os.environ


def log(fmt: str, logger: Callable[[str], None] = print) -> Callable[[T], T]:
    if __log_is_on:
        return lambda obj: (obj, logger(fmt % (obj, )))[0]
    return identity
