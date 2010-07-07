
from lex import tokenize
from parse import parse
from environment import Environment
from function import basic_environment

DEBUG = False

# -----------------------------------------------------------------------------

def repl(env, parser):
    """reads a statement, evaluates it, applys (calls 
       as function) then prints it's result"""

    for sexp in parser:
        # if DEBUG: print "#< ", str(sexp)
        result = sexp.scm_eval(env)
        # if DEBUG: print "#> ", str(result)
        yield str(result)


# -----------------------------------------------------------------------------

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

# -----------------------------------------------------------------------------

def read_file(stream, env):
    if DEBUG: print "read file start:", stream
    for result in repl(env, parse(tokenize(iter(stream)))):
        if DEBUG: print result
    if DEBUG: print "read file finished: ", stream

# -----------------------------------------------------------------------------

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
        ("nil"       , "(define x 20)" ),
        ("20"        , "x" ),
        ("nil"       , "(set! x 44)" ),
        ("44"        , "x" ),
        ("nil"       , "(define m 2)" ),
        ("nil"       , "(define (add8 y) (+ 8 y) )" ),
        ("nil"       , "(define (getspoon) 'spoon )" ),
        ("nil"       , "(define (rac x y z)  (+ x (* y z) ))" ),
        ("10"        , "(add8 m)" ),
        ("1001"      , "(rac 1 10 100)" ),
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
        ("nil" , "(define (add13 y) (+ ((lambda (z) (+ 3 z)) 10) y) )" ),
        ("15"        , "(add13 (- 0(- 0 2)) )" ),
        # -------------------------------------- Shorthand quote
        ("hi"        , "'hi"),
        ("( + 3 4 )" , "'(+ 3 4)"),
        # -------------------------------------- Random
        # ("#PROC"       , "(lambda () (+ 3 -4))" ),
        ("nil"         , "(define meep (lambda () (+ 2 -6)))" ),
        ("-4"          , "(meep)" ),
        ("( 45 . 32 )" , "'(45 . 32)" ),
        ("( as . nd )" , "'(as.nd)" ),
        ("nil"         , "(display 'hello)"),
        ("6"           , "((lambda (x) (+ x 1)) 5)"),
        ("nil"         , "(define aax 2)"),
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
        # -------------------------------------- Recurse (works but spams)
        ("nil"         , "(define (xxx x) (display 'in) (if (< x 10) (xxx (+ x 1))))"),
        # ("nil"         , "(xxx 0)"),
        # ("nil"         , "(xxx 1)"),
        # ("nil"         , "(xxx 9)"),
        # -------------------------------------- Factorial 
        ("nil"       , """(define (factorial n)
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
        ("nil"   , """(define (outer w x)
                              (define (inner y z)
                                (+ w (+ y z)))
                              (inner x 1))"""),
        ("111"         ,"(outer 10 100)"),
        # -------------------------------------- Fibonacci James
        ("nil"   , """(define (fibonacci-james n)
                                (define (fib n1 n2 aaaaaa)
                                    (if (= aaaaaa n)
                                        n1
                                        (fib n2 (+ n1 n2) (+ aaaaaa 1))))
                                (fib 0 1 0))"""),
        ("55"         ,"(fibonacci-james 10)"),
        # -------------------------------------- Fibonacci
        ("nil"   , """(define fibonacci
                              (lambda (n)
                                (define fib 
                                  (lambda (n1 n2 cnt)
                                    (if (= cnt n)
                                        n1
                                        (fib n2 (+ n1 n2) (+ cnt 1)))))
                                (fib 0 1 0)))"""),
        ("55"         ,"(fibonacci 10)"),
        # -------------------------------------- String
        ('"jam"'      , '"jam"'),
        ('"jam"'      , '(car (cons "jam" "spoon"))'),
        ('"jam"'      , '\'"jam"'),
        # -------------------------------------- Basic Functions
        ("nil"       , "(define (test0) 0)"),
        ("0"         , "(test0)"),
        ("nil"       , "(define (test1 x) x)"),
        ("-5"        , "(test1 -5)"),
        ("nil"       , "(define (test2 x y) (cons x y))"),
        ("( 6 . hi )", "(test2 6 'hi)"),
        ("nil"       , "(define (test3 x y z) (set! x y) z)"),
        ("hi"        , "(test3 x 6 'hi)"),
        ("nil"       , "(define (test4 x y z) (+ x y) z)"),
        ("56"        , "(test4 12 34 56)"),
        ("nil"       , "(define (test5 x y z) (+ x y) z (+ 2 4) (+ 7 z))"),
        ("9"         , "(test5 4 3 2)"),
        # -------------------------------------- Dotted Function Calling
        ("nil"           , "(define (test6 . all) all)"),
        ("( 1 )"         , "(test6 1)"),
        ("( 1 2 )"       , "(test6 1 2)"),
        ("( ( a . b ) )" , "(test6 '(a . b))"),
        ("nil"           , "(define (list . x) x)"),
        ("nil"           , "(define (test7 a . all) (list all a))"),
        ("( nil 1 )"     , "(test7 1)"),
        ("( ( 2 ) 1 )"   , "(test7 1 2)"),
        ("( ( 2 3 4 5 6 ) 1 )"   , "(test7 1 2 3 4 5 6)"),
        # -------------------------------------- Dotted Lambda Calling
        ("( 1 )"         , "((lambda all all) 1)"),
        ("( 1 2 )"       , "((lambda all all) 1 2)"),
        ("( ( a . b ) )" , "((lambda all all) '(a . b))"),
        ("( nil 1 )"     , "((lambda (a . all) (list all a)) 1)"),
        ("( ( 2 ) 1 )"   , "((lambda (a . all) (list all a)) 1 2)"),
        ("( ( 2 3 4 5 6 ) 1 )"   , "((lambda (a . all) (list all a)) 1 2 3 4 5 6)"),
        # -------------------------------------- Quine
("( ( lambda ( x ) ( list x ( list ( quote quote ) x ) ) ) ( quote ( lambda ( x ) ( list x ( list ( quote quote ) x ) ) ) ) )",
 "( ( lambda ( x ) ( list x ( list ( quote quote ) x ) ) ) ( quote ( lambda ( x ) ( list x ( list ( quote quote ) x ) ) ) ) )"),
        # -------------------------------------- Class
        ("<#class#>"         , "class-base" ),
        ("nil"               , "(define point (class (class-base) (_x _y) (length total thing)))"),
        ("nil"               , "(class-set! point 'length 2)"),
        ("nil"               , "(class-set! point 'total (lambda (self) (+ (self _x) (self _y))))"),
        ("nil"               , "(class-set! point 'thing (lambda (self mm) (+ mm ((self total) self))))"),
        ("2"                 , "(point length)"),
        ("<#procedure#>"     , "(point total)"),
        ("nil"               , "(define p1 (class (point) () ()))"),
        ("nil"               , "(class-set! p1 '_x 4)"),
        ("nil"               , "(class-set! p1 '_y 6)"),
        ("4"                 , "(p1 _x)"),
        ("6"                 , "(p1 _y)"),
        ("<#procedure#>"     , "(p1 total)"),
        ("10"                , "((point total) p1)"),
        ("10"                , "((p1 total) p1)"),
        # ("110"               , "(p1 thing 100)"),
        # -------------------------------------- Macros
        ("<#procedure#>" , "(mac (yyx) (+ 3 yyx))" ),
        ("3"             , "((mac (x) x) (+ 1 2))" ),
        ("nil"           , "(define ggg 835)" ),
        ("835"           , "((mac (ggg) 'ggg) (+ 1 2))" ),
        ("nil"           , "(define when (mac (test . body) (list 'if test (cons 'begin body))))" ),
        ("jam"           , "(when (= 4 4) 'jam)" ),
        ("nil"           , "(when (= 3 4) 'jam)" ),
        # -------------------------------------- Quasiquote
        ("a"                 , "(quasiquote a)" ),
        ("( a )"             , "(quasiquote (a))" ),
        ("( a b )"           , "(quasiquote (a b))" ),
        ("( a b c )"         , "(quasiquote (a b c))" ),
        ("( a . b )"         , "(quasiquote (a . b))" ),
        ("( a b c )"         , "(quasiquote (a b c))" ),
        ("( a b . c )"       , "(quasiquote (a b . c))" ),
        ("( a b a b )"       , "(quasiquote (a b . (a b)))" ),
        ("( quote a )"       , "(quasiquote 'a)" ),
        ("a"                 , "(quasiquote (unquote 'a))" ),
        ("( ( quote a ) b )" , "(quasiquote ( 'a (unquote 'b)))" ),
        ("( list 3 4 )"      , "(quasiquote (list (unquote (+ 1 2)) 4))" ),
        ("( a b 3 4 )"       , "(quasiquote (a . (b (unquote (+ 1 2)) 4)))" ),
        ("( a ( quasiquote ( b ( unquote c ) d ) ) e )" , 
         "(quasiquote ( a (quasiquote ( b (unquote c) d)) e ))" ),
        # -------------------------------------- Quasiquote (Sugar)
        ("a"                 , "`a" ),
        ("( a )"             , "`(a)" ),
        ("( a b )"           , "`(a b)" ),
        ("( a b c )"         , "`(a b c)" ),
        ("( a . b )"         , "`(a . b)" ),
        ("( a b c )"         , "`(a b c)" ),
        ("( a b . c )"       , "`(a b . c)" ),
        ("( a b a b )"       , "`(a b . (a b))" ), # tested on plt-scheme
        ("( quote a )"       , "`'a" ),
        ("a"                 , "`,'a" ),
        ("( ( quote a ) b )" , "`( 'a ,'b)" ),
        ("( list 3 4 )"      , "`(list ,(+ 1 2) 4)" ),
        ("( a b 3 4 )"       , "`(a . (b ,(+ 1 2) 4))" ),
        ("( a ( quasiquote ( b ( unquote c ) d ) ) e )" , "`(a`(b,c d)e)" ),
        # -------------------------------------- Done
        ("nil"         , "()" )]

    env = Environment([], [], basic_environment)

    print "testing: toplevel"
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


# -----------------------------------------------------------------------------

def main():
    inp = """
; (define (list . x) x)
"----- START -----"

"""

    env = Environment([], [], basic_environment)

    if True:
        with open("prelude.scm") as prelude:
            read_file(prelude, env)

    if True:
        for result in repl(env,parse(tokenize([inp]))):
            print "$", result

    if False:
        for result in repl(env,parse(tokenize(reader_raw()))):
            print result
main()


# -----------------------------------------------------------------------------
