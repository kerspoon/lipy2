#scheme.py
#This is a implementations of an intrepreter
#for a small subset of scheme.
#
#What it has:
#Commands
#   Look at the function 'eval'
#Functions
#   look at the dictionary 'predefineds'
#
#Examples:
#1)Fibonacci numbers
#python scheme.py
#>>>(define fibonacci
#...  (lambda (n)
#...    (define fib 
#...      (lambda (n1 n2 cnt)
#...        (if (= cnt n)
#...            n1
#...            (fib n2 (+ n1 n2) (+ cnt 1)))))
#...    (fib 0 1 0)))
#>>>(display (fibonacci 10))
#55
#>>>
#
#2)Coroutines
#python scheme.py
#>>>(define list (lambda l l))
#>>>(define message 
#...  (lambda (cont msg)
#...    (call/cc 
#...     (lambda (newCont) 
#...       (cont (cons newCont msg))))))
#>>>(define f
#...  (lambda (fname cont msg)
#...    (display (cons fname msg))
#...    (define msgList (message cont (+ 1 msg)))
#...    (f fname (car msgList) (cdr msgList))))
#>>>(define msg 
#...    (call/cc (lambda (cont)
#...               (f "f1:" cont 1))))
#>>>(f "f2" (car msg) (cdr msg))
#
#Changes;
#24-Feb-2005 Added quote and the quote symbol '
#25-Feb-2005 Fixed a bug with begin
#25-Feb-2005 Added eval
#25-Feb-2005 Added py-eval and py-exec

#Uncomment the following line if you are using python 2.2
#from __future__ import generators
import re

py_context = {}
py_eval_func = eval

class context:
    def setVars(self, names, values):
        if names == None:
            return
        elif isinstance(names, symbol):
            self.vars[str(names)] = values
        else:   
            (name, restNames) = names
            (value, restValues) = values
            self.vars[str(name)]=value
            self.setVars(restNames, restValues)

    def __init__(self, parent, var_names = None, values = None):
        self.parent = parent
        self.vars = {}
        self.setVars(var_names, values)

    def get(self, var_name):
        if self.vars.has_key(var_name):
            return self.vars[var_name]
        elif self.parent != None:
            return self.parent.get(var_name)
        else:
            raise KeyError("Unknown variable "+var_name)

    def set(self, var_name, value):
        if self.vars.has_key(var_name):
            self.vars[var_name] = value
        elif self.parent != None:
            return self.parent.set(var_name, value)
        else:
            raise Key("Unknown variable " + var_name)

    def define(self, var_name, value):
        self.vars[var_name] = value
        

class symbol:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return self.value

    def __repr__(self):
        return "symbol('"+self.value+"')"

    def __eq__(self, value):
        if isinstance(value, symbol):
            return self.value == value.value
        else:
            return False

# Predefined Symbols (can't be redefined)
LAMBDA = symbol("lambda")
IF = symbol("if")
BEGIN = symbol("begin")
SET = symbol("set!")
DEFINE = symbol("define")
LOAD = symbol("load")
QUOTE = symbol("quote")

#The tokenizer

#Token Types
OPENBRACKET = 0
CLOSEBRACKET = 2
ATOM = 3
SYMBOL = 4
DOT = 5
SINGLE_QUOTE = 6

tokens_re = re.compile(r'\(|\)|(?:[\w+\-*/<>=!?.]+)|'+
                       r'(?:"(?:[^"]|\\")+")|'+
                       r'(?:#(?:t|f|(?:\\(?:newline|space|.))))|'+
                       r'\'')
def tokenize(code):
    """This is a very simple tokenizer,
    it accepts a string that represents
    the code an returns a list of
    token type, token paris"""
    
    tokens = tokens_re.findall(code)
    for token in tokens:
        if token == "(":
            yield (OPENBRACKET, token)
        elif token == ")":
            yield (CLOSEBRACKET, token)
        elif token == ".":
            yield (DOT, token)
        elif token == "'":
            yield (SINGLE_QUOTE, token)
        elif token.isdigit():
            yield (ATOM, int(token))
        elif token[0]=='"':
            yield (ATOM, token[1:-1].replace(r'\\', "\\").replace(r'\"', r'"'))
        elif token[0]=="#":
            if token[1]=="\\":
                char = token[2:]
                if char == "space":
                    char = " "
                if char == "newline":
                    char = "\n"
                yield (ATOM, char)
            elif token[1]=="t":
                yield (ATOM, True)
            elif token[1]=="f":
                yield (ATOM, False)
            else:
                raise Exception("Invalid token "+ token)
        else:
            yield (SYMBOL, symbol(token))

            
