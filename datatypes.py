debug = False

# ----------------------------------------------------------------------------

class LispBase(object):
    pass
    
# ----------------------------------------------------------------------------

class LispNil(LispBase):
    def __init__(self): pass
    def scm_eval(self, env): return self
    def __str__(self): return "nil"
    def __eq__(self, other): return self is other

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

    def __eq__(self, other): 
        return self is other

obarray = {}

def mksym(name):
    """mysym :: Str 'name' -> Symbol"""
    assert isinstance(name, str)
    # assert valid_symbol_name(name), "invalid atom in symbol %s" % name
    if name not in obarray:
        obarray[name] = LispSymbol(name)
    return obarray[name]

# ----------------------------------------------------------------------------

call_stack = []

class LispPair(LispBase):
    def __init__(self, first, rest):
        self.first = first
        self.rest = rest
    
    def scm_eval(self, env):
        func = self.first.scm_eval(env)
        assert callable(func), "cannot call '%s' in %s" % (func, self)
        call_stack.append(func)
        result = func(self.rest, env)
        call_stack.pop()
        return result

    def __str__(self):
        text = "( "
        sexp = self
        while (isinstance(sexp, LispPair)):
            text += str(sexp.first) + " "
            sexp = sexp.rest
        
        if sexp is not nil:
            text += ". " + str(sexp) + " "
        text += ")"
        return text

    def __eq__(self, other):
        if not isinstance(other, LispPair):
            return False

        return self.first == other.first and self.rest == other.rest

def get_stack():
    return from_list(call_stack)

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

    lambda_id = 0

    def __init__(self, scm_vars, body, macro=False):
        """Procedure :: SchemeBase -> LispPair"""

        LispLambda.lambda_id += 1
        self.id = LispLambda.lambda_id

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
            if debug: print "\tmacro\t", mac
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
        return mksym(str(self))

    def __str__(self):
        return "<#procedure-%d#>" % self.id

    def __eq__(self, other):
        if not isinstance(other, LispLambda):
            return False
        return self is other

# ----------------------------------------------------------------------------

class LispBool(LispBase):
    def __init__(self, val): 
        assert (val is True) or (val is False)
        self.val = val
    def scm_eval(self, env): return self
    def __str__(self): return str(self.val).lower()

    def __eq__(self, other):
        return self is other

true = LispBool(True)
false = LispBool(False)

# ----------------------------------------------------------------------------

class LispString(LispBase):
    def __init__(self, text):
        assert isinstance(text, str)
        self.text = text
    def scm_eval(self, env): return self
    def __str__(self): return '"%s"' % self.text
    def __eq__(self, other): 
        if not isinstance(other, LispString):
            return False
        return self.text == other.text

# ----------------------------------------------------------------------------

class LispInteger(LispBase):
    def __init__(self, num):
        assert isinstance(num, int)
        self.num = num
    def scm_eval(self, env): return self
    def __str__(self): return str(self.num)
    def __cmp__(self, other): 
        if not isinstance(other, LispInteger):
            return False
        return cmp(self.num,other.num)

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

    def copy(self):
        perm = Permission()
        perm.class_read  = self.class_read 
        perm.class_write = self.class_write
        perm.any_read    = self.any_read   
        perm.any_write   = self.any_write  
        perm.virtual     = self.virtual    
        return perm

class Variable(object):
    def __init__(self, permission, datatype=None, value=None):
        self.permission = permission
        self.datatype = datatype
        self.value = value

    def __str__(self):
        return str(self.value)

    def copy(self):
        return Variable(self.permission.copy(),
                        self.datatype,
                        self.value)

class MissingSym(Exception): pass
class AlreadyDefined(Exception): pass
class InvalidPermission(Exception): pass

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
                self.variables[p] = v.copy()
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
        if self.finalised: raise InvalidPermission("finalised:" + var)
        if var in self.variables: raise AlreadyDefined(var)

        # give the default permission and no value
        permission = Permission()
        variable = Variable(permission, datatype, value)
        self.variables[var] = variable

    def set(self, var, value):
        # set :: Str 'var' -> LispBase 'value' -> None
        if var not in self.variables: raise MissingSym(var)

        # check permissions
        permissions = self.variables[var].permission
        if permissions.virtual: raise InvalidPermission(var)
        if not permissions.any_write:
            if not (self.internal and permissions.class_write):
                raise InvalidPermission(var)
        

        # todo: check datatypes match
        self.variables[var].value = value

    def get(self, var):
        # get :: Str 'var' -> LispBase
        if var not in self.variables: raise MissingSym(var)

        # check permissions
        permissions = self.variables[var].permission
        if permissions.virtual: raise InvalidPermission(var)
        if not permissions.any_read:
            if not (self.internal and permissions.class_read):
                raise InvalidPermission(var)

        value = self.variables[var].value
        assert value is not None, "%s not set" % var
        return value

    def chmod(self, var, flags):
        # chmod  :: Str 'var' -> [Str] 'flags' -> None
        if self.finalised: raise InvalidPermission("finalised:" + var)
        if var not in self.variables: raise MissingSym(var)
        # todo: should only those with write permission be able to set this?
        self.variables[var].permission.set_flags(flags)

    def call(self, func, args, env):
        # call :: LispBase 'func' -> LispPair 'args' -> LispBase

        # note: could remove these hacks!
        # 
        # They are hack because:
        # 
        #   1. If the func is somehow called from somewhere other than here
        #      it wont have self set or worse will use one from another class!
        #   2. internal set's it for the duration of the function call. if
        #      anything else is call it too has priveladed access. I guess 
        #      this is consistent with how the Env accesses stuff but I think 
        #      it is wrong for classes. 
        # 
        # Actually maybe it's not that bad. (1) can only happen if it get used 
        # in the wrong way. (2) is consistent with the rest of the language.

        if debug:
            print "call-class %s:" % self
            print "\targs", args

        newenv = Environment(['self'], [self], env)

        try:
            self.internal = True
            result = func(args, newenv)
        finally:
            self.internal = False
        return result


    def __call__(self, args, env):
        """__call__ :: SchemePair -> Environment"""

        assert isinstance(first(args), LispSymbol)
        value = self.get(first(args).name)
        if callable(value):
            return self.call(value, rest(args), env)
        else:
            assert rest(args) is nil
            return value

    def scm_eval(self, env): return mksym(str(self))
    def __str__(self): return "<#class-%d#>" % self.id
    def __eq__(self, other): return self is other

