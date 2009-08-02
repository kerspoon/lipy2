
from symbol import NIL, QUOTE 

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
    # print "parse start:", tok 

    # if tok == ")":
    #     print "Error", [tok] + list(tokens)
    #     exit

    assert len(tok) != 0, "zero sized token"
    assert tok != ".", "found '.' outside of pair"
    assert tok != ")", "found ')' mismatched bracket"

    if tok == "'":
        # print "got a quote"
        return [QUOTE, [inner_parse(tokens), NIL]]
    elif tok == "(":
        tok = tokens.next()

        if tok == ")":
            return NIL

        tokens.undo(tok)
        sexp = [inner_parse(tokens), NIL]
        full_sexp = sexp
        # print "sexp:", full_sexp, tokens.peek()

        while (tokens.peek() not in [")", "."]):
            sexp[1] = [inner_parse(tokens),NIL]
            sexp = sexp[1]
        
        tok = tokens.next()
        if tok == ".":
            # print "peakr:", tokens.peek()
            sexp[1] = inner_parse(tokens)
            # print "full_sexp", full_sexp
            assert tokens.next() == ")", "expected one sexp after a fullstop"
        else:
            assert tok == ")"
        return full_sexp
    else:
        # we have a symbol or number
        # print "symbol:", tok, tokens.peek()
        
        return tok

def parse(tokens):
    while (True):
        yield inner_parse(tokens)

def test():
    from lex import tokenize

    print "result=", list(parse(iterator_undo(tokenize("a"))))
    print "-----"
    print "result=", list(parse(iterator_undo(tokenize("'a"))))
    print "-----"
    print "result=", list(parse(iterator_undo(tokenize("()"))))
    print "-----"
    print "result=", list(parse(iterator_undo(tokenize("(a )"))))
    print "-----"
    print "result=", list(parse(iterator_undo(tokenize("(a b)"))))
    print "-----"
    print "result=", list(parse(iterator_undo(tokenize("(a c . b)"))))
    print "-----"
    print "result=", list(parse(iterator_undo(tokenize("(a . b)"))))
    print "-----"
    print "result=", list(parse(iterator_undo(tokenize("(() ())"))))
    print "-----"
    print "result=", list(parse(iterator_undo(tokenize("(a b c ())"))))
    print "-----"
    # print "result=", list(parse(iterator_undo(tokenize("(a c . b c)"))))
    print "-----"

test()

