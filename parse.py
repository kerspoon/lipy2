
import re
import string  

# todo make sure it only accepts valid chars

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

def inner_parse(tokens):
    """take the token list from the lexer and make it into an object"""

    tok = tokens.next()
    # print "inner_parse:", tok

    assert len(tok) != 0, "zero sized token"
    assert tok != ".", "found '.' outside of pair"
    assert tok != ")", "found ')' mismatched bracket"

    if tok == "'":
        return ["quote", [inner_parse(tokens), "nil"]]
    elif tok == "(":
        tok = tokens.next()

        if tok == ")":
            return "nil"

        tokens.undo(tok)
        sexp = [inner_parse(tokens), "nil"]
        full_sexp = sexp

        while (tokens.peek() not in [")", "."]):
            sexp[1] = [inner_parse(tokens),"nil"]
            sexp = sexp[1]
        
        tok = tokens.next()
        if tok == ".":
            sexp[1] = inner_parse(tokens)
            assert tokens.next() == ")", "expected one sexp after a fullstop"
        else:
            assert tok == ")", "missing close bracket of pair"
        return full_sexp
    else:
        # we have a symbol or number
        # print "symbol:", tok, tokens.peek()
        if isinstance(tok,str):
            if isnumber(tok):
                return int(tok)
            assert set(tok).issubset(normalchars), "invalid atom in symbol"
            return tok
        raise Exception("can't happen")

def parse(tokens):
    tokens = iterator_undo(tokens)
    while (True):
        yield inner_parse(tokens)

def sexp_str(sexp):
    text = ""
    if isinstance(sexp,list):
        text += "( "
        while (isinstance(sexp,list)):
            assert(len(sexp)==2), "lists (cons pairs) must only have 2 elements"
            text += sexp_str(sexp[0]) + " "
            sexp = sexp[1]
        assert isinstance(sexp,(str,int)), "must be str, int or list"
        assert isinstance(sexp,int) or len(sexp) != 0, "zero sized token"

        if sexp != "nil":
            text += ". " + sexp_str(sexp) + " "
        text += ")"
    elif isinstance(sexp,str):
        assert set(sexp).issubset(normalchars), "invalid atom in symbol" + sexp
        text += sexp
    elif isinstance(sexp,int):
        text += str(sexp)
    else:
        print type(sexp), str(sexp)
        raise Exception("must be str, int or list")
    return text 

def test():
    from lex import tokenize

    to_process = [ ("()"        , "nil"),
                   ("'()", None),
                   ("'a", None),
                   ("'( a b)", None),
                   ("()", None),
                   ("(a)", None),
                   ("('a)", None),
                   ("(a b)", None),
                   ("(a b c)", None),
                   ("(a b c d e f (g) h (i j) k (l m n) o (p q (r s) t) u (v (w (x (y (z))))))", None),
                   ("(a . b)", None),
                   ("(a b . c)", None),
                   ("(() (()()))", None)]
    
    for test, expected in to_process:
        print "----"
        print "test    :", test
        print "expected:", expected
        tokens = tokenize([test])
        result = list(parse(tokens))

        print "result  :", 
        for sexp in result:
            print sexp,
        print 
        print "printed :", 
        for x in result:
            print sexp_str(x),
        print 

# test()

