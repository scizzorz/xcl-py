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
    "true": Boolean(True),
    "false": Boolean(False),
    "null": Null(),
    "0": Int(0),
    "0.": Float(0),
    "0.1": Float(0.1),
    "3": Int(3),
    "3.14": Float(3.14),
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
