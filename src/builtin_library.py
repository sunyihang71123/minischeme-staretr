"""mini-Scheme 内建过程库，对应 spec §5。

模块名刻意避免与 Python 自带的 ``builtins`` 模块重名。
"""

from __future__ import annotations

from datatypes import (
    NIL,
    FALSE,
    TRUE,
    BuiltinProcedure,
    Pair,
    SchemeBool,
    SchemeError,
    SchemeString,
    Symbol,
    UserProcedure,
    is_false,
    is_number,
    is_proper_list,
    make_list,
    proper_list_length,
)
from printer import display_value, value_to_string


def _arity(name: str, args: list, minimum: int, maximum: int | None = None) -> None:
    maximum = minimum if maximum is None else maximum
    if not (minimum <= len(args) <= maximum):
        raise SchemeError(f"{name} 参数个数错误：{len(args)}")


def _number(name: str, value):
    if not is_number(value):
        raise SchemeError(f"{name} 需要数字")
    return value


def _all_numbers(name: str, args: list):
    return [_number(name, arg) for arg in args]


def _integer(name: str, value):
    value = _number(name, value)
    if isinstance(value, float) and not value.is_integer():
        raise SchemeError(f"{name} 需要整数")
    return value


def _add(args):
    return sum(_all_numbers("+", args), 0)


def _subtract(args):
    numbers = _all_numbers("-", args)
    if not numbers:
        raise SchemeError("- 至少需要一个参数")
    if len(numbers) == 1:
        return -numbers[0]
    result = numbers[0]
    for value in numbers[1:]:
        result -= value
    return result


def _multiply(args):
    result = 1
    for value in _all_numbers("*", args):
        result *= value
    return result


def _divide(args):
    numbers = _all_numbers("/", args)
    if not numbers:
        raise SchemeError("/ 至少需要一个参数")
    if len(numbers) == 1:
        if numbers[0] == 0:
            raise SchemeError("除数不能为零")
        return 1 / numbers[0]
    result = numbers[0]
    for value in numbers[1:]:
        if value == 0:
            raise SchemeError("除数不能为零")
        if isinstance(result, int) and isinstance(value, int):
            result = int(result / value)  # 负数商向零截断
        else:
            result = result / value
    return result


def _modulo(args):
    _arity("modulo", args, 2)
    left = _integer("modulo", args[0])
    right = _integer("modulo", args[1])
    if right == 0:
        raise SchemeError("modulo 的除数不能为零")
    return left % right


def _quotient(args):
    _arity("quotient", args, 2)
    left = _integer("quotient", args[0])
    right = _integer("quotient", args[1])
    if right == 0:
        raise SchemeError("quotient 的除数不能为零")
    return int(left / right)


def _expt(args):
    _arity("expt", args, 2)
    base = _number("expt", args[0])
    power = _number("expt", args[1])
    return base**power


def _abs(args):
    _arity("abs", args, 1)
    return abs(_number("abs", args[0]))


def _comparison(name: str, args: list, compare):
    if len(args) < 2:
        raise SchemeError(f"{name} 至少需要两个参数")
    for left, right in zip(args, args[1:]):
        if not compare(left, right):
            return FALSE
    return TRUE


def _eq_numeric_or_symbolic(left, right):
    if is_number(left) and is_number(right):
        return left == right
    if isinstance(left, Symbol) and isinstance(right, Symbol):
        return left.name == right.name
    raise SchemeError("比较操作支持数字与符号")


def _symbolic_or_numeric_order(left, right):
    if is_number(left) and is_number(right):
        return left, right
    if isinstance(left, Symbol) and isinstance(right, Symbol):
        return left.name, right.name
    raise SchemeError("比较操作支持数字与符号")


def _make_comparison(name, predicate):
    def builtin(args):
        def compare(left, right):
            a, b = _symbolic_or_numeric_order(left, right)
            return predicate(a, b)

        return _comparison(name, args, compare)

    return builtin


