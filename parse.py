
from symbol import NIL, QUOTE

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

def inner_parse(tokens):
    """take the token list from the lexer and make it into an object"""

    tok = tokens.next()
    # print "inner_parse:", tok

    assert len(tok) != 0, "zero sized token"
    assert tok != ".", "found '.' outside of pair"
    assert tok != ")", "found ')' mismatched bracket"

    if tok == "'":
        return [QUOTE, [inner_parse(tokens), NIL]]
    elif tok == "(":
        tok = tokens.next()

        if tok == ")":
            return NIL

        tokens.undo(tok)
        sexp = [inner_parse(tokens), NIL]
        full_sexp = sexp

        while (tokens.peek() not in [")", "."]):
            sexp[1] = [inner_parse(tokens),NIL]
            sexp = sexp[1]
        
        tok = tokens.next()
        if tok == ".":
            sexp[1] = inner_parse(tokens)
            assert tokens.next() == ")", "expected one sexp after a fullstop"
        else:
            assert tok == ")"
        return full_sexp
    else:
        # we have a symbol or number
        # print "symbol:", tok, tokens.peek()
        if isinstance(tok,str):
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
        assert isinstance(sexp,str), "must be str or list"
        assert len(sexp) != 0, "zero sized token"

        if sexp != "nil":
            text += ". " + sexp_str(sexp[0]) + " "
        text += ")"
    elif isinstance(sexp,str):
        text += sexp
    else:
        print type(sexp), str(sexp)
        raise Exception("must be list or str")
    return text 

def test():
    from lex import tokenize

    to_process = [ ("()"        , "NIL"),
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

