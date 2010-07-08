
Classes
====

There is no difference between a class and an instance (object). An instance is just an inherited class. Classes are simply modelled as a dictionary of variables. These variables have permissions, a data-type, and a value (or may not be set). A class acts as a special form in that it can be applied (called as a function). It's first parameter is the name of the variable to get: If it is a class function then the function gets called with any additional parameters; Otherwise it gets returned as a value.

Class Related Function and Special Forms
----

 + class           : create a class
 + class-define!   : add a variable to a class
 + class-set!      : set a class variable's values
 + class-chmod!    : set a class variable's permission
 + class-finalize! : make it so no new variables can be defined
 + new             : macro to make a new class (instance) and set its variables

Example
----

    ; ---- New Class
    (define Point (class BaseClass)
    ; ---- Declare Members
    (class-define! Point x  Int)
    (class-define! Point y  Int)
    ; ---- Declare Functions
    (class-define! Point +     (Lambda Point Point Point))
    (class-define! Point -     (Lambda Point Point Point))
    (class-define! Point str   (Lambda Str Point))
    (class-define! Point angle (Lambda Int))
    ; ---- Define Functions
    (class-set! Point +     (lambda ...))
    (class-set! Point -     (lambda ...))
    (class-set! Point str   (lambda ...))
    (class-set! Point angle (lambda ...))
    ; ---- Permissions
    (class-chmod! Point -     'read-only)
    (class-chmod! Point +     'read-only)
    (class-chmod! Point str   'read-only)
    (class-chmod! Point x 'any 'virtual)
    (class-chmod! Point x 'any 'virtual)
    ; ---- Finish
    (class-finalize! Point)

    ; ---- Create Instance
    (define p1 (class Point BaseClass))
    (class-set! Point x 1)
    (class-set! Point y 2)
    
    ; ---- Create Instance (using macro)
    (define p1 (new Point 'x 1 'y 2))

    ; ---- Calling a function / getting a variable
    (p1 add p2)  ; p1.add(p2)
    (p1 x)       ; p1.x 
    (p1 str)     ; p1.str()

Permissions of Class Variables
----

Any of the following can be true or false:

 + class-read    : in the class functions the variable can be read
 + class-write   : in the class functions the variable can be written
 + any-read      : anything can write to it
 + any-write     : anything can read from it
 + virtual       : nothing can read/write this (doesn't get inherited).

`virtual` is differnt in that it doesn't get inherited and over-rules other permission flags. If a class wants to inherit

These can be set once and never changed. Child classes initially inherit the permissions of the parents and then get one chance to set variables. (not really sure on this, hard to implement and may be useless).

If two parents have the same variable it is the first one that gets inherited.

Permissions of Classes
----

`class-finalize!` changes `class-add!` and `class-chmod!` so that new variables cannot be added and permissions can't be changed. Any class that should be inherited should (but doesn't have to) be finalized so that all child classes can be sure to have the same set of variables. Also all functions in such classes should be read-only. If this doesn't happen subclasses could change their functions and certain vectors might for instance add instead of take away.

Notes
----

 1. Type declerations are optional, that is `(class-add! Point x)` is the same as `(class-add! Point x Any)`. 

 2. Getting or calling a class variable which is not set is an error.

 3. Only the direct parents need to be specified. Grand parents can be calcluated. 

 4. A child class will inherit all variable declerations, definitions and permissions. Except for the virtual flag on permissions. 

 5. `new` will finalize a class as class instances should not be adding new variables. 


Environment
====

The environment is where all data is stored. A function call creates a child environment with the data of it's paremeters. As with classes, environment variable have a data type can can be set and have new permissions.

In some programming languages you have access to only two environments, the local one and the global one. The global one is where all globals are defined and the local one is for the current function only. 

In this programming language any parent environment can be accessed. Though child defintions shadow the ones defined in any parents. 

Because any function could change a global (such as `let` or `begin`) they have permission in the same way that classes do. 

In the same way that `class` creates a class `lambda` create a new environment. 

Although I can't see why it would be needed `finalize!` does the same as it does in classes. 

Example
----

    ; ---- declare and define an environmental variable
    (define! y Int 15)
    (assert-eq y 15)

    ; ---- set an environmental variable
    (set! y 10)
    (assert-eq y 15)

    ; ---- make a new environment (where we change y)
    ((lambda () 
        (assert-eq y 10)
        (set! y 4)))
    (assert-eq y 4)

    ; ---- new y masks the old one
    ((lambda (y) 
        (assert-eq y 5)
        (set! y 100)) 5)
    (assert-eq y 4)

    ; ---- set an environmental variable's permissions
    (chmod! y 'read-only)

Data Types
====

The following could define a new data type called Bob (all types start
with a capital letter). Bob is of type Int.

    type Bob :: Int 

The `|` operator specifies alternative types that can be taken. Here
Bill can either be an Int or a Bool.

    type Bill :: (Either Int Bool)

Sometimes a type will need another type as a parameter like so. Ben is
a list of Int's. 

    type Ben :: (List Int)

Tuple i.e. taking more than one value:

    type Ben :: (Tuple Int Bool)

This means Ben is an Int followed by a bool

Treating a lambda like any other syntax it must take two types one for
the return the other for the parameters (this must be a tuple). 

    type Jim :: (Lambda Bool (Tuple Int Int))

Dotted syntax could be like so

    type Mat :: (Lambda Bool Int)

Mat takes any number of Ints

    type Tim :: (Lambda Bool (Tuple Int Float) Any)

Tim takes an int float and any number of Anything.

----

Types can be stored in the env. hence can be looked up. 

    (define-typed 
        Type 
        Func-Bool-Int-Int 
        (Type Lambda Bool (Int, Int)))

    (define-typed 
        Func-Bool-Int-Int 
        greater-than 
        (lambda (x y) (> x y)))


Debugging
====

For debugging it would be great to have lambdas store (or lookup)
their defined name in the env. 

For debugging viewing the historic call stack as well as stack frames would be
all that is required to be awesome.

main
-- <#built-in#> 'define' (name='bob', val='15')
-- <#lambda#> 'fred' (...)
-- -- <#lambda#> 'list' (...)



-------------------------------------------


    class Variable
        var permission : Permission
        var type       : Optional Type
        var value      : Optional LispBase

    class LispClass :: LispBase
        private var parents   :: Set LispClass
        private var variables :: Dict Str Variable

        func __init__ 
        func __call__ 
        func __str__
        func scm_eval

        func chmod  :: Str 'var' -> [Str] 'flags' -> None
        func define :: Str 'var' -> Type 'type' -> None
        func set    :: Str 'var' -> LispBase 'value' -> None
        func get    :: Str 'var' -> LispBase
        func call   :: Str 'var' -> LispPair 'args' -> LispBase
