from datatypes import nil, true, false, mksym, cons, from_list, to_list, LispSymbol, LispLambda, LispPair, first, rest, LispInteger, LispClass, class_base, Environment

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

    # todo set the datatype
    env.define(var.name, None, result)
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
# (class <parent1> ...)
# 
# create a new class
# 
# -----------------------------------------------------------------------------

def class_func(args, env):

    # turn to a list and remove the trailing nil
    parents = to_list(args)[:-1]

    # lookup the parents
    evaled_parents = [parent.scm_eval(env) for parent in parents]

    return LispClass(evaled_parents)

# -----------------------------------------------------------------------------
# class-define!
# 
# (class-define! <class-name> <var-name> <type>)
# (class-define! <class-name> <var-name>)
# 
# add a variable to a class
#
# (class-define! Point + (Lambda Point Point Point))
# (class-define! Point y  Int)
# 
# -----------------------------------------------------------------------------

def class_define_func(args, env):

    class_name = first(args)
    var_name = first(rest(args))

    # todo: deal with the datatype
    # datatype = first(rest(rest(args)))
    evaled_type = None

    evaled_class = class_name.scm_eval(env)
    evaled_var = var_name.scm_eval(env).name
    evaled_class.define(evaled_var, evaled_type)

    return nil

# -----------------------------------------------------------------------------
# class-set!
# 
# (class-set! <class-name> <var-name> <value>)
# 
# set a class variable's value
# 
# -----------------------------------------------------------------------------

def class_set_func(args, env):
    
    class_name = first(args)
    var_name = first(rest(args))
    value = first(rest(rest(args)))

    evaled_class = class_name.scm_eval(env)
    evaled_var   = var_name.scm_eval(env).name
    evaled_value = value.scm_eval(env)

    # print "class", class_name, evaled_class
    # print "param", param_name, evaled_param
    # print "value", value, evaled_value

    evaled_class.set(evaled_var, evaled_value)
    return nil

# -----------------------------------------------------------------------------
# class-chmod!
# 
# (class-chmod! <class-name> <var-name> . <flags>)
# 
# set a class variable's permission
#
# (class-chmod! Point str 'read-only)
# (class-chmod! Point x   'any 'virtual)
#
# -----------------------------------------------------------------------------
 
def class_chmod_func(args, env):

    class_name = first(args)
    var_name = first(rest(args))
    flags = to_list(rest(rest(args)))[:-1]

    evaled_class = class_name.scm_eval(env)
    evaled_var   = var_name.scm_eval(env).name
    evaled_flags = [flag.scm_eval(env).name for flag in flags]

    evaled_class.chmod(evaled_var, evaled_flags)
    return nil
    
# -----------------------------------------------------------------------------
# class-finalize!
# 
# (class-finalize! <class-name> )
# 
# set a class variable's permission
#
# (class-finalize! Point)
#
# -----------------------------------------------------------------------------
 
def class_finalize_func(args, env):

    class_name = first(args)

    evaled_class = class_name.scm_eval(env)

    evaled_class.finalised = True
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
#
# -----------------------------------------------------------------------------
 
def macro_func(args, env):

    param = first(args)
    body = rest(args)

    return LispLambda(param, body, True)

# -----------------------------------------------------------------------------
# quasiquote
# 
# (quasiquote <param>)
#
# If no `unquote` appear within the <param>, the result of is equivalent to 
# evaluating quote. If `unquote` does appears the expression following the 
# comma is evaluated and its result is inserted into the structure instead of 
# the comma and the expression. 
#
# It is basically a completly new way to eval a sexp. One where only unquote
# and unquote-splicing and quasiquote really do anything interesting. 
#
# 
# example:
# 
#   'a                 --> a
#   (quote a b)        --> ERROR (too many args)
#   `a                 --> a
#   `,a                --> eval(a)
#   (quasiquote a b)   --> ERROR (too many args)
#   `(a (unquote d b)) --> ERROR (too many args)
#   (unquote a b)      --> ERROR (not in quasiquote)
#   `(a)               --> (a)
#   `(a ,c)            --> (a eval(c))
#   `(a (b ,c))        --> (a (b eval(c)))
#   ``,a               --> `,a
#   `(list ,(+ 1 2) 4) -->  (list 3 4)
#   `(a `(b ,c) d)     --> (a `(b ,c) d)
#
# -----------------------------------------------------------------------------

def unquote_func(args, env):
    raise Exception("Cannot call unquote outsite of quasiquote")

def quasiquote_func(args, env):
    assert rest(args) is nil, "ERROR (too many args in quasiquote)"
    arg = first(args)

    if not isinstance(arg, LispPair):
        return arg
    else:
        # build up new list with 'unquote' evaluated
        def inner_qq(inargs):
            # print "in args", inargs
            if first(inargs) is mksym("unquote"):
                # (unquote x) -> (eval x)
                assert rest(rest(inargs)) is nil
                return first(rest(inargs)).scm_eval(env)
            elif first(inargs) is mksym("quasiquote"):
                # (quasiquote x) -> (quasiquote x)
                assert rest(rest(inargs)) is nil
                return inargs
            elif first(inargs) is mksym("unquote-splicing"):
                raise Exception("Not implemented")
            else:
                # recurse the list checking each elm
                # return the newly formed list
                newlist = []
                while isinstance(inargs, LispPair):
                    if isinstance(first(inargs), LispPair):
                        newlist.append(inner_qq(first(inargs)))
                    else:
                        newlist.append(first(inargs))
                    inargs = rest(inargs)
                
                # deal with the final element (which is probably a nil)
                if isinstance(inargs, LispPair):
                    newlist.append(inner_qq(inargs))
                else:
                    newlist.append(inargs)
                # put the list back into sexp
                return from_list(newlist)

        return inner_qq(arg)

# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------

def predefined_function(inputfunction):
    def func(args, env):
        evaled_args = [arg.scm_eval(env) for arg in to_list(args)][:-1]
        result = inputfunction(*evaled_args)
        if result is None: result = nil
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

        ("class"           , class_func),
        ("class-define!"   , class_define_func),
        ("class-set!"      , class_set_func),
        ("class-chmod!"    , class_chmod_func),
        ("class-finalize!" , class_finalize_func),
        ("BaseClass"       , class_base),

        ("mac"         , macro_func),
        ("quasiquote"  , quasiquote_func),
        ("unquote"     , unquote_func),

        ("display", predefined_function(lambda a: display(str(a)))),
        ("newline", predefined_function(lambda a: display("\n"))),

        ("cons"   , predefined_function(lambda a, b: cons(a, b))),
        ("car"    , predefined_function(lambda(a): first(a))),
        ("cdr"    , predefined_function(lambda(a): rest(a))),
        ("is?"    , predefined_function(lambda x, y: to_scm_bool(x is y))),
        ("equal?" , predefined_function(lambda x, y: to_scm_bool(x == y))),

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

