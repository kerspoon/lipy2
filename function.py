from datatypes import nil, true, false, mksym, cons, from_list, to_list, LispSymbol, LispLambda, LispPair, first, rest, LispInteger, LispClass, class_base
from environment import Environment

# -----------------------------------------------------------------------------
# QUOTE
# 
# (quote <exp>)
# 
# Return the <exp> without the quote part.
# 
# example:
#   hi      <= (quote hi)
#   (+ 3 4) <= (quote (+ 3 4))
# -----------------------------------------------------------------------------

def quote_func(args, env):
    args = to_list(args)
    assert args[-1] is nil
    assert len(args) == 2
    return args[0]

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

def set_func(args, env):
    args = to_list(args)
    assert args[-1] is nil
    assert len(args) == 3

    var = args[0]
    arg = args[1]

    assert isinstance(var, LispSymbol)

    evaled_arg = arg.scm_eval(env)
    env.set(var.name, evaled_arg)
    return nil

# -----------------------------------------------------------------------------
# DEFINITION
# 
# 1. (define <var> <value>)
# 2. (define (<var> <param1> ... <paramN> ) <body1> ... )
# 2. (define (<var> . <param1> ) <body1> ... )
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

def define_func(args, env):

    if isinstance(first(args), LispSymbol):
        # we have the first form

        args = to_list(args)
        assert args[-1] is nil
        assert len(args) == 3

        var = args[0]
        value = args[1]

    elif isinstance(first(args), LispPair):
        # we have the second form

        var = first(first(args))
        param = rest(first(args))
        body = rest(args)

        assert isinstance(var, (LispSymbol, LispPair))

        value = from_list([mksym("lambda"), param, body])
    else:
        raise Exception("invalid form")

    assert isinstance(var, LispSymbol)
    result = value.scm_eval(env)
    env.add(var.name, result)
    return nil

# -----------------------------------------------------------------------------
# IF
# 
# (if <pred> <cons> <alt> )
# (if <pred> <cons> )
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

def if_func(args, env):

    args = to_list(args)
    assert args[-1] is nil
    assert 3 <= len(args) <= 4
    
    predicate   = args[0]
    consequence = args[1]
    alternative = args[2]

    result = predicate.scm_eval(env)

    if result is true:
        return consequence.scm_eval(env)
    else:
        return alternative.scm_eval(env)

# -----------------------------------------------------------------------------
# LAMBDA
# 
# (lambda (<param1> ... <paramN>) <body1> ... )
# (lambda <param> <body1> ... )
# 
# make a procedure, <parameters> can be a symbol, proper-list or 
# dotted-list. when evaluated returns the value of (eval <bodyN>) 
# in an environment where <parameters> are bound to the arguments.
# 
# example:
#   #FUN <= (lambda (x) (+ 3 x))
#   13   <= ((lambda (x) (+ 3 x)) 10)
#   222  <= ((lambda (x) (+ 111 x) 222) 333)
# -----------------------------------------------------------------------------

def lambda_func(args, env):

    param = first(args)
    body = rest(args)

    return LispLambda(param, body)

# -----------------------------------------------------------------------------
# BEGIN 
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

def begin_func(args, env):

    args = to_list(args)
    assert args[-1] is nil, "invalid args for 'begin': %s" % args
    assert len(args) >= 2, "invalid args for 'begin': %s" % args

    for arg in args[:-1]:
        result = arg.scm_eval(env)
    return result


# -----------------------------------------------------------------------------
# class
# 
# (class (<parent1> ...) (slot1 ...) (parameter1 ...))
# 
# create a new class
# 
# -----------------------------------------------------------------------------

def class_func(args, env):

    # turn to a list and remove the trailing nil
    # make the params and slots a string
    parents = to_list(first(args))[:-1]
    params = [str(x) for x in to_list(first(rest(args)))[:-1]]
    slots = [str(x) for x in to_list(first(rest(rest(args))))[:-1]]

    # lookup the parents
    evaled_parents = [parent.scm_eval(env) for parent in parents]

    return LispClass(evaled_parents, params, slots)

# -----------------------------------------------------------------------------
# class-set!
# 
# (class-set! <class-name> <param-name> <value>)
# 
# change the value of `slot` in `class` to `value`.
# 
# -----------------------------------------------------------------------------

