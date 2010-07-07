
from environment import Environment

debug = False

# ----------------------------------------------------------------------------

class LispBase(object):
    pass
    
# ----------------------------------------------------------------------------

class LispNil(LispBase):
    def __init__(self): pass
    def scm_eval(self, env): return self
    def __str__(self): return "nil"

nil = LispNil()

# ----------------------------------------------------------------------------

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

# ----------------------------------------------------------------------------

class LispPair(LispBase):
    def __init__(self, first, rest):
        self.first = first
        self.rest = rest
    
    def scm_eval(self, env):
        func = self.first.scm_eval(env)
        assert hasattr(func, '__call__'), "cannot call '%s' in %s" % (func,self)
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
    if len(args) == 0: 
        return nil
    elif len(args) == 1: 
        return args[0]
    elif len(args) == 2: 
        return cons(args[0], args[1])
    else:
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

# ----------------------------------------------------------------------------

def extended_env(scm_vars, scm_args, env):
    """extended_env :: [Str] -> [LispBase] -> Environment -> Environment"""
    
    if scm_vars[-1] is nil:
        # we have a normal list (ending in nil)
        # remove the ending nil
        evaled_vars = scm_vars[:-1]
        evaled_args = scm_args[:-1]
    else:
        # we have a dotted form
        # create the combined 'rest'
        evaled_vars = scm_vars
        start_args = scm_args[:len(scm_vars)-1]
        rest_args  = from_list(scm_args[len(scm_vars)-1:])
        evaled_args = start_args + [rest_args]

    # vars and args must match exactly
    assert len(evaled_vars) == len(evaled_args)
            
    # extend the Environment with the new frame
    return Environment(evaled_vars, evaled_args, env)

class LispLambda(object):
    def __init__(self, scm_vars, body, macro=False):
        """Procedure :: SchemeBase -> LispPair"""

        self.body = cons(mksym("begin"), body)
        self.macro = macro

        if scm_vars is nil:
            self.scm_vars = [nil]
        elif isinstance(scm_vars, LispSymbol):
            self.scm_vars = [str(scm_vars)]
        else:
            assert isinstance(scm_vars, LispPair)
            list_vars = to_list(scm_vars)
            self.scm_vars = map(str, list_vars[:-1]) 
            if list_vars[-1] is nil:
                self.scm_vars.append(nil)
            else:
                self.scm_vars.append(str(list_vars[-1]))
        
        if debug:
            print "lambda-init"
            print "\told vars\t", scm_vars
            print "\tnew vars\t", self.scm_vars
            print "\tbody\t", self.body

    def expand_macro(self, args, env):
        """expand_macro :: SchemePair -> Environment"""

        assert self.macro

        # extend the Environment with the new frame
        new_env = extended_env(self.scm_vars, to_list(args), env)

        # eval in a the new environment to get the macro expansion
        return self.body.scm_eval(new_env)

    def __call__(self, args, env):
        """__call__ :: SchemePair -> Environment"""

        if self.macro:
            # expand in a new env
            mac = self.expand_macro(args, env)
            # call in the *old* one.
            return mac.scm_eval(env)
       
        # eval everything and return as a list
        evaled_args = [arg.scm_eval(env) for arg in to_list(args)]
        
        if debug:
            print "lambda-call"
            print "\tpre vars\t", self.scm_vars
            print "\tpre args\t", args
            print "\tevl args\t", [str(x) for x in evaled_args]

        # extend the Environment with the new frame
        new_env = extended_env(self.scm_vars, evaled_args, env)

        # eval the body in the new Environment
        return self.body.scm_eval(new_env)
    
    def scm_eval(self, env):
        return mksym("<#procedure#>")

    def __str__(self):
        return "<#procedure#>"

# ----------------------------------------------------------------------------

class LispBool(LispBase):
    def __init__(self, val): 
        assert (val is True) or (val is False)
        self.val = val
    def scm_eval(self, env): return self
    def __str__(self): return str(self.val).lower()

true = LispBool(True)
false = LispBool(False)

# ----------------------------------------------------------------------------

class LispString(LispBase):
    def __init__(self, text):
        assert isinstance(text, str)
        self.text = text
    def scm_eval(self, env): return self
    def __str__(self): return '"%s"' % self.text

# ----------------------------------------------------------------------------

class LispInteger(LispBase):
    def __init__(self, num):
        assert isinstance(num, int)
        self.num = num
    def scm_eval(self, env): return self
    def __str__(self): return str(self.num)

# ----------------------------------------------------------------------------

class LispClass(LispBase):
    
    def __init__(self, parents, parameters, slots):
        
        if debug:
            print "pre-make-class:"
            print "\tparents", parents
            print "\tparameters", parameters
            print "\tslots", slots

        self.readonly = []

        # something can't be both a parameter and a slot
        assert set(parameters).isdisjoint(set(slots))

        # gather all super-classes and make unique
        self.parents = set(list(parents))
        for parent in parents:
            self.parents |= parent.parents

        # make sure they are unique
        self.slots = set(list(slots))

        # parameters are anything passed in and
        # anything in superclass parameters & superclass slots.
        # except the ones that are slots in this class
        # they are start as nil
        self.parameters = {}

        for p in parameters:
            self.parameters[p] = nil

        for sc in self.parents:
            for s in sc.slots:
                if s not in self.slots:
                    self.parameters[s] = nil

            for p,v in sc.parameters.items():
                    self.parameters[p] = v

        if debug:
            print "make-class:"
            print "\tparents", self.parents
            print "\tparameters", self.parameters
            print "\tslots", self.slots

    def __call__(self, args, env):
        """__call__ :: SchemePair -> Environment"""
        # return the parameter name

        if debug:
            print "call-class:"
            print "\targs", args

        assert isinstance(first(args), LispSymbol)
        assert rest(args) is nil
        return self.get(first(args).name)

    def get(self, param_name):
        assert param_name not in self.slots
        assert param_name in self.parameters
        assert param_name not in self.readonly
        return self.parameters[param_name]
 
    def set(self, param_name, value):
        assert param_name not in self.slots
        assert param_name in self.parameters
        assert param_name not in self.readonly
        self.parameters[param_name] = value
    
    def make_read_only(self, param_name, value = True):
        assert (param_name in self.parameters) or (param_name in self.slots)
        self.readonly = value
        
    def scm_eval(self, env): return mksym("<#class#>")
    def __str__(self): return "<#class#>"

class_base = LispClass(set(), set(), set())

# -----------------------------------------------------------------------------