class_base = LispClass(set())


# ----------------------------------------------------------------------------

class Environment(LispClass):
    """Binds symbols to values. Seperate frame can mean bindings can 
    shadow others. You cannot re-bind something in the same frame though
    you can set it to something else."""

    def __init__(self, syms, vals, parent):
        # init :: [Str] -> [LispBase] -> Optional Environment -> Environment

        # Environment have no parent classes, 
        # they don't need to inherit anything!
        super( Environment, self ).__init__([])


        # we could have parent as a mamember of Environment directly rather
        # than through self.variables but this way we can if we want expose it
        # to Lisp as a class.

        if parent:
            assert(isinstance(parent, Environment))
            super(Environment, self).define("__parent__", None, parent)
            super(Environment, self).chmod("__parent__", 
                                           ["no-class-read", "no-class-write",
                                            "no-any-read", "no-any-write"])

        for sym, val in zip(syms, vals):
            assert(isinstance(sym, str))
            # todo: this could be usefull but not for testing
            # or adding primative functions (which are not LispBase)
            # assert(isinstance(val, LispBase))
            super(Environment, self).define(sym, None, val)

    def parent(self):
        if "__parent__" in self.variables:
            return self.variables["__parent__"].value
        else:
            return None

    def get(self, var):
        # func get :: Str 'var' -> LispBase
        if var in self.variables:
            return super(Environment, self).get(var)
        elif self.parent() is None:
            raise MissingSym(var)
        else:
            return self.parent().get(var)

    def set(self, var, val):
        # func set :: Str 'var' -> LispBase 'val' -> None
        if var in self.variables:
            return super(Environment, self).set(var, val)
        elif self.parent() is None:
            raise MissingSym(var)
        else:
            return self.parent().set(var, val)

    def chmod(self, var, flags):
        # func chmod :: Str 'var' -> [Str] 'flags' -> None
        if var in self.variables:
            return super(Environment, self).chmod(var, flags)
        elif self.parent() is None:
            raise MissingSym(var)
        else:
            return self.parent().chmod(var, flags)

    def __str__(self):
        # func __str__ :: None -> Str
        ret = "PRINT ENV\n"
        for sym, val in self.variables.items():
            if sym != "__parent__":
                ret += sym + " = " + str(val) + "\n"
        ret += "---\n"
        if self.parent() is not None:
            ret += str(self.parent())
        else:
            ret += "===\n"
        
        return ret




#------------------------------u------------------------------------------------

def test():
    topenv = Environment(["a","b","c"],[1, 2, 3], None)

    def test1():
        topenv = Environment(["a","b","c"], [1, 2, 3], None)
        assert(topenv.get("a") == 1)
        assert(topenv.get("b") == 2)
        assert(topenv.get("c") == 3)

    def test2():
        newenv = Environment([], [], topenv)
        assert(newenv.get("a") == 1)
        assert(newenv.get("b") == 2)
        assert(newenv.get("c") == 3)

    def test3():
        newenv = Environment(["x"],[7], topenv)
        assert(newenv.get("x") == 7)
        assert(newenv.get("a") == 1)
        assert(newenv.get("b") == 2)
        assert(newenv.get("c") == 3)

    def test4():
        newenv = Environment([], [], topenv)
        newenv.define("x", None, 7)
        assert(newenv.get("x") == 7)
        newenv.set("x", 99)
        assert(newenv.get("x") == 99)

    def test5():
        try:
            newenv = Environment([], [], topenv)
            newenv.define("x", None, 7)
            newenv.define("x", None, 7)
            raise Exception("an error should have been thrown")
        except AlreadyDefined:
            pass

    def test6():
        try:
            newenv = Environment([], [], topenv)
            newenv.get("notdefined")
            raise Exception("an error should have been thrown")
        except MissingSym:
            pass

    def test7():
        try:
            newenv = Environment([], [], topenv)
            newenv.set("x", 7)
            raise Exception("an error should have been thrown")
        except MissingSym:
            pass

    test1()
    test2()
    test3()
    test4()
    test5()
    test6()
    test7()

# test()

