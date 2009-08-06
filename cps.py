

"""
Continuation Passing Style, Trampolining, call/cc, and Monads

Trampolining: http://home.pipeline.com/~hbaker1/CheneyMTA.html
              http://jtauber.com/blog/2008/03/30/thunks,_trampolines_and_continuation_passing/

CPS: http://blogs.msdn.com/wesdyer/archive/2007/12/22/continuation-passing-style.aspx
Monads: http://blog.sigfpe.com/2006/08/you-could-have-invented-monads-and.html

Monads are a way of passing information between pure functional functions. A random number generator needs a seed which will change with every call. Normally this would be a mutable global; however in pure functional languages you cannot have mutable variables. Hence you have to have the following:

    # rng :: int -> (int, int)
    def rng(seed):
        ...
        return val, new_seed

    val1, seed1 = rng(27633)
    val2, seed2 = rng(seed1)
    val3, seed3 = rng(seed2)
    
It would be hugely annoying to have to pass the seed into every function that uses 'rng'. Monads tie up the seed so you don't have to worry about it. 

----------

CPS is a style of writing functions where, among other things, they never return. They have an extra argument called the continuation which represents the operations to perform when it's done with it's calcluations. So, rather than return we call the continuation. It has the effect of giving the code the look of being inisde out. 

The continutation itself is simply a function that takes the return value of the function and never returns. Because it never returns you will have a stack overflow unless your language has tail call optimisiation. Interestingly all calls are tail calls because no function ever returns any code after a function call will never be executed. 

It is annoying and error prone having to pass the continuation round explicity, but as it is a form of modifying state it is the perfect canditate to be a Monad. 

    # Identity :: t -> (t -> Void) -> Void
    def Identity(value, continuation):
        continuation(value)
     
    # Main :: Void -> Void
    def Main():
        # Inner :: str -> Void
        Inner = lambda s: print s
     
        Identity("foo", Inner)

----------

Trampolining is a way to implement tail call optimisiation. Whenever you have a tail call you return the function an parameters to a dispatcher. The dispatcher then calls that function with the arguments it was given. The net effect is that your functions gets called in the order you want but you don't use the stack. 

If you using Trampolining when using CPS you wont blow the stack. 

    def trampoline(bouncer):
        while callable(bouncer):
            bouncer = bouncer()
        return bouncer

----------

call/cc is the name of a function in scheme that takes one argument. That argument is a function which takes one parameter. That parementer is the continutation. Hence call-with-current-continuation. You can then store the continuation at any point in the programs execution and jump back to it at any other point. Using call/cc we can implement many control flow structures such as return, exceptions, virtual-threads, longjmp, goto.  

If you use CPS you can implement call/cc very easily. You have the continuation passed explicity into every function. Even if Trampolining and CPS isnt used it can be helpful to think of it this way. You have a partial snapshort of the programs execution, which you can jump back to after possibly changing some of the values in that snapshot.

    guile> (define CC #f)
    guile> (let ((i 0))
        (call/cc (lambda (k) (set! CC k)))
        (printf "~s~n" i)
        (set! i (+ i 1)))
    0
    guile> (CC nil)
    1
    guile> (CC nil)
    2

Here we store the continuation, print out i, increment i then call the stored continuation (with a value of which isn't used). This has the effect of jumping us to the line with call/cc and it returning nil. from here we print out the now changed value of i. and so it all once again. 

    guile> (define KK #f)
    guile> (begin 
             (display (call/cc (lambda (k) (set! KK k) "jam")))
             (newline))
    jam
    guile> (KK 5)
    5
    guile> (KK "moose")
    moose 

In this one we use the value given to the continuation. 
"""

thunk = lambda name, *args: lambda: name(*args)

_factorial = lambda n, c=identity: c(1) if n == 0 else thunk(_factorial, n - 1, lambda result: thunk(c, n * result))

def factorial (n, c=identity):
    c(1)
    if n == 0:
    else:
        thunk(factorial, n - 1, lambda result: thunk(c, n * result))


# ------------------------
# Example 1
# ------------------------

# Identity :: t -> t
def Identity(value):
    return value

# Main :: Void -> Void
def Main():
    print Identity("foo")

# ------------------------

# Identity :: t -> (t -> Void) -> Void
def Identity(value, continuation):
    continuation(value)

# Main :: Void -> Void
def Main():
    # Inner :: str -> Void
    Inner = lambda s: print s

    Identity("foo", Inner)

# ------------------------
# Example 2
# ------------------------

# AddFour :: int -> int
def AddFour(value):
    return value + 4

# Stringify :: int -> str
def Stringify(value):
    return "jam " + str(value) 

# Main :: Void -> Void
def Main():
    print Stringify(AddFour(10))

