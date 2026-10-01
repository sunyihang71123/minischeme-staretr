"""mini-Scheme 运行时使用的数据类型。

这里刻意不复用 Python 的 ``bool``、``str`` 等类型作为值，因为 Python 中
``True == 1``、字符串与符号容易混淆等行为会破坏 ``eq?`` / ``equal?`` 的语义。
"""

from __future__ import annotations


class SchemeError(Exception):
    """解释器遇到无法继续执行的程序时抛出的异常。"""


class Symbol:
    """mini-Scheme 符号，例如 ``foo``、``+``、``x1``。"""

    __slots__ = ("name",)

    def __init__(self, name: str):
        self.name = name

    def __repr__(self) -> str:
        return f"Symbol({self.name!r})"

    def __str__(self) -> str:
        return self.name

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Symbol) and self.name == other.name

    def __hash__(self) -> int:
        return hash(("Symbol", self.name))


class SchemeString:
    """mini-Scheme 字符串。内部保存真实字符，打印时再转义。"""

    __slots__ = ("value",)

    def __init__(self, value: str):
        self.value = value

    def __repr__(self) -> str:
        return f"SchemeString({self.value!r})"

    def __eq__(self, other: object) -> bool:
        return isinstance(other, SchemeString) and self.value == other.value

    def __hash__(self) -> int:
        return hash(("SchemeString", self.value))


class SchemeBool:
    """mini-Scheme 布尔值。只有两个单例：``TRUE`` 与 ``FALSE``。"""

    __slots__ = ("value",)

    def __init__(self, value: bool):
        self.value = value

    def __repr__(self) -> str:
        return "#t" if self.value else "#f"

    def __str__(self) -> str:
        return "#t" if self.value else "#f"

    def __eq__(self, other: object) -> bool:
        return isinstance(other, SchemeBool) and self.value is other.value

    def __hash__(self) -> int:
        return hash(("SchemeBool", self.value))


TRUE = SchemeBool(True)
FALSE = SchemeBool(False)


class Pair:
    """点对，是列表与所有复合数据的底层表示。"""

    __slots__ = ("car", "cdr")

    def __init__(self, car, cdr):
        self.car = car
        self.cdr = cdr

    def __repr__(self) -> str:
        return f"Pair({self.car!r}, {self.cdr!r})"


class _Nil:
    """空表的唯一实例。"""

    __slots__ = ()

    def __repr__(self) -> str:
        return "()"

    def __str__(self) -> str:
        return "()"


NIL = _Nil()


class BuiltinProcedure:
    """由 Python 函数实现的 mini-Scheme 内建过程。"""

    __slots__ = ("name", "function")

    def __init__(self, name: str, function):
        self.name = name
        self.function = function

    def __repr__(self) -> str:
        return f"#<procedure:{self.name}>"


class UserProcedure:
    """由 ``lambda`` 创建的用户过程（闭包）。"""

    __slots__ = ("params", "body", "env")

    def __init__(self, params, body, env):
        self.params = params
        self.body = body
        self.env = env

    def __repr__(self) -> str:
        return "#<procedure>"


def is_false(value) -> bool:
    """mini-Scheme 中只有 ``#f`` 为假；``0``、``()``、``""`` 都为真。"""

    return value is FALSE


def is_number(value) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def list_from_pair(pair) -> list:
    """把正确的点对链转成 Python list；遇到点对或非列表则报错。"""

    result = []
    current = pair
    while isinstance(current, Pair):
        result.append(current.car)
        current = current.cdr
    if current is not NIL:
        raise SchemeError("期望一个列表，却遇到不正确的点对")
    return result


def make_list(values) -> object:
    """把 Python 可迭代对象中的值转成点对链。"""

    result = NIL
    for value in reversed(values):
        result = Pair(value, result)
    return result


def is_proper_list(value) -> bool:
    current = value
    while isinstance(current, Pair):
        current = current.cdr
    return current is NIL


def proper_list_length(value) -> int:
    current = value
    length = 0
    while isinstance(current, Pair):
        length += 1
        current = current.cdr
    if current is not NIL:
        raise SchemeError("length 需要真列表")
    return length
