
from environment import Environment
from copy import deepcopy

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
            print "\tmacro\t", mac
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

# -----------------------------------------------------------------------------

class Permission(object):
    def __init__(self, flags=None):
        self.set_default()
        if flags:
            self.set_flags(flags)

    def set_default(self):
        self.class_read  = True
        self.class_write = True
        self.any_read    = True
        self.any_write   = True
        self.virtual     = False

    def set_flags(self, flags):
        # todo: could implement flags that set many things
        #       such as read-only or private

        assert set(flags) <= set(["class-read", "no-class-read", 
                                  "class-write", "no-class-write", 
                                  "any-read", "no-any-read", 
                                  "any-write", "no-any-write", 
                                  "virtual", "no-virtual",
                                  "read-only", "private"])

        if "class-read" in flags  : self.class_read  = True
        if "class-write" in flags : self.class_write = True 
        if "any-read" in flags    : self.any_read    = True 
        if "any-write" in flags   : self.any_write   = True 
        if "virtual" in flags     : self.virtual     = True 

        if "no-class-read" in flags  : self.class_read  = False
        if "no-class-write" in flags : self.class_write = False 
        if "no-any-read" in flags    : self.any_read    = False 
        if "no-any-write" in flags   : self.any_write   = False 
        if "no-virtual" in flags     : self.virtual     = False 

        if "read-only" in flags:
            self.any_write = False
            self.class_write = False

        if "private" in flags:
            self.any_read = False
            self.any_write = False

class Variable(object):
    def __init__(self, permission, datatype=None, value=None):
        self.permission = permission
        self.datatype = datatype
        self.value = value

    def __str__(self):
        return self.value


class LispClass(LispBase):

    classid = 0

    def __init__(self, parents):

        # set id as incrementing number for output
        LispClass.classid += 1
        self.id = LispClass.classid

        self.finalised = False
        self.internal  = False

        # gather all super-classes and make unique
        # might as well store the direct parents too
        self.parents = set(list(parents))
        self.direct_parents = self.parents
        for parent in parents:
            self.parents |= parent.parents
        
        # inherit all parents' variables
        # except virtual
        self.variables = {}
        for sc in self.parents:
            for p, v in sc.variables.items():
                # todo: is deepcopy(v) needed?
                self.variables[p] = v
                self.variables[p].permission.virtual = False

        if debug:
            print self.get_info()

    def get_info(self):
        txt = "make-class %s:\n" % self
        txt += "\tfinalised\t%d\n" % self.finalised
        txt += "\tparents\t%s\n" % map(str, self.parents)
        txt += "\tvariables\t%s\n" % str(self.variables)
        return txt

    def define(self, var, datatype=None, value=None):
        # define :: Str 'var' -> Type 'type' -> None
        assert not self.finalised, "can't `define` a finalised class"
        
        # give the default permission and no value
        permission = Permission()
        variable = Variable(permission, datatype, value)
        self.variables[var] = variable

    def set(self, var, value):
        # set :: Str 'var' -> LispBase 'value' -> None
        assert var in self.variables, "%s not in class" % var

        # check permissions
        permissions = self.variables[var].permission
        msg = "insufficient permission to set %s" % var
        assert not permissions.virtual, msg
        if not permissions.any_write:
            assert self.internal and permissions.class_write, msg
        
        # todo: check datatypes match
        self.variables[var].value = value

    def get(self, var):
        # get :: Str 'var' -> LispBase
        assert var in self.variables, "%s not in class" % var

        # check permissions
        permissions = self.variables[var].permission
        msg = "insufficient permission to get %s" % var
        assert not permissions.virtual, msg
        if not permissions.any_read:
            assert self.internal and permissions.class_read, msg
        
        value = self.variables[var].value
        assert value is not None, "%s not set" % var
        return value

    def chmod(self, var, flags):
        # chmod  :: Str 'var' -> [Str] 'flags' -> None
        assert not self.finalised, "can't `chmod` a finalised class"
        assert var in self.variables, "%s not in class" % var
        # todo: should only those with write permission be able to set this?
        self.variables[var].permission.set_flags(flags)

    def call(self, func, args, env):
        # call :: LispBase 'func' -> LispPair 'args' -> LispBase

        # todo: remove these horrible hacks!
        # 
        # They are hack because:
        # 
        #   1. If the func is somehow called from somewhere other than here
        #      it wont have self set or worse will use one from another class!
        #   2. internal set's it for the duration of the function call. if
        #      anything else is call it too has priveladed access. (I guess 
        #      this is consistent with how the Env accesses stuff but I think 
        #      it is wrong for classes. Also if anything raises an exception 
        #      internal does not get changed back and everything gets 
        #      privelaged access.

        if debug:
            print "call-class %s:" % self
            print "\targs", args

        newenv = Environment(['self'], [self], env)

        self.internal = True
        result = func(args, newenv)
        self.internal = False
        return result


    def __call__(self, args, env):
        """__call__ :: SchemePair -> Environment"""

        assert isinstance(first(args), LispSymbol)
        value = self.get(first(args).name)
        if callable(value):
            return self.call(value, rest(args), env)
        else :
            assert rest(args) is nil
            return value

    def scm_eval(self, env): return mksym(str(self))
    def __str__(self): return "<#class-%d#>" % self.id

class_base = LispClass(set())