#S-Espressions
def process_sexpr(tokens):
    token_type, value = tokens.next()
    if token_type == SINGLE_QUOTE:
        return [QUOTE, [process_sexpr(tokens), None]]
    elif token_type == OPENBRACKET:
        cons = [None, None]
        lst = cons
        token = None
        while True :
            token = process_sexpr(tokens)
            if token not in [")", "."]:
                cons[1] = [token, None]
                cons = cons[1]
            else:
                break
        if token == ".":
            cons[1] = process_sexpr(tokens)
            token_type, token = tokens.next()
        if token == ")":
            return lst[1]
        else:
            raise Exception("expected close bracket for expression "+
                            str(lst)+token)
    else:
        return value

def sexpr(text):
    return process_sexpr(tokenize(text))


def sexprs(text):
    """Build an s-expression from a string"""
    lst = [None, None]
    cur = lst
    tokens = tokenize(text)
    try:
        while True:
            cur[1] = [process_sexpr(tokens), None]
            cur = cur[1]
    except StopIteration:
        pass
    return lst[1]
        
        
    
#Pedefined Functions

#Convert a python function into a form
#suitable for the interpreter
def predefined_function(function):
    def func(continuation, args):
        argList = []
        while args!=None:
            arg, args = args
            argList.append(arg)
        return continuation, function(*argList)
    return func

#Some basic predefined functions

def display(obj):
    print obj

def callcc(continuation, args):
    (func, nil) = args
    def cont_func(cont, (arg, nil)):
        return (continuation, arg)
    return func(continuation, (cont_func, None))

def gen_eval(context):
    def eval_func(continuation, arg):
        expr, nil = arg
        return (eval_continuation(continuation, context, expr), None)
    return eval_func

def py_exec(continuation, arg):
    code, nil = arg
    exec code in py_context
    return (continuation, None)

def py_eval(continuation, arg):
    code, nil = arg
    return (continuation, py_eval_func(code, py_context))
    

global_context = context(None)

predefineds = {"+":predefined_function(lambda *args:sum(args)),
               "*":predefined_function(lambda *args:reduce(int.__mul__, args)),
               "-":predefined_function(lambda a, b:a - b),
               "<":predefined_function(lambda a, b:a < b),
               ">":predefined_function(lambda a, b:a > b),
               "=":predefined_function(lambda a, b:a == b),
               "cons":predefined_function(lambda a, b:[a, b]),
               "car":predefined_function(lambda(a, b):a),
               "cdr":predefined_function(lambda(a, b):b),
               "display":predefined_function(display),
               "call-with-current-continuation":callcc,
               "call/cc":callcc,
               "eval":gen_eval(global_context),
               "py-exec":py_exec,
               "py-eval":py_eval}

global_context.vars = predefineds

#Eval

#A continuation for the evaluation of an expression
class eval_continuation:
    
    def __init__(self, continuation, context, expr):
        self.next = continuation
        self.context = context
        self.expr = expr

    def run(self, val):
        return eval(self.next, self.context, self.expr)

def eval_str(continuation, context, code):
    if isinstance(code, str):
        code = sexpr(code)
    return eval(continuation, context, code)

#The eval method       
def eval(continuation, context,  code):
    if isinstance(code, list):
        if code[0] == LAMBDA:
            return eval_lambda(continuation, context,  code)
        elif code[0] == IF:
            return eval_if(continuation, context, code)
        elif code[0]== BEGIN:
            return eval_begin(continuation, context, code)
        elif code[0] == DEFINE:
            return eval_define(continuation, context, code)
        elif code[0] == SET:
            return eval_set(continuation, context, code)
        elif code[0] == QUOTE:
            return eval_quote(continuation, context, code)
        elif code[0] == LOAD:
            return eval_load(continuation, context, code)
        else:
            return eval_apply(continuation, context, code)
    elif isinstance(code, symbol):
        return (continuation, context.get(str(code)))
    else:
        return (continuation, code)

#Helper to evaluate a list of expressions
class expr_list_continuation:
    def __init__(self, continuation, context, exprs):
        expr, rest = exprs
        self.expr = expr
        if rest == None:
            self.continuation = continuation
        else:
            self.continuation = expr_list_continuation(continuation,
                                                       context, rest)
        self.context = context
        
    def run(self, value):
        return eval(self.continuation, self.context, self.expr)