def _not(args):
    _arity("not", args, 1)
    return FALSE if not is_false(args[0]) else TRUE


def _cons(args):
    _arity("cons", args, 2)
    return Pair(args[0], args[1])


def _car(args):
    _arity("car", args, 1)
    if not isinstance(args[0], Pair):
        raise SchemeError("car 需要点对")
    return args[0].car


def _cdr(args):
    _arity("cdr", args, 1)
    if not isinstance(args[0], Pair):
        raise SchemeError("cdr 需要点对")
    return args[0].cdr


def _list(args):
    return make_list(args)


def _length(args):
    _arity("length", args, 1)
    return proper_list_length(args[0])


def _append(args):
    if not args:
        return NIL
    for arg in args[:-1]:
        if not is_proper_list(arg):
            raise SchemeError("append 需要真列表")
    if not is_proper_list(args[-1]):
        raise SchemeError("append 需要真列表")
    if len(args) == 1:
        return _copy_list(args[0])
    result = _copy_list(args[0])
    tail = result
    if tail is NIL:
        result = NIL
        for arg in args[1:]:
            copied = _copy_list(arg)
            result = _concat_lists(result, copied)
        return result
    while isinstance(tail, Pair) and isinstance(tail.cdr, Pair):
        tail = tail.cdr
    for arg in args[1:-1]:
        tail.cdr = _copy_list(arg)
        while isinstance(tail.cdr, Pair):
            tail = tail.cdr
    tail.cdr = args[-1]
    return result


def _copy_list(value):
    if value is NIL:
        return NIL
    result = Pair(value.car, NIL)
    tail = result
    current = value.cdr
    while isinstance(current, Pair):
        tail.cdr = Pair(current.car, NIL)
        tail = tail.cdr
        current = current.cdr
    tail.cdr = current
    return result


def _concat_lists(left, right):
    if left is NIL:
        return right
    current = left
    while isinstance(current.cdr, Pair):
        current = current.cdr
    current.cdr = right
    return left


def _null(args):
    _arity("null?", args, 1)
    return TRUE if args[0] is NIL else FALSE


def _pair(args):
    _arity("pair?", args, 1)
    return TRUE if isinstance(args[0], Pair) else FALSE


def _list_predicate(args):
    _arity("list?", args, 1)
    return TRUE if is_proper_list(args[0]) else FALSE


def _number_predicate(args):
    _arity("number?", args, 1)
    return TRUE if is_number(args[0]) else FALSE


def _boolean_predicate(args):
    _arity("boolean?", args, 1)
    return TRUE if isinstance(args[0], SchemeBool) else FALSE


def _symbol_predicate(args):
    _arity("symbol?", args, 1)
    return TRUE if isinstance(args[0], Symbol) else FALSE


def _string_predicate(args):
    _arity("string?", args, 1)
    return TRUE if isinstance(args[0], SchemeString) else FALSE


def _procedure_predicate(args):
    _arity("procedure?", args, 1)
    return TRUE if isinstance(args[0], (BuiltinProcedure, UserProcedure)) else FALSE


def _zero(args):
    _arity("zero?", args, 1)
    value = _number("zero?", args[0])
    return TRUE if value == 0 else FALSE


def _even(args):
    _arity("even?", args, 1)
    value = _integer("even?", args[0])
    return TRUE if int(value) % 2 == 0 else FALSE


def _odd(args):
    _arity("odd?", args, 1)
    value = _integer("odd?", args[0])
    return TRUE if int(value) % 2 != 0 else FALSE


def _eq(args):
    _arity("eq?", args, 2)
    left, right = args
    if _is_atomic(left) or _is_atomic(right):
        return TRUE if _atomic_equal(left, right) else FALSE
    return TRUE if left is right else FALSE


def _is_atomic(value) -> bool:
    return is_number(value) or isinstance(value, (SchemeBool, Symbol, SchemeString))


