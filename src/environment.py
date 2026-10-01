"""环境：变量名到值的绑定表，并支持指向外层环境的词法作用域链。"""

from __future__ import annotations

from datatypes import SchemeError


class Environment:
    """一层变量环境。"""

    def __init__(self, parent: "Environment | None" = None):
        self.bindings: dict[str, object] = {}
        self.parent = parent

    def define(self, name: str, value) -> None:
        self.bindings[name] = value

    def lookup(self, name: str):
        env: Environment | None = self
        while env is not None:
            if name in env.bindings:
                return env.bindings[name]
            env = env.parent
        raise SchemeError(f"未定义的符号：{name}")

    def make_child(self) -> "Environment":
        return Environment(self)


def standard_environment() -> Environment:
    """创建包含全部内建过程的全局环境。"""

    from builtin_library import BUILTINS

    env = Environment()
    for name, procedure in BUILTINS.items():
        env.define(name, procedure)
    return env