def eval_expr_list(continuation, context, exprs):
    return (expr_list_continuation(continuation, context, exprs), None)
    

#Quote
def eval_quote(continuation, context, code):
    (quote, (item, nil)) = code
    return (continuation, item)

#Load
def eval_load(continuation, context, code):
    (load, (filepath, nil)) = code
    fi = file(filepath)
    exprs =  sexprs(fi.read())
    return eval_expr_list(continuation, context, exprs)
    
#Begin
def eval_begin(continuation, context, code):
    begin, exprs = code
    return eval_expr_list(continuation, context, exprs)

#Lambda
def eval_lambda(continuation, parent_context, code):
    (lmbda, (params, exprs)) = code
    def func(continuation, args):
        new_context = context(parent_context, params, args)
        return eval_expr_list(continuation, new_context, exprs)
    return (continuation, func)

#Define
class define_continuation:
    def __init__(self, continuation, context, var_name):
        self.continuation = continuation
        self.context = context
        self.var_name = var_name

    def run(self, value):
        self.context.define(self.var_name, value)
        return self.continuation, None

def eval_define(continuation, context, code):
    (define, (var_name, (expr, nil))) = code
    continuation = define_continuation(continuation,
                                       context, str(var_name))
    return eval(continuation, context, expr)
    
#set!
class set_continuation:
    def __init__(self, continuation, context, var_name):
        self.continuation = continuation
        self.context = context
        self.var_name = var_name

    def run(self, value):
        self.context.set(self.var_name, value)
        return self.continuation, None

def eval_set(continuation, context, code):
    (set, (var_name, (expr, nil))) = code
    continuation = set_continuation(continuation, context,
                                    str(var_name))
    return eval(continuation, context, expr)

#If    
class if_continuation:
    def __init__(self, continuation, context, ifTrue, ifFalse):
        self.continuation = continuation
        self.context = context
        self.ifTrue = ifTrue
        self.ifFalse = ifFalse

    def run(self, value):
        if value:
            return eval(self.continuation,
                        self.context, self.ifTrue)
        else:
            return eval(self.continuation,
                        self.context, self.ifFalse)

def eval_if(continuation, context, code):
    (If, (predicate, (ifTrue, rest))) = code
    if rest==None:
        ifFalse = None
    else:
        ifFalse = rest[0]        
    return eval(if_continuation(continuation, context, ifTrue, ifFalse),
                context, predicate)


#Apply

class apply_continuation:
    def __init__(self, continuation):
        self.continuation = continuation

    def run(self, func):
        return func(self.continuation, self.params)

class param_continuation:
    def __init__(self, continuation, prev):
        self.continuation = continuation
        self.prev = prev
        self.params = None

    def run(self, value):
        self.prev.params = (value, self.params)
        return (self.continuation, None)

class list_param_continuation:
    def __init__(self, continuation, prev):
        self.continuation = continuation
        self.prev = prev
    def run(self, value):
        self.prev.params = value
        return (self.continuation, None)

def construct_param_continuations(continuation,
                                  prev, context, code):
    if isinstance(code, list):
        expr, rest = code
        paramContinuation = param_continuation(continuation, prev)
        continuation = eval_continuation(paramContinuation, context, expr)
        if rest == None:
            return continuation
        else:
            return construct_param_continuations(continuation, paramContinuation,
                                                 context, rest)
    else:
        continuation = list_param_continuation(continuation, prev)
        return eval_continuation(continuation, context, code)
        
    

def eval_apply(continuation, context, code):
    (operator, exprs) = code
    apply_cont = apply_continuation(continuation)
    continuation = eval_continuation(apply_cont, context, operator)
    continuation = construct_param_continuations(continuation, apply_cont,
                                                 context, exprs)
    return (continuation, None)

#The read eval loop

class read_eval_continuation:
    def __init__(self, context, reader):
        self.context = context
        self.reader = reader
        self.code = None
        self.continuation = None

    def run(self, value):
        try:
            if self.code == None:
                self.code = self.reader.next()
                self.continuation = read_eval_continuation(self.context,
                                                           self.reader)
        except StopIteration:
            return None, value
        return eval_str(self.continuation, self.context, self.code)

        
def expression_reader(fi):
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

def read_eval_loop(fi):
    reader = expression_reader(fi)
    continuation = read_eval_continuation(global_context, reader)
    value = "Simple scheme!!!"
    while(continuation!=None):
        (continuation, value) = continuation.run(value)

if __name__=="__main__":
    import sys
    read_eval_loop(sys.stdin)

