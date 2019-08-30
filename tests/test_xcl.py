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


in_1 = 'name = "foo"'
out_1 = {"name": "foo"}

in_2 = "one = 1"
out_2 = {"one": 1}

in_3 = "pi = 3.14"
out_3 = {"pi": 3.14}

in_4 = "ls = [1 2 3]"
out_4 = {"ls": [1, 2, 3]}

in_5 = "ls = [1, 2, 3]"
out_5 = {"ls": [1, 2, 3]}

in_6 = "ls = [1, 2, 3,]"
out_6 = {"ls": [1, 2, 3]}

in_7 = "ls = [1 2, 3]"
out_7 = {"ls": [1, 2, 3]}

in_8 = "a = 3 b = 4"
out_8 = {"a": 3, "b": 4}

in_9 = "x.x = 3"
out_9 = {"x.x": 3}

in_10 = '"x|x" = 3'
out_10 = {"x|x": 3}

in_11 = "p = {x = 0 y = 3}"
out_11 = {"p": {"x": 0, "y": 3}}

in_12 = "p = [[1 2], [3 4] [5, 6]]"
out_12 = {"p": [[1, 2], [3, 4], [5, 6]]}

in_13 = "p = {tl = [1 2] br = [3 4]}"
out_13 = {"p": {"tl": [1, 2], "br": [3, 4]}}

# magic
ins = [v for k, v in locals().items() if k.startswith("in_")]
outs = [v for k, v in locals().items() if k.startswith("out_")]


@pytest.mark.parametrize("input,output", lex_tests.items())
def test_lexing(input, output):
    assert list(lex(input)) == [output]


@pytest.mark.parametrize("input,output", zip(ins, outs))
def test_parse(input, output):
    assert loads(input) == output
