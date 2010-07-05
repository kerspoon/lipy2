
import re
import string
from datatypes import nil, true, false, mksym, cons, from_list, LispString, LispInteger

class iterator_undo(object):   # undo-able iterator wrapper
    def __init__(self, iterable):
        super(iterator_undo, self).__init__()
        self.iterator = iter(iterable)
        self.stack = []

    def __iter__(self):
        return self

    def next(self):
        if self.stack:
            # print "next: stack", self.stack
            return self.stack.pop()
        return self.iterator.next()  # Raises StopIteration eventually

    def undo(self, item):
        # print "undo:", item 
        self.stack.append(item)

    def peek(self):
        item = self.next()
        self.undo(item)
        return item

    def skip(self, num=1):
        for i in range(num):
            x = self.next()

def test_iterator_undo():
    it = iterator_undo([1,2,3,4,5])
    assert list(it) == [1,2,3,4,5]
    it = iterator_undo([1,2,3,4,5])
    assert 1 == it.next()
    assert it.next() == 2
    assert it.peek() == 3
    assert it.peek() == 3
    assert it.next() == 3
    assert it.next() == 4
    assert it.next() == 5
    
test_iterator_undo()

# -----------------------------------------------------------------------------

re_num = re.compile(r"^[-+]?\d+$")
normalchars = set(string.ascii_letters + string.digits + "-_<>%=!^&?*+/")

def isnumber(str):
    return re_num.match(str) != None

def test_isnumber():
    print "testing: isnumber"
    assert isnumber("0")
    assert isnumber("1")
    assert isnumber("10")
    assert isnumber("0001")
    assert isnumber("01234567890")
    assert isnumber("+0")
    assert isnumber("+1")
    assert isnumber("+10")
    assert isnumber("+0001")
    assert isnumber("+01234567890")
    assert isnumber("-0")
    assert isnumber("-1")
    assert isnumber("-10")
    assert isnumber("-0001")
    assert isnumber("-01234567890")
    assert not isnumber("")
    assert not isnumber("--1")
    assert not isnumber("_5")
    assert not isnumber("asdf")
    assert not isnumber("5a")
    assert not isnumber("a5")
    assert not isnumber("5a5")
    assert not isnumber("a5a")
    assert not isnumber("+a1")
    assert not isnumber("+9a")
    assert not isnumber("-9a")
    assert not isnumber("-a3")
    assert not isnumber("-10+")
test_isnumber()

# -----------------------------------------------------------------------------

quote = mksym("quote")


def valid_symbol_name(text):
    return set(text).issubset(normalchars)

def inner_parse(tokens):
    """take the token list from the lexer and make it into an object"""

    tok = tokens.next()

    assert len(tok) != 0, "zero sized token"
    assert tok != ".", "found '.' outside of pair"
    assert tok != ")", "found ')' mismatched bracket"

    if tok == "'":
        return from_list([quote, inner_parse(tokens), nil])
    elif tok[0] == '"':
        return LispString(tok[1:-1])
    elif tok == "(":
        tok = tokens.next()

        if tok == ")": return nil

        tokens.undo(tok)
        tok_list = [inner_parse(tokens)]
        while (tokens.peek() not in [")", "."]):
            tok_list.append(inner_parse(tokens))
        
        tok = tokens.next()
        if tok == ".":
            tok_list.append(inner_parse(tokens))
            assert tokens.next() == ")", "expected one sexp after a fullstop"
        else:
            tok_list.append(nil)
            assert tok == ")", "missing close bracket of pair"

        return from_list(tok_list)
    elif isnumber(tok):
        return LispInteger(int(tok))
    else:
        # we have a symbol 
        assert valid_symbol_name(tok), "invalid atom in symbol '%s'" % tok
        return mksym(tok)

def kill_comments(iterable):
    for x in iterable:
        if x[0] != ";":
            yield x

def parse(tokens):
    tokens = iterator_undo(kill_comments(tokens))
    while (True):
        yield inner_parse(tokens)

def test():
    print "testing: parse"
    from lex import tokenize

    to_process = [ 
        ("()"        , "nil"),
        ("'()"       , "( quote nil )"),
        ("'a"        , "( quote a )"),
        ("'( a b)"   , "( quote ( a b ) )"),
        ("()"        , "nil"),
        ("(a)"       , "( a )"),
        ("('a)"      , "( ( quote a ) )"),
        ("(a b)"     , "( a b )"),
        ("(a b c)"   , "( a b c )"),
        ("(a b c d e f (g) h (i j) k (l m n) o (p q (r s) t) u (v (w (x (y (z))))))", 
         "( a b c d e f ( g ) h ( i j ) k ( l m n ) o ( p q ( r s ) t ) u ( v ( w ( x ( y ( z ) ) ) ) ) )"),
        ("(a . b)"   , "( a . b )"),
        ("(a b . c)" , "( a b . c )"),
        ('"asdf"'    , '"asdf"'), 
        ('("asdf")'    , '( "asdf" )'), 
        ('(4"asdf")'   , '( 4 "asdf" )'), 
        ('(4."asdf")'   , '( 4 . "asdf" )'), 
        ('"as df"'    , '"as df"'), 
        ('as ;'    , 'as'), 
        ('as ;abcdef12345'    , 'as'), 
        ('(as ";")'    , '( as ";" )'), 
        ('(as "; hello")'    , '( as "; hello" )'), 
        ('as ;;;;;;'    , 'as'), 
        ('as ; !" %$ 86842 "$^P~>?:@:~'    , 'as'), 
        ("(() (()()))", "( nil ( nil nil ) )")]
    
    for test, expected in to_process:

        tokens = tokenize([test])
        result = list(parse(tokens))
        assert len(result) == 1
        res = str(result[0])
        if res != expected:
            print "Mismatch"
            print "test    :", test
            print "result  :", res
            print "expected:", expected


test()

