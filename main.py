
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
        ("true" , "true" ),
        ("false" , "false" ),
        # -------------------------------------- Self Evaluating
        ("4"     , "4" ),
        ("-455"  , "-455" ),
        # -------------------------------------- Use of Special Forms
        ("hi"        , "(quote hi)"),
        ("( + 3 4 )" , "(quote (+ 3 4))"),
        ("hello"     , "'hello"),
        ("( hello )" , "'(hello)"),
        ("define-ok" , "(define x 20)" ),
        ("20"        , "x" ),
        ("set-ok"    , "(set! x 44)" ),
        ("44"        , "x" ),
        ("define-ok" , "(define m 2)" ),
        ("define-ok" , "(define (add8 y) (+ 8 y) )" ),
        ("define-ok" , "(define (getspoon) 'spoon )" ),
        ("define-ok" , "(define (mac x y z)  (+ x (* y z) ))" ),
        ("10"        , "(add8 m)" ),
        ("1001"      , "(mac 1 10 100)" ),
        ("y"         , "(if true 'y 'n)" ),
        ("y"         , "(if true 'y)" ),
        ("nil"       , "(if false 'y)" ),
        ("5"         , "(if (= 2 3) (- 3) (+ 2 3) )" ),
        # ("#PROC"     , "(lambda (z) (+ 3 z))" ),
        ("13"        , "((lambda (z) (+ 3 z)) 10)" ),
        # ("#PROC"     , "(lambda () 5)" ),
        ("222"       , "((lambda (x) (+ 111 x) 222) 333)"),
        ("5"         , "((lambda () 5))" ),
        ("5"         , "(begin 2 3 4 5)" ),
        ("nil"       , "(begin (+ x 3) nil)"),
        ("4"         , "(begin (set! x -99) 4)"),
        ("-99"       , "x" ),
        # -------------------------------------- Pairs
        ("( 4 . 5 )" , "(cons 4 5)"),
        ("( nil . 6 )" , "(cons () 6)"),
        ("4"         , "(car (cons 4 5))"),
        ("5"         , "(cdr (cons 4 5))"),
        # -------------------------------------- Nesting
        ("10"        , "(if true (if true 10 20) 30 )"),
        ("define-ok" , "(define (add13 y) (+ ((lambda (z) (+ 3 z)) 10) y) )" ),
        ("15"        , "(add13 (- 0(- 0 2)) )" ),
        # -------------------------------------- Shorthand quote
        ("hi"        , "'hi"),
        ("( + 3 4 )" , "'(+ 3 4)"),
        # -------------------------------------- Random
        # ("#PROC"       , "(lambda () (+ 3 -4))" ),
        ("define-ok"   , "(define meep (lambda () (+ 2 -6)))" ),
        ("-4"          , "(meep)" ),
        ("( 45 . 32 )" , "'(45 . 32)" ),
        ("( as . nd )" , "'(as.nd)" ),
        ("nil"         , "(display 'hello)"),
        ("nil"         , "(display2 'hello)"),
        ("6"           , "((lambda (x) (+ x 1)) 5)"),
        ("define-ok"   , "(define aax 2)"),
        ("154"         , "((lambda (moose) (set! aax moose) 154) -73)"),
        ("-73"         , "aax"),
        # -------------------------------------- Maths
        ("true"         , "(< 4 5)"),
        ("false"        , "(< 5 4)"),
        ("false"        , "(< 5 5)"),
        ("false"        , "(> 4 5)"),
        ("true"         , "(> 5 4)"),
        ("false"        , "(> 5 5)"),
        ("false"        , "(= 5 4)"),
        ("false"        , "(= 4 5)"),
        ("true"         , "(= 5 5)"),
        # -------------------------------------- Recurse (works but spams output)
        # ("define-ok"   , "(define (xxx x) (display2 'in) (if (< x 10) (xxx (+ x 1))))"),
        # ("nil"         , "(xxx 0)"),
        # ("nil"         , "(xxx 1)"),
        # ("nil"         , "(xxx 9)"),
        # -------------------------------------- Factorial 
        ("define-ok"   , """(define (factorial n)
                              (if (= n 0)
                                1
                                (if (= n 1)
                                  1
                                  (* n (factorial (- n 1))))))"""),
        ("1"         ,"(factorial 0)"),
        ("1"         ,"(factorial 1)"),
        ("2"         ,"(factorial 2)"),
        ("6"         ,"(factorial 3)"),
        ("40320"     ,"(factorial 8)"),
        # -------------------------------------- Nested Define
        ("define-ok"   , """(define (outer w x)
                              (define (inner y z)
                                (+ w y z))
                              (inner x 1))"""),
        ("111"         ,"(outer 10 100)"),
        # -------------------------------------- Fibonacci James
        ("define-ok"   , """(define (fibonacci-james n)
                                (define (fib n1 n2 aaaaaa)
                                    (if (= aaaaaa n)
                                        n1
                                        (fib n2 (+ n1 n2) (+ aaaaaa 1))))
                                (fib 0 1 0))"""),
        ("55"         ,"(fibonacci-james 10)"),
        # -------------------------------------- Fibonacci
        ("define-ok"   , """(define fibonacci
                              (lambda (n)
                                (define fib 
                                  (lambda (n1 n2 cnt)
                                    (if (= cnt n)
                                        n1
                                        (fib n2 (+ n1 n2) (+ cnt 1)))))
                                (fib 0 1 0)))"""),
        ("55"         ,"(fibonacci 10)"),
        # -------------------------------------- Quine
