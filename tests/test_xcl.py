import pytest
from xcl import (
    __version__,
    Id,
    Boolean,
    Null,
    Int,
    Float,
    Str,
    Cul,
    Cur,
    Sql,
    Sqr,
    Com,
    Eq,
    lex,
    parse,
    loads,
)


def test_version():
    assert __version__ == "0.1.0"


lex_tests = {
    "hello": Id("hello"),
    '"hello"': Str("hello"),
    '|"hello"': Str("hello"),
    r'"hello\nworld"': Str("hello\nworld"),
    r'"hello\tworld"': Str("hello\tworld"),
    r'"hello\rworld"': Str("hello\rworld"),
    r"true": Boolean(True),
    r"false": Boolean(False),
    r"null": Null(),
    r"3": Int(3),
    r"3.14": Float(3.14),
    "=": Eq(),
    "[": Sql(),
    "]": Sqr(),
    "{": Cul(),
    "}": Cur(),
    ",": Com(),
}


@pytest.mark.parametrize("input,output", lex_tests.items())
def test_lexing(input, output):
    assert list(lex(input)) == [output]
