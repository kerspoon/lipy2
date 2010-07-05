
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

# ------------------------------------------------------------------------------

debug = True

class LispLambda(object):
    def __init__(self, scm_vars, body):
        """Procedure :: SchemeBase -> LispPair"""
        
        # print "vars\t", scm_vars

        self.body = cons(mksym("begin"), body)

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
            print "\tvars\t", scm_vars
            print "\tvars\t", self.scm_vars

    def __call__(self, args, env):
        """__call__ :: SchemePair -> Environment"""

        # eval everything
        evaled_args = [arg.scm_eval(env) for arg in to_list(args)]

        if debug:
            print "lambda-call"
            print "\tvars\t", self.scm_vars
            print "\targs\t", args
            print "\tcall\t", [str(x) for x in evaled_args]

        if self.scm_vars[-1] is nil:
            # remove the ending nil
            evaled_vars = self.scm_vars[:-1]
            evaled_args = evaled_args[:-1]
        else:
            # create the combined 'rest'
            evaled_vars = self.scm_vars
            start_args = evaled_args[:len(self.scm_vars)-1]
            rest_args  = from_list(evaled_args[len(self.scm_vars)-1:])
            evaled_args = start_args + [rest_args]

        # vars and args must match exactly
        assert len(evaled_vars) == len(evaled_args)
            
        if debug:
            print "\tcall\t", [str(x) for x in evaled_vars]
            print "\twith\t", [str(x) for x in evaled_args]

        # extend the Environment with the new frame
        new_env = Environment(evaled_vars, evaled_args, env)

        # eval the body in the new Environment
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

class LispClass(LispBase):
    
    def __init__(self, parents, parameters, slots):
        
        print "pre-make-class:"
        print "\tparents", parents
        print "\tparameters", parameters
        print "\tslots", slots

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
            self.parameters[p] = "nil"

        for sc in self.parents:
            for s in sc.slots:
                if s not in self.slots:
                    self.parameters[s] = "nil"

            for p,v in sc.parameters.items():
                    self.parameters[p] = v

        print "make-class:"
        print "\tparents", self.parents
        print "\tparameters", self.parameters
        print "\tslots", self.slots

    def __call__(self, args, env):
        """__call__ :: SchemePair -> Environment"""

        print "call-class:"
        print "\targs", args

        # find the parameter name
        param = self.parameters[first(args)]

        # return as data when only one arg
        if rest(args) is nil: 
            return param

        # call as function with `self` and the rest of args
        new_args = cons(self, rest(args))
        result = param(new_args, env)
        return result

    def scm_eval(self, env): return mksym("<#class#>")
    def __str__(self): return "<#class#>"

class_base = LispClass(set(), set(), set())

# ------------------------------------------------------------------------------
