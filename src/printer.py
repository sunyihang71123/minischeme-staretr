"""打印：把 mini-Scheme 值转成符合规范 §8 的文本。"""

from __future__ import annotations

from datatypes import NIL, BuiltinProcedure, Pair, SchemeBool, SchemeString, Symbol, UserProcedure, is_number


def _escape_string(value: str) -> str:
    result = []
    for ch in value:
        if ch == "\\":
            result.append("\\\\")
        elif ch == '"':
            result.append('\\"')
        elif ch == "\n":
            result.append("\\n")
        elif ch == "\t":
            result.append("\\t")
        else:
            result.append(ch)
    return "".join(result)


def value_to_string(value, *, display: bool = False) -> str:
    """把值转成普通打印文本；``display=True`` 时字符串不带引号。"""

    if value is NIL:
        return "()"
    if isinstance(value, Symbol):
        return value.name
    if isinstance(value, SchemeString):
        if display:
            return value.value
        return '"' + _escape_string(value.value) + '"'
    if isinstance(value, SchemeBool):
        return "#t" if value.value else "#f"
    if is_number(value):
        return str(value)
    if isinstance(value, Pair):
        return _pair_to_string(value, display=display)
    if isinstance(value, (BuiltinProcedure, UserProcedure)):
        return "#<procedure>"
    raise TypeError(f"无法打印的值：{value!r}")


def _pair_to_string(pair: Pair, *, display: bool) -> str:
    parts = []
    current = pair
    while isinstance(current, Pair):
        parts.append(value_to_string(current.car, display=display))
        current = current.cdr
    if current is NIL:
        return "(" + " ".join(parts) + ")"
    return "(" + " ".join(parts) + " . " + value_to_string(current, display=display) + ")"


def display_value(value) -> str:
    """``display`` 使用的表示：字符串递归地去引号。"""

    if isinstance(value, Pair):
        return _pair_to_string(value, display=True)
    return value_to_string(value, display=True)
