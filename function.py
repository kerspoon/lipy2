
from repl import eval_list, lipy_eval
from trampoline import thunk

def flatten(x):
    """flatten(sequence) -> list

    Returns a single, flat list which contains all elements retrieved
    from the sequence and all recursively contained sub-sequences
    (iterables).

    Examples:
    >>> [1, 2, [3,4], (5,6)]
    [1, 2, [3, 4], (5, 6)]
    >>> flatten([[[1,2,3], (42,None)], [4,5], [6], 7, MyVector(8,9,10)])
    [1, 2, 3, 42, None, 4, 5, 6, 7, 8, 9, 10]
    
    http://kogs-www.informatik.uni-hamburg.de/~meine/python_tricks
    """

    result = []
    for el in x:
        #if isinstance(el, (list, tuple)):
        if hasattr(el, "__iter__") and not isinstance(el, basestring):
            result.extend(flatten(el))
        else:
            result.append(el)
    return result

class procedure(object):
    def __init__(self, body, lipy_vars):
        self.body = body
        self.vars = lipy_vars
    
    def __call__(self, context, args, continuation):
        # print "procedure", self, args
        def call_inner( evaled_args ):
            # add the arguments to the environment in a new frame
            newcontext = context.extend(flatten(self.vars)[:-1], flatten(evaled_args)[:-1])

            def call_inner2(result): 
                return thunk(continuation)(result)

            # evaluate the body in an extened environment
            return thunk(lipy_eval)(newcontext, self.body, call_inner2)

        # evaluate the arguments
        return thunk(eval_list)(context, args, call_inner)

#Convert a python function into a form
#suitable for the interpreter
# TODO this should be a deccorator
# it also should be refectored, lots of messy code
def predefined_function(inputfunction):
    def func(context, args, continuation):
        def predefined_function_inner(evaled_args):
            argList = []
            while evaled_args != "nil":
                arg, evaled_args = evaled_args
                argList.append(arg)
            result = inputfunction(*argList)
            if result == None:
                result = "nil"
            return thunk(continuation)(result)
        return thunk(eval_list)(context, args, predefined_function_inner)
    return func

def display(context, args, continuation):
    def display_inner(x):
        print x[0]
        return thunk(continuation)("nil")
    return thunk(eval_list)(context, args, display_inner)

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

def quote_func(context, args, continuation):
    return thunk(continuation)(args[0])

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

def set_func(context, args, continuation):

    var = args[0]
    arg = args[1][0]

    def set_func_inner(evaled_arg):
        context.set(var,evaled_arg)
        return thunk(continuation)("set-ok")

    return thunk(lipy_eval)(context, arg, set_func_inner)
    
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

def define_func(context, args, continuation):
    if isinstance(args[0], str):
        (var,  (arg, tmp_nil)) = args 
        assert tmp_nil == "nil", "invalid args to define"
    else:
        ((var, lambda_vars), lambda_body) = args
        arg = ["lambda", [lambda_vars, lambda_body]]
    context.add(var, "define-in-progress")

    def define_func_inner(result): 
        # print "inner", result
        context.set(var, result)
        return thunk(continuation)("define-ok")

    # print "define_func", args
    return thunk(lipy_eval)(context, arg, define_func_inner)

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

def if_func(context, args, continuation):
    
    (condition, (true_thunk, (false_thunk, tmp_nil))) = args
    assert tmp_nil == "nil"

    # inner_if :: sexp -> None
    def inner_if(evaluated_args):
        if ( evaluated_args == 'true' ):
            return thunk(lipy_eval)(context, true_thunk, continuation)
        else:
            return thunk(lipy_eval)(context, false_thunk, continuation)

    return thunk(lipy_eval)(context, condition, inner_if)

# -----------------------------------------------------------------------------
# LAMBDA - done
# 
# (lambda (<param1> ... <paramN>) <body> )
# 
# make a procedure.
# 
# example:
#   #FUN <= (lambda (x) (+ 3 x))
#   13   <= ((lambda (x) (+ 3 x)) 10)
#   222  <= ((lambda (x) (+ 111 x) 222) 333)
# -----------------------------------------------------------------------------

def lambda_func(context, args, continuation):   
    if args[0] == "nil":
        lipy_vars = "nil"
    else:
        lipy_vars = args[0]
    body = args[1]
    return thunk(continuation)(procedure(["begin", body], lipy_vars))

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

def begin_func(context, args, continuation):

    def begin_func_inner(res):
        if args[1] == "nil":
            return thunk(continuation)(res)
        return thunk(begin_func)(context, args[1], continuation)
        
    return thunk(lipy_eval)(context, args[0], begin_func_inner)

# -----------------------------------------------------------------------------
# call/cc - done
# 
# (call/cc <lambda_exp>)
# 
# call the lambda_exp with the paremeter of the current continuation
# 
# -----------------------------------------------------------------------------

def callcc_func(context, args, continuation):
    stored_cont = continuation
    def callable_continuation(context, args, continuation2):
        def callable_continuation_inner(arggg):
            return thunk(stored_cont)(arggg)
        return thunk(eval_list)(context, args, callable_continuation_inner)

    def callcc_func_inner(func):
        xx = ["quote", [callable_continuation, "nil"]]
        return thunk(func)(context, [xx, "nil"] , continuation)

    return thunk(lipy_eval)(context, args[0], callcc_func_inner)

# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------


# def environment_func(context, args, continuation):
#     assert args == "nil"
#     print context
#     return continuation, "nil"

def to_scm_bool(x):
    if x:
        return "true"
    return "false"

def newline_func():
    print ""

basic_environment = [
    ("nil", "nil"),
    ("true", "true"),
    ("false", "false"),
    ("quote" , quote_func),
    ("set!"  , set_func),
    ("define", define_func),
    ("if"    , if_func),
    ("lambda", lambda_func),
    ("begin" , begin_func),
    ("callcc", callcc_func),
    ("display", display),
    ("display2", predefined_function(display2)),
    ("newline", predefined_function(newline_func)),
    ("+", predefined_function(lambda *args:sum(args))),
    ("*", predefined_function(lambda *args:reduce(int.__mul__, args))),
    ("-", predefined_function(lambda a, b:a - b)),
    ("<", predefined_function(lambda a, b:to_scm_bool(a < b))),
    (">", predefined_function(lambda a, b:to_scm_bool(a > b))),
    ("=", predefined_function(lambda a, b:to_scm_bool(a == b))),
    ("cons", predefined_function(lambda a, b:[a, b])),
    ("car", predefined_function(lambda(a, b):a)),
    ("cdr", predefined_function(lambda(a, b):b))]

# sexp_str, lipy_eval, call/cc, ^, environment

    