def _atomic_equal(left, right) -> bool:
    if is_number(left) and is_number(right):
        return left == right
    if isinstance(left, SchemeBool) and isinstance(right, SchemeBool):
        return left is right
    if isinstance(left, Symbol) and isinstance(right, Symbol):
        return left.name == right.name
    if isinstance(left, SchemeString) and isinstance(right, SchemeString):
        return left.value == right.value
    return False


def _equal(args):
    _arity("equal?", args, 2)
    return TRUE if _structurally_equal(args[0], args[1], set()) else FALSE


def _structurally_equal(left, right, seen) -> bool:
    if left is right:
        return True
    if is_number(left) and is_number(right):
        return left == right
    if isinstance(left, SchemeBool) and isinstance(right, SchemeBool):
        return left is right
    if isinstance(left, Symbol) and isinstance(right, Symbol):
        return left.name == right.name
    if isinstance(left, SchemeString) and isinstance(right, SchemeString):
        return left.value == right.value
    if isinstance(left, Pair) and isinstance(right, Pair):
        marker = (id(left), id(right))
        if marker in seen:
            return True
        seen.add(marker)
        return _structurally_equal(left.car, right.car, seen) and _structurally_equal(
            left.cdr, right.cdr, seen
        )
    return False


def _display(args):
    _arity("display", args, 1)
    import sys

    sys.stdout.write(display_value(args[0]))
    return None


def _newline(args):
    _arity("newline", args, 0)
    import sys

    sys.stdout.write("\n")
    return None


BUILTINS = {
    "+": BuiltinProcedure("+", _add),
    "-": BuiltinProcedure("-", _subtract),
    "*": BuiltinProcedure("*", _multiply),
    "/": BuiltinProcedure("/", _divide),
    "modulo": BuiltinProcedure("modulo", _modulo),
    "quotient": BuiltinProcedure("quotient", _quotient),
    "expt": BuiltinProcedure("expt", _expt),
    "abs": BuiltinProcedure("abs", _abs),
    "=": BuiltinProcedure("=", _make_comparison("=", lambda a, b: a == b)),
    "<": BuiltinProcedure("<", _make_comparison("<", lambda a, b: a < b)),
    ">": BuiltinProcedure(">", _make_comparison(">", lambda a, b: a > b)),
    "<=": BuiltinProcedure("<=", _make_comparison("<=", lambda a, b: a <= b)),
    ">=": BuiltinProcedure(">=", _make_comparison(">=", lambda a, b: a >= b)),
    "not": BuiltinProcedure("not", _not),
    "cons": BuiltinProcedure("cons", _cons),
    "car": BuiltinProcedure("car", _car),
    "cdr": BuiltinProcedure("cdr", _cdr),
    "list": BuiltinProcedure("list", _list),
    "length": BuiltinProcedure("length", _length),
    "append": BuiltinProcedure("append", _append),
    "null?": BuiltinProcedure("null?", _null),
    "pair?": BuiltinProcedure("pair?", _pair),
    "list?": BuiltinProcedure("list?", _list_predicate),
    "number?": BuiltinProcedure("number?", _number_predicate),
    "boolean?": BuiltinProcedure("boolean?", _boolean_predicate),
    "symbol?": BuiltinProcedure("symbol?", _symbol_predicate),
    "string?": BuiltinProcedure("string?", _string_predicate),
    "procedure?": BuiltinProcedure("procedure?", _procedure_predicate),
    "zero?": BuiltinProcedure("zero?", _zero),
    "even?": BuiltinProcedure("even?", _even),
    "odd?": BuiltinProcedure("odd?", _odd),
    "eq?": BuiltinProcedure("eq?", _eq),
    "equal?": BuiltinProcedure("equal?", _equal),
    "display": BuiltinProcedure("display", _display),
    "newline": BuiltinProcedure("newline", _newline),
}
