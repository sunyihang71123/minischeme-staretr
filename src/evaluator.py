"""求值器：evaluate 与 apply 相互递归，是解释器的心脏。"""

from __future__ import annotations

from datatypes import (
    NIL,
    FALSE,
    TRUE,
    BuiltinProcedure,
    Pair,
    SchemeError,
    Symbol,
    UserProcedure,
    is_false,
    list_from_pair,
    make_list,
)
from environment import Environment


def _elements(pair) -> list[object]:
    return list_from_pair(pair)


def _is_pair(value) -> bool:
    return isinstance(value, Pair)


def _eval_sequence(expressions, env):
    """按 ``begin`` 语义求值一串表达式，返回最后一个结果。"""

    result = None
    for expr in expressions:
        result = evaluate(expr, env)
    return result


def evaluate(expr, env: Environment):
    if isinstance(expr, Symbol):
        return env.lookup(expr.name)
    if not isinstance(expr, Pair):
        return expr

    op = expr.car
    args = _elements(expr.cdr)

    if isinstance(op, Symbol):
        name = op.name
        if name == "quote":
            _check_arity(name, args, 1, 1)
            return args[0]
        if name == "if":
            _check_arity(name, args, 2, 3)
            test = evaluate(args[0], env)
            if not is_false(test):
                return evaluate(args[1], env)
            if len(args) == 3:
                return evaluate(args[2], env)
            return None
        if name == "cond":
            return _eval_cond(args, env)
        if name == "and":
            return _eval_and(args, env)
        if name == "or":
            return _eval_or(args, env)
        if name == "define":
            return _eval_define(args, env)
        if name == "lambda":
            return _eval_lambda(args, env)
        if name == "let":
            return _eval_let(args, env)
        if name == "begin":
            return _eval_sequence(args, env)

    proc = evaluate(op, env)
    values = [evaluate(arg, env) for arg in args]
    return apply(proc, values)


def apply(proc, args: list[object]):
    if isinstance(proc, BuiltinProcedure):
        return proc.function(args)
    if isinstance(proc, UserProcedure):
        if len(args) != len(proc.params):
            raise SchemeError(
                f"过程参数个数不匹配：期望 {len(proc.params)} 个，实际 {len(args)} 个"
            )
        child = proc.env.make_child()
        for param, value in zip(proc.params, args):
            child.define(param.name, value)
        return _eval_sequence(proc.body, child)
    raise SchemeError(f"无法调用非过程值：{proc!r}")


def _check_arity(name: str, args: list, minimum: int, maximum: int) -> None:
    if not (minimum <= len(args) <= maximum):
        raise SchemeError(f"{name} 参数个数错误：{len(args)}")


def _eval_cond(clauses, env):
    for clause in clauses:
        if not isinstance(clause, Pair):
            raise SchemeError("cond 子句必须是列表")
        clause_items = _elements(clause)
        if not clause_items:
            raise SchemeError("cond 子句不能为空")
        test_expr = clause_items[0]
        body = clause_items[1:]
        if isinstance(test_expr, Symbol) and test_expr.name == "else":
            return _eval_sequence(body, env)
        test = evaluate(test_expr, env)
        if not is_false(test):
            if body:
                return _eval_sequence(body, env)
            return test
    return None


def _eval_and(expressions, env):
    result = TRUE
    for expr in expressions:
        value = evaluate(expr, env)
        if is_false(value):
            return FALSE
        result = value
    return result


def _eval_or(expressions, env):
    for expr in expressions:
        value = evaluate(expr, env)
        if not is_false(value):
            return value
    return FALSE


def _eval_define(args, env):
    if not args:
        raise SchemeError("define 缺少名字")
    target = args[0]
    if isinstance(target, Symbol):
        _check_arity("define", args, 2, 2)
        value = evaluate(args[1], env)
        env.define(target.name, value)
        return target
    if isinstance(target, Pair):
        sig = _elements(target)
        if not sig or not isinstance(sig[0], Symbol):
            raise SchemeError("函数定义缺少函数名")
        name = sig[0]
        params = sig[1:]
        for param in params:
            if not isinstance(param, Symbol):
                raise SchemeError("函数参数必须是符号")
        body = args[1:]
        procedure = UserProcedure(params, body, env)
        env.define(name.name, procedure)
        return name
    raise SchemeError("define 目标必须是符号或函数签名")


def _eval_lambda(args, env):
    if len(args) < 2:
        raise SchemeError("lambda 需要参数列表与函数体")
    param_expr = args[0]
    params = _elements(param_expr)
    for param in params:
        if not isinstance(param, Symbol):
            raise SchemeError("lambda 参数必须是符号")
    return UserProcedure(params, args[1:], env)


def _eval_let(args, env):
    if len(args) < 2:
        raise SchemeError("let 需要绑定列表与函数体")
    binding_expr = args[0]
    bindings = _elements(binding_expr)
    names = []
    values = []
    for binding in bindings:
        if not isinstance(binding, Pair):
            raise SchemeError("let 绑定必须是 (名字 表达式)")
        pair = _elements(binding)
        if len(pair) != 2 or not isinstance(pair[0], Symbol):
            raise SchemeError("let 绑定必须是 (名字 表达式)")
        names.append(pair[0])
        # 所有绑定表达式都在外层环境求值，保证并行绑定。
        values.append(evaluate(pair[1], env))
    child = env.make_child()
    for name, value in zip(names, values):
        child.define(name.name, value)
    return _eval_sequence(args[1:], child)


def evaluate_program(expressions, env: Environment) -> list[object]:
    return [evaluate(expr, env) for expr in expressions]
