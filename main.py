
from lex import tokenize
from parse import parse
from environment import environment
from function import basic_environment
from repl import repl

def reader_raw():
    """a generator which returns one complete sexp as a string"""
    code = ""
    brackets = 0
    while True:
        if code == "":
            prompt = ">>>"
        else:
            prompt = "..."
        ln = raw_input(prompt)
        code+=ln+" "
        brackets+=ln.count("(") -  ln.count(")")
        if brackets == 0 and len(ln.strip())!=0:
            yield code
            code = ""

def testall():

    to_test = [
        # -------------------------------------- Special Symbols
        ("nil"   , "()" ),
        ("nil"   , "nil" ),
        ("true?" , "true?" ),
        # -------------------------------------- Self Evaluating
        ("4"     , "4" ),
        ("-455"  , "-455" ),
        # -------------------------------------- Use of Special Forms
        ("hi"        , "(quote hi)"),
        ("( + 3 4 )" , "(quote (+ 3 4))"),
        ("hello"     , "'hello"),
        ("( hello )" , "'(hello)"),
        ("ok"        , "(define x 20)" ),
        ("20"        , "x" ),
        ("ok"        , "(set! x 44)" ),
        ("44"        , "x" ),
        ("ok"        , "(define m 2)" ),
        ("ok"        , "(define (add8 y) (+ 8 y) )" ),
        ("ok"        , "(define (getspoon) 'spoon )" ),
        ("10"        , "(add8 m)" ),
        ("y"         , "(if true? 'y 'n)" ),
        ("5"         , "(if (= 2 3) (- 3) (+ 2 3) )" ),
        # ("#PROC"     , "(lambda (z) (+ 3 z))" ),
        ("13"        , "((lambda (z) (+ 3 z)) 10)" ),
        # ("#PROC"     , "(lambda () 5)" ),
        ("5"         , "((lambda () 5))" ),
        ("5"         , "(begin 2 3 4 5)" ),
        ("nil"       , "(begin (+ x 3) nil)"),
        ("4"         , "(begin (set! x -99) 4)"),
        ("-99"       , "x" ),
        # -------------------------------------- Nesting
        ("10"        , "(if true? (if true? 10 20) 30 )"),
        ("ok"        , "(define (add13 y) (+ ((lambda (z) (+ 3 z)) 10) y) )" ),
        ("15"        , "(add13 (-(- 2)) )" ),
        # -------------------------------------- Shorthand quote
        ("hi"        , "'hi"),
        ("( + 3 4 )" , "'(+ 3 4)"),
        # -------------------------------------- Random
        # ("#PROC"       , "(lambda () (+ 3 -4))" ),
        ("ok"          , "(define meep (lambda () (+ 2 -6)))" ),
        ("-4"          , "(meep)" ),
        ("( 45 . 32 )" , "'(45 . 32)" ),
        ("( as . nd )" , "'(as.nd)" ),
        ("nil"         , "(display 'hello)"),
        ("nil"         , "(display2 'hello)"),
        # -------------------------------------- Done
        ("nil"   , "()" )]

    syms, vals = zip(*basic_environment)
    env = environment(syms, vals)

    for n, (expected, inp) in enumerate(to_test):
        print "----"
        print "input    ", inp
        print "expected ", expected
        tok = tokenize([inp])
        exp = parse(tok)
        res = repl(env,exp)
        print "result   ", res    
        
        if str(res) != expected:
            print "mismatch error"
testall()