def class_set_func(args, env):
    
    class_name = first(args)
    param_name = first(rest(args))
    value = first(rest(rest(args)))


    evaled_class = class_name.scm_eval(env)
    evaled_param = param_name.scm_eval(env)
    evaled_value = value.scm_eval(env)

    print "class", class_name, evaled_class
    print "param", param_name, evaled_param
    print "value", value, evaled_value

    evaled_class.parameters[evaled_param] = evaled_value

    return nil

# -----------------------------------------------------------------------------
# Macro
# 
# (mac (<param1> ... <paramN>) <body1> ... )
# (mac <param> <body1> ... )
# 
# make a procedure, <parameters> can be a symbol, proper-list or 
# dotted-list. when evaluated returns the value of (eval <bodyN>) 
# in an environment where <parameters> are bound to the arguments.
# 
# example:
#   #FUN <= (mac (x) (+ 3 x))
#   (+ 1)<= ((mac (x) x) (+ 1))
#   #FUN <= (define when (mac (test . body) (list ('if test (cons 'begin body))))
#   jam  <= (when (= 4 4) 'jam)
# -----------------------------------------------------------------------------
 
def macro_func(args, env):

    param = first(args)
    body = rest(args)

    return LispLambda(param, body, True)

# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------

def predefined_function(inputfunction):
    def func(args, env):
        evaled_args = [arg.scm_eval(env) for arg in to_list(args)][:-1]
        result = inputfunction(*evaled_args)
        if result == None: result = nil
        return result
    return func

def to_scm_bool(x):
    if x: return true
    else: return false

def two_integer_function(inputfunction):
    def func(args, env):
        evaled_args = [arg.scm_eval(env) for arg in to_list(args)][:-1]

        assert len(evaled_args) == 2
        assert isinstance(evaled_args[0], LispInteger)
        assert isinstance(evaled_args[1], LispInteger)
        result = inputfunction(evaled_args[0].num, evaled_args[1].num)
        if isinstance(result, int):
            result = LispInteger(result)
        return result
    return func

def display(text):
    print text

# -----------------------------------------------------------------------------

def make_basic_environment():
    
    basic = [
        ("nil"   , nil),
        ("true"  , true),
        ("false" , false),
        ("quote" , quote_func),
        ("set!"  , set_func),
        ("define", define_func),
        ("if"    , if_func),
        ("lambda", lambda_func),
        ("begin" , begin_func),

        ("class"      , class_func),
        ("class-set!" , class_set_func),
        ("class-base" , class_base),

        ("mac"  , macro_func),

        ("display", predefined_function(lambda a: display(str(a)))),
        ("newline", predefined_function(lambda a: display("\n"))),

        ("cons", predefined_function(lambda a, b: cons(a, b))),
        ("car" , predefined_function(lambda(a): first(a))),
        ("cdr" , predefined_function(lambda(a): rest(a))),
        ("is"  , predefined_function(lambda x, y: to_scm_bool(x is y))),

        ("+",  two_integer_function(lambda a, b: a + b)),
        ("*",  two_integer_function(lambda a, b: a * b)),
        ("-",  two_integer_function(lambda a, b: a - b)),
        ("<",  two_integer_function(lambda a, b:to_scm_bool(a < b))),
        (">",  two_integer_function(lambda a, b:to_scm_bool(a > b))),
        ("=",  two_integer_function(lambda a, b:to_scm_bool(a == b))),
        ("<=", two_integer_function(lambda a, b:to_scm_bool(a <= b))),
        (">=", two_integer_function(lambda a, b:to_scm_bool(a >= b)))]

    syms, vals = [], []
    for sym,val in basic:
        syms.append(sym)
        vals.append(val)

    return Environment(syms, vals, None)

basic_environment = make_basic_environment()

# -----------------------------------------------------------------------------



# anything that can be called or is stored in the envorinment needs to have its types checked. 

# You can call something currently one of 3 ways.
#   defined in function.py (special form)
#   LispLambda.__call_
#   LispClass.__call_

# you can change the environment by:
#   define
#   set!

# you can also chencge things in the environment through 
#   class-set!

