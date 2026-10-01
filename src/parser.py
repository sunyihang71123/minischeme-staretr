"""语法分析：把 token 流转成嵌套的 mini-Scheme 表达式。"""

from __future__ import annotations

from datatypes import NIL, Pair, SchemeError, Symbol, make_list


class Parser:
    def __init__(self, tokens: list[tuple[str, object]]):
        self.tokens = tokens
        self.pos = 0

    def parse_all(self) -> list[object]:
        expressions = []
        while self.pos < len(self.tokens):
            expressions.append(self.parse_expr())
        return expressions

    def parse_expr(self):
        if self.pos >= len(self.tokens):
            raise SchemeError("程序在表达式中间结束")
        kind, value = self.tokens[self.pos]
        self.pos += 1
        if kind == "atom":
            return value
        if kind == "quote":
            datum = self.parse_expr()
            return make_list([Symbol("quote"), datum])
        if kind == "lparen":
            items = []
            while True:
                if self.pos >= len(self.tokens):
                    raise SchemeError("缺少右括号")
                if self.tokens[self.pos][0] == "rparen":
                    self.pos += 1
                    break
                items.append(self.parse_expr())
            return make_list(items)
        raise SchemeError(f"无法解析的 token：{kind}")


def parse(tokens: list[tuple[str, object]]) -> list[object]:
    return Parser(tokens).parse_all()


def parse_program(text: str) -> list[object]:
    from lexer import tokenize

    return parse(tokenize(text))