# ------------------------

# AddFour :: int -> (int -> Void) -> Void
def AddFour(value, continuation):
    continuation(value + 4)

# Stringify :: int -> (str -> Void) -> Void
def Stringify(value, continuation):
    continuation("jam " + str(value))

# Main :: Void -> Void
def Main():
   
    # InnerInner :: str -> Void
    InnerInner =  lambda value: print value

    # Inner :: int -> void
    Inner = lambda s: Stringify(s,InnerInner)

    AddFour(10,Inner)

# ------------------------
# Example 3
# ------------------------

def iffy(value):
    if value > 4:
        return "spoons"
    else:
        return "jams"

# Main :: Void -> Void
def Main():
    print iffy(5)

# ------------------------

# Main :: Void -> Void
def Main():
    # Inner :: str -> Void
    Inner = lambda value: print value
    
    iffy(5,Inner)

# iffy :: int -> (str, -> Void) -> Void
def iffy(value, continuation):
    if value > 4:
        continuation("spoons")
    else:
        continuation("jams")

# ------------------------
# Example 4
# ------------------------

# lipy_if :: Context -> (sexp, sexp, sexp) -> sexp
def lipy_if(context, args):

    (condition, true_thunk, false_thunk) = args

    condition = lipy_eval(context, condition)

    if ( condition == 'true' ):
        return lipy_eval(context, true_thunk)
    else:
        return lipy_eval(context, false_thunk)

# lipy_eval :: Context -> sexp -> sexp
def lipy_eval(context, code):
    if isinstance(code,str):
        return context.lookup(code)
    elif isinstance(code,int):
        return code
    elif isinstance(code,list):
        func = lipy_eval(context, code[0])
        return funct(context, code[1])

# Main :: Void -> Void
def Main():
    context = Context()
    context.define("if", lipy_if)
    print lipy_eval(Context(), parse(tokenize("(if (< 1 2) 3 4)")))

# ------------------------

# Main :: Void -> Void
def Main():
    # Inner :: sexp -> Void
    Inner = lambda value: print value

    parsed = parse(tokenize("(if (< 1 2) 3 4)"))
    context = Context()

    context.define("if", lipy_if)
    lipy_eval(context, parsed, Inner)

# lipy_eval :: Context -> sexp -> (sexp -> None) -> None
def lipy_eval(context, code, continuation):
    if isinstance(code,str):
        continuation(context.lookup(code))
    elif isinstance(code,int):
        continuation(code)
    elif isinstance(code,list):
        # inner_apply :: sexp -> None
        inner_apply = lambda func: func(context, code[1], continuation)
        lipy_eval(context, code[0], inner_apply)

# lipy_if :: Context -> sexp -> (sexp -> None) -> None
def lipy_if(context, args, continuation):
    
    (condition, true_thunk, false_thunk) = args
    
    # inner_if :: sexp -> None
    def inner_if(evaluated_args):
        if ( evaluated_args[0] == 'true' ):
            lipy_eval(context, true_thunk, continuation)
        else:
            lipy_eval(context, false_thunk, continuation)

    lipy_eval(context, condition, inner_if)

# ---------------------------------------------------------
# with Trampolining

thunk = lambda name: lambda *args: lambda: name(*args)
identity = lambda x: x
def _trampoline(bouncer):
    while callable(bouncer):
        bouncer = bouncer()
    return bouncer
trampoline = lambda f: lambda *args: _trampoline(f(*args))

def Main():
    parsed = parse(tokenize("(if (< 1 2) 3 4)"))
    context = Context()
    context.define("if", lipy_if)

    lipy = trampoline(lipy_eval)
    result = lipy(context, parsed, identity)
    print result 

# lipy_eval :: Context -> sexp -> (sexp -> None) -> None
def lipy_eval(context, code, continuation):
    if isinstance(code,str):
        return thunk(continuation)(context.lookup(code))
    elif isinstance(code,int):
        return thunk(continuation)(code)
    elif isinstance(code,list):
        # inner_apply :: sexp -> None
        inner_apply = lambda func: func(context, code[1], continuation)
        return thunk(lipy_eval)(context, code[0], inner_apply)

# lipy_if :: Context -> sexp -> (sexp -> None) -> None
def lipy_if(context, args, continuation):
    
    (condition, true_thunk, false_thunk) = args
    
    # inner_if :: sexp -> None
    def inner_if(evaluated_args):
        if ( evaluated_args[0] == 'true' ):
            return thunk(lipy_eval)(context, true_thunk, continuation)
        else:
            return thunk(lipy_eval)(context, false_thunk, continuation)

    return thunk(lipy_eval)(context, condition, inner_if)