# ("((lambda (x) (list x (list 'quote x)))'(lambda (x) (list x (list 'quote x))))",
# "((lambda (x) (list x (list 'quote x)))'(lambda (x) (list x (list 'quote x))))"),
        # -------------------------------------- String
        ('"jam"'      , '"jam"'),
        ('"jam"'      , '(car (cons "jam" "spoon"))'),
        ('"jam"'      , '\'"jam"'),
        # -------------------------------------- Done
        # ("nil"         , "(env)" ),
        ("nil"         , "()" )]

    syms, vals = zip(*basic_environment)
    env = environment(syms, vals)
    env = env.extend([],[])

    DEBUG = False

    for n, (expected, inp) in enumerate(to_test):
        if DEBUG: print "----"
        if DEBUG: print "input    ", inp
        if DEBUG: print "expected ", expected
        tok = tokenize([inp])
        tok = list(tok)
        exp = parse(tok)
        exp = list(exp)

        results = list(repl(env,exp))
        assert len(results) == 1
        res = results[0]

        if DEBUG: print "result   ", res
        
        if str(res) != expected:
            print "Mismatch Error!"
            print "  > input    ", inp
            print "  > expected ", expected
            # print "  > sexp     ", exp
            print "  > result   ", res   
            print "-------------"
            
testall()

def testme(): 
    inp = """
    (define list (lambda args args))
    (define when (mac body 
       (list 'if (car body) (cons 'begin (cdr body)))))
    (define a 4)
    (when (= a 4) 'hello)
"""

    inp2 = """
    (define MM false)
    (callcc (lambda (k) 6))
    (display MM)
    (callcc (lambda (jaaam) (set! MM jaaam)))
    (display MM)

    (define CC false)
    ((lambda (i)
        (callcc (lambda (k) (set! CC k)))
        (display i)
        (set! i (+ i 1)))0)

    (CC nil)
    (CC nil)
    (CC nil)

    (define KK false)
    (begin 
         (display (callcc (lambda (k) (set! KK k) 'jam)))
         (newline))
    (KK 5)
    (KK 'moose)
    """

    syms, vals = zip(*basic_environment)
    env = environment(syms, vals)
    for result in repl(env.extend([],[]),parse(tokenize([inp]))):
        print "$", result

testme()

def read_file(stream, env):

    for result in repl(env, parse(tokenize(iter(stream)))):
        print result

def main():
    syms, vals = zip(*basic_environment)
    env = environment(syms, vals)

    with open("prelude.scm") as prelude:
        read_file(prelude, env)

    for result in repl(env.extend([],[]),parse(tokenize(reader_raw()))):
        print result
main()

