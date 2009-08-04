
from repl import eval_list, lipy_eval

class function(object):
    def __init__(self,func):
        self.func = func

    def apply(self, continuation, context, args):
        continuation, result = self.func(continuation, context, args)
        return continuation, result

class procedure(object):
    def __init__(self, body, lipy_vars):
        self.body = body
        self.vars = lipy_vars
    
    def apply(self, continuation, context, args):
        # evaluate the arguments
        continuation, args = eval_list(continuation, context, args)

        # add the arguments to the environment in a new frame
        context = context.extened(self.vars,args)

        # evaluate the body in an extened environment
        result = lipy_eval(continuation, context, self.body)

        return continuation, result    

#Convert a python function into a form
#suitable for the interpreter
# TODO this should be a deccorator
def predefined_function(inputfunction):
    def func(continuation, context, args):
        continuation, args = eval_list(continuation, context, args)
        argList = []
        while args != "nil":
            arg, args = args
            argList.append(arg)
        result = inputfunction(*argList)
        if result == None:
            result = "nil"
        return continuation, result
    return function(func)

def display(continuation, context, args):
    continuation, args = eval_list(continuation, context, args)
    # print "FUNC display"
    # print type(args[0]), args[0]
    print args[0]
    return continuation, "nil"

def display2(arg):
    # print "FUNC display2"
    # print type(arg), arg
    print arg

# -----------------------------------------------------------------------------
# QUOTE - done
# 
# (quote <exp>)
# 
# Return the <exp> without the quote part.
# 
# example:
#   hi      <= (quote hi)
#   (+ 3 4) <= (quote (+ 3 4))
# -----------------------------------------------------------------------------
def quote_func(continuation, context, args):
    return continuation, args[0]

# -----------------------------------------------------------------------------
# ASSIGNMENT
# 
# (set! <var> <value>)
# 
# Find in the environment the varable <var> and change
# it's value to <value>
# 
# example:
#   ok  <= (define x 20)
#   20  <= x
#   ok  <= (set! x 44)
#   44  <= x
# -----------------------------------------------------------------------------

def set_func(continuation, context, args):
    var = args[0]
    arg = args[1][0]
    context.set(var,arg)
    return continuation, "ok"

# -----------------------------------------------------------------------------
# DEFINITION - done
# 
# 1. (define <var> <value>)
# 2. (define (<var> <param1> ... <paramN> ) <body> )
# 
# 1. Add <var> to the environment with the value eval(<value>).
# 2. Convert the second form to define a lambda expression.
#      (define <var> ( lambda (<param1> ... <paramN>) <body> ))
#    process this in the same way as form one.
# 
# example:
#   ok <= (define m 2)
#   ok <= (define (add8 y) (+ 8 y) )
#   10 <= (add8 m)
# -----------------------------------------------------------------------------

def define_func(continuation, context, args):
    if isinstance(args[0], str):
        var = args[0]
        arg = args[1][0]
    else:
        var = args[0][0]
        lambda_vars = args[0][1]
        lambda_body = args[1]
        arg = ["lambda", [lambda_vars, lambda_body]]
    continuation, result = lipy_eval(continuation,context,arg)
    context.add(var, result)
    return continuation, "ok"

# -----------------------------------------------------------------------------
# IF - done
# 
# (if <pred> <cons> <alt> )
# 
# evaluate the predicate. If it's true then
# evaluate the consequence, otherwise
# evaluate the alternative (or nil if there is no alt)
# 
# example:
#   y <= (if true? 'y 'n)
#   5 <= (if (= 2 3) (- 3) (+ 2 3) )
#   nil <= (if (= 2 3) 'boop)
# -----------------------------------------------------------------------------

def if_func(continuation, context, args):
    continuation, result = lipy_eval(continuation, context, args[0])
    if result == "true":
        return lipy_eval(continuation, context, args[1][0])
    else:
        if args[1][1] == "nil":
            return continuation, "nil"
        else:
            return lipy_eval(continuation, context, args[1][1][0])

# -----------------------------------------------------------------------------
# LAMBDA - done
# 
# (lambda (<param1> ... <paramN>) <body> )
# 
# make a procedure.
# 
# example:
#   #FUN <= (lambda (x) (+ 3 x))b
#   13   <= ((lambda (x) (+ 3 x)) 10)
# -----------------------------------------------------------------------------

def lambda_func(continuation, context, args):   
    if args[0] == "nil":
        lipy_vars = "nil"
    else:
        lipy_vars = args[0][0]
    body = args[1][0]
    return continuation, procedure(body, lipy_vars)

# -----------------------------------------------------------------------------
# BEGIN - done
# 
# (begin <exp1> ... <expN>)
# 
# evaluate each expression in turn. Returning the result
# of that last one.
# 
# example:
#   5   <= (begin 2 3 4 5)
#   nil <= (begin (+ x 3) nil)  // shouldn't change x
#   4   <= (begin (set! x 3) 4) // should change x
# -----------------------------------------------------------------------------

def begin_func(continuation, context, args):
    continuation, res = lipy_eval(continuation, context, args[0])
    if args[1] == "nil":
        return continuation, res
    # don't need to retuen the continuation here as 
    # it is done inside the inner begin_func
    return begin_func(continuation, context, args[1])

# -----------------------------------------------------------------------------

basic_environment = [
    ("nil", "nil"),
    ("true", "true"),
    ("false", "false"),
    ("quote" , function(quote_func)),
    ("set!"  , function(set_func)),
    ("define", function(define_func)),
    ("if"    , function(if_func)),
    ("lambda", function(lambda_func)),
    ("begin" , function(begin_func)),
    ("display", function(display)),
    ("display2", predefined_function(display2))]



