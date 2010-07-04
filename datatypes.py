
from environment import Environment

# ------------------------------------------------------------------------------

class LispBase(object):
    pass
    
# ------------------------------------------------------------------------------

class LispNil(LispBase):
    def __init__(self): pass
    def scm_eval(self, env): return self
    def __str__(self): return "nil"

nil = LispNil()

# ------------------------------------------------------------------------------

class LispSymbol(LispBase):
    def __init__(self, name):
        """__init__ :: Str 'name' -> None"""
        assert isinstance(name, str)
        self.name = name
        
    def scm_eval(self, env):
        return env.get(self.name)

    def __str__(self):
        return self.name

obarray = {}

def mksym(name):
    """mysym :: Str 'name' -> Symbol"""
    assert isinstance(name, str)
    # assert valid_symbol_name(name), "invalid atom in symbol %s" % name
    if name not in obarray:
        obarray[name] = LispSymbol(name)
    return obarray[name]

# ------------------------------------------------------------------------------

class LispPair(LispBase):
    def __init__(self, first, rest):
        self.first = first
        self.rest = rest
    
    def scm_eval(self, env):
        func = self.first.scm_eval(env)
        return func(self.rest, env)

    def __str__(self):
        text = "( "
        sexp = self
        while (isinstance(sexp, LispPair)):
            text += str(sexp.first) + " "
            sexp = sexp.rest
        
        if sexp != nil:
            text += ". " + str(sexp) + " "
        text += ")"
        return text

def cons(first, rest):
    return LispPair(first, rest)

def from_list(args):
    # from_list :: [LispBase] -> LispPair
    # note that for a proper list a nil must be put at the end
    if len(args) <= 1: raise Exception("must have 2 elements")
    if len(args) == 2: return cons(args[0], args[1])
    return cons(args[0], from_list(args[1:]))

def to_list(sexp):
    # from_list :: LispPair -> [LispBase]
    # note that a proper list will have a nil at the end
    result = []
    while (isinstance(sexp, LispPair)):
        result.append(sexp.first)
        sexp = sexp.rest
    result.append(sexp)
    return result

def first(args):
    assert isinstance(args, LispPair)
    return args.first
    
def rest(args):
    assert isinstance(args, LispPair)
    return args.rest

# ------------------------------------------------------------------------------

class LispLambda(object):
    def __init__(self, scm_vars, body):
        """Procedure :: SchemeBase -> LispPair"""
        
        # print "vars\t", scm_vars

        self.body = cons(mksym("begin"), body)

        if scm_vars is nil:
            self.scm_vars = nil
        elif isinstance(scm_vars, LispSymbol):
            self.scm_vars = str(scm_vars)
        else:
            assert isinstance(scm_vars, LispPair)
            self.scm_vars = map(str, to_list(scm_vars))
        
    
    def __call__(self, args, env):
        """__call__ :: SchemePair -> Environment"""

        if False:
            print "class-call"
            print "\tvars\t", self.scm_vars
            print "\targs\t", args

        if self.scm_vars is nil:
            assert args is nil
            new_env = Environment([], [], env)
            # print "\tcall\tnil"
        elif isinstance(self.scm_vars, str):
            combined_args = from_list([arg.scm_eval(env) for arg in to_list(args)])
            new_env = Environment([self.scm_vars], [combined_args], env)
            # print "\tcall\t", combined_args
        else:
            evaled_args = [arg.scm_eval(env) for arg in to_list(args)]
            assert len(self.scm_vars) == len(evaled_args)
            new_env = Environment(self.scm_vars, evaled_args, env)
            # print "\tcall\t", [str(x) for x in evaled_args]

        return self.body.scm_eval(new_env)
    
    def scm_eval(self, env):
        return mksym("<#procedure#>")

    def __str__(self):
        return "<#procedure#>"

# ------------------------------------------------------------------------------

class LispBool(LispBase):
    def __init__(self, val): 
        assert (val is True) or (val is False)
        self.val = val
    def scm_eval(self, env): return self
    def __str__(self): return str(self.val).lower()

true = LispBool(True)
false = LispBool(False)

# ------------------------------------------------------------------------------

class LispString(LispBase):
    def __init__(self, text):
        assert isinstance(text, str)
        self.text = text
    def scm_eval(self, env): return self
    def __str__(self): return '"%s"' % self.text

# ------------------------------------------------------------------------------

class LispInteger(LispBase):
    def __init__(self, num):
        assert isinstance(num, int)
        self.num = num
    def scm_eval(self, env): return self
    def __str__(self): return str(self.num)

# ------------------------------------------------------------------------------
