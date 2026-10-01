"""mini-Scheme 解释器入口。

运行方式：
    python src/main.py [file1.scm ...]
没有文件参数时从标准输入读取程序。
"""

from __future__ import annotations

import sys

from datatypes import SchemeError
from environment import standard_environment
from evaluator import evaluate
from lexer import tokenize
from parser import parse
from printer import value_to_string


def run_text(text: str, env) -> None:
    expressions = parse(tokenize(text))
    for expr in expressions:
        result = evaluate(expr, env)
        if result is not None:
            print(value_to_string(result))


def main(argv: list[str]) -> int:
    env = standard_environment()
    try:
        if not argv:
            text = sys.stdin.read()
            run_text(text, env)
            return 0
        for path in argv:
            with open(path, "r", encoding="utf-8") as handle:
                run_text(handle.read(), env)
        return 0
    except (SchemeError, TypeError, ValueError, ZeroDivisionError, FileNotFoundError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
