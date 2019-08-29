__version__ = '0.1.0'

import string


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


class Token:
  def __init__(self, val=None):
    self.val = val

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
    self.val = (val.lower() == 'true')


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


KEYWORD_MAP = {
  'true': Boolean,
  'false': Boolean,
  'null': Null,
}
STR_ESCAPES = {
  'n': '\n',
  'r': '\r',
  't': '\t',
  '"': '"',
  "'": "'",
}

VALID_ID_START = string.ascii_letters + '_'
VALID_ID = VALID_ID_START + string.digits
VALID_NUM_START = '123456789'
VALID_NUM = string.digits + '.'
SKIP = string.whitespace


def lex(text):
  chars = Peek(iter(text))

  while True:
    if chars.cur is StopIteration:
      break

    if chars.cur in VALID_ID_START:
      yield lex_id(chars)
      continue

    if chars.cur in VALID_NUM_START:
      yield lex_num(chars)
      continue

    if chars.cur == '"':
      yield lex_str(chars)
      continue

    if chars.cur == '[':
      yield Sql()

    if chars.cur == ']':
      yield Sqr()

    if chars.cur == '{':
      yield Cul()

    if chars.cur == '}':
      yield Cur()

    if chars.cur == ',':
      yield Com()

    try:
      next(chars)
    except StopIteration:
      break


def lex_id(chars):
  build = []
  while chars.cur is not StopIteration and chars.cur in VALID_ID:
    build.append(chars.cur)
    next(chars)

  id = ''.join(build)
  return KEYWORD_MAP.get(id, Id)(id)


def lex_num(chars):
  build = []
  token = Int
  while chars.cur is not StopIteration and chars.cur in VALID_NUM:
    if chars.cur == '.':
      token = Float

    build.append(chars.cur)
    next(chars)

  return token(''.join(build))


def lex_str(chars):
  build = []
  start = next(chars)
  while chars.cur is not StopIteration:
    if chars.cur == start:
      next(chars)
      break

    if chars.cur == '\\':
      next(chars)
      if chars.cur in STR_ESCAPES:
        build.append(STR_ESCAPES[chars.cur])
      else:
        raise Exception(f"Invalid string escape sequence: \\{chars.cur}")

    else:
      build.append(chars.cur)

    next(chars)

  return Str(''.join(build))


inp = r'''foobar true null false { } [ ] , 1 2.3 "hello world" "\"wow
world\""'''
for tok in lex(inp):
  print(repr(tok))
