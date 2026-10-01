"""词法分析：把程序文本拆成 token 列表。"""

from __future__ import annotations

from datatypes import FALSE, TRUE, SchemeError, SchemeString, Symbol


def _is_delimiter(ch: str) -> bool:
    return ch.isspace() or ch in "()'\""


def _parse_string(text: str, start: int) -> tuple[SchemeString, int]:
    """从 ``start`` 处（已经跳过开头的双引号）读取字符串。"""

    chars: list[str] = []
    i = start
    while i < len(text):
        ch = text[i]
        if ch == '"':
            return SchemeString("".join(chars)), i + 1
        if ch == "\\":
            if i + 1 >= len(text):
                raise SchemeError("字符串末尾出现不完整的转义")
            nxt = text[i + 1]
            escapes = {"n": "\n", "t": "\t", '"': '"', "\\": "\\"}
            if nxt not in escapes:
                raise SchemeError(f"不支持的转义：\\{nxt}")
            chars.append(escapes[nxt])
            i += 2
            continue
        chars.append(ch)
        i += 1
    raise SchemeError("字符串没有闭合的引号")


def tokenize(text: str) -> list[tuple[str, object]]:
    """把完整程序文本转换为 token 流。

    每个 token 是 ``(kind, value)``，其中 kind 为
    ``lparen``、``rparen``、``quote`` 或 ``atom``。
    """

    tokens: list[tuple[str, object]] = []
    i = 0
    n = len(text)
    while i < n:
        ch = text[i]
        if ch.isspace():
            i += 1
            continue
        if ch == ";":
            while i < n and text[i] != "\n":
                i += 1
            continue
        if ch == "(":
            tokens.append(("lparen", None))
            i += 1
            continue
        if ch == ")":
            tokens.append(("rparen", None))
            i += 1
            continue
        if ch == "'":
            tokens.append(("quote", None))
            i += 1
            continue
        if ch == '"':
            string, i = _parse_string(text, i + 1)
            tokens.append(("atom", string))
            continue

        start = i
        while i < n and not _is_delimiter(text[i]):
            i += 1
        word = text[start:i]
        if word == "#t":
            tokens.append(("atom", TRUE))
        elif word == "#f":
            tokens.append(("atom", FALSE))
        elif _looks_like_number(word):
            tokens.append(("atom", _parse_number(word)))
        else:
            tokens.append(("atom", Symbol(word)))
    return tokens


def _looks_like_number(word: str) -> bool:
    if not word:
        return False
    candidate = word[1:] if word[0] in "+-" else word
    if candidate == "":
        return False
    if "." in candidate:
        parts = candidate.split(".")
        if len(parts) != 2:
            return False
        left, right = parts
        return (left.isdigit() or left == "") and (right.isdigit() or right == "") and (left or right)
    return candidate.isdigit()


def _parse_number(word: str):
    if "." in word:
        return float(word)
    return int(word)
