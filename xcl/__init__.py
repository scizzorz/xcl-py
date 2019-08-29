__version__ = "0.1.0"

import string
from contextlib import contextmanager


class Peek:
    def __init__(self, it):
        self.it = it
        self.cur = next(it)
        self.finished = False

    def __iter__(self):
        return self

    def __next__(self):
        ret = self.cur
        try:
            self.cur = next(self.it)
        except StopIteration:
            if self.finished:
                raise
            else:
                self.finished = True
                self.cur = StopIteration
        return ret

    @staticmethod
    def check(thing, what):
        return isinstance(thing, what)

    def done(self):
        return self.cur is StopIteration

    def __bool__(self):
        return not self.done()

    def expect(self, *what):
        check = next(self)
        if not self.check(check, what):
            if len(what) > 1:
                choices = ", ".join(x.__name__ for x in what)
                raise Exception(f"Expected any of {choices}; found {self.cur!r}")
            raise Exception(f"Expected {what[0]}; found {self.cur!r}")

        return check

    def has(self, *what):
        return self.cur if self.check(self.cur, what) else None

    def maybe(self, *what):
        check = self.has(*what)
        if check:
            next(self)

        return check

    @contextmanager
    def wrap(self, left, right):
        self.expect(left)
        yield
        self.expect(right)


class CharPeek(Peek):
    @staticmethod
    def check(thing, what):
        return thing in what


class Token:
    def __init__(self, val=None):
        self.val = val

    def __eq__(self, other):
        return (self.__class__ is other.__class__) and (self.val == other.val)

    def __str__(self):
        if self.val is not None:
            return str(self.val)

        return self.__class__.__name__

    def __repr__(self):
        if self.val is not None:
            return f"<{self.__class__.__name__} {self.val!r}>"

        return f"<{self.__class__.__name__}>"


class Id(Token):
    pass


class Boolean(Token):
    def __init__(self, val=None):
        if isinstance(val, str):
            self.val = val.lower() == "true"
        else:
            self.val = bool(val)


class Null(Token):
    def __init__(self, val=None):
        self.val = None


class Int(Token):
    def __init__(self, val=None):
        self.val = int(val)


class Float(Token):
    def __init__(self, val=None):
        self.val = float(val)


class Str(Token):
    pass


class Cul(Token):
    pass


class Cur(Token):
    pass


class Sql(Token):
    pass


class Sqr(Token):
    pass


class Com(Token):
    pass


class Eq(Token):
    pass


KEYWORD_MAP = {"true": Boolean, "false": Boolean, "null": Null}
STR_ESCAPES = {"n": "\n", "r": "\r", "t": "\t", '"': '"', "'": "'"}

VALID_ID_START = string.ascii_letters + "_-*?+."
VALID_ID = VALID_ID_START + string.digits + "|"
VALID_NUM_START = "123456789"
VALID_NUM = string.digits + "."
SKIP = string.whitespace


def lex(text):
    chars = CharPeek(iter(text))

    while not chars.done():
        if chars.has(*VALID_ID_START):
            yield lex_id(chars)
            continue

        if chars.has(*VALID_NUM_START):
            yield lex_num(chars)
            continue

        if chars.maybe("0"):
            if chars.maybe("."):
                yield lex_num(chars, start="0.")
            else:
                yield Int(0)
            continue

        if chars.has('"'):
            yield lex_str(chars)
            continue

        if chars.maybe("|"):
            if chars.has('"'):
                yield lex_str(chars, dedent=True)
                continue
            else:
                raise Exception(f"Unexpected character sequence: |{chars.cur}")

        if chars.has("["):
            yield Sql()

        if chars.has("]"):
            yield Sqr()

        if chars.has("{"):
            yield Cul()

        if chars.has("}"):
            yield Cur()

        if chars.has(","):
            yield Com()

        if chars.has("="):
            yield Eq()

        try:
            next(chars)
        except StopIteration:
            break


def lex_id(chars):
    build = []
    while not chars.done() and chars.has(*VALID_ID):
        build.append(next(chars))

    id = "".join(build)
    return KEYWORD_MAP.get(id, Id)(id)


def lex_num(chars, start=""):
    build = list(start)
    while not chars.done() and chars.has(*VALID_NUM):
        build.append(next(chars))

    token = Float if "." in build else Int
    return token("".join(build))


def lex_str(chars, dedent=False):
    build = []
    start = next(chars)
    while not chars.done():
        if chars.maybe(start):
            break

        if chars.maybe("\\"):
            if chars.has(*STR_ESCAPES):
                build.append(STR_ESCAPES[next(chars)])
            else:
                raise Exception(f"Invalid string escape sequence: \\{chars.cur}")

        else:
            build.append(next(chars))

    result = "".join(build)
    if dedent:
        lines = result.split("\n")
        while len(lines) > 0 and lines[0].strip() == "":
            lines = lines[1:]

        indent_chars = len(lines[0]) - len(lines[0].lstrip(" \t"))
        indent = lines[0][:indent_chars]
        for line in lines:
            if len(line.strip()) > 0 and not line.startswith(indent):
                raise Exception("Indent mismatch in indented string")

        lines = [line[indent_chars:] for line in lines]
        result = "\n".join(lines)

    return Str(result)


def parse(tokens):
    into = {}

    tokens = Peek(iter(tokens))
    while not tokens.done():
        key, val = parse_assn(tokens)
        into[key] = val

    return into


def parse_assn(tokens):
    key = tokens.expect(Id, Str).val
    tokens.expect(Eq)
    val = parse_val(tokens)
    return key, val


def parse_val(tokens):
    if tokens.has(Cul):
        val = parse_dict(tokens)

    elif tokens.has(Sql):
        val = parse_list(tokens)

    elif tokens.has(Boolean, Null, Int, Float, Str):
        val = next(tokens).val

    else:
        raise Exception(
            f"Expected one of Boolean, Null, Int, Float, Str, Cul, or Sql; found {tokens.cur!r}"
        )

    return val


def parse_dict(tokens):
    with tokens.wrap(Cul, Cur):
        into = {}
        while not tokens.has(Cur):
            key, val = parse_assn(tokens)
            into[key] = val

    return into


def parse_list(tokens):
    with tokens.wrap(Sql, Sqr):
        into = []
        while not tokens.has(Sqr):
            val = parse_val(tokens)
            into.append(val)
            tokens.maybe(Com)

    return into


def loads(s):
    return parse(lex(s))
