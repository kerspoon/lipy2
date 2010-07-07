LiPi - Lisp in Python
====

I have been developing *LiPi* to teach me various programming concepts. It is a small lisp/scheme like programming language made in python.

It has a small test suite but only test for success at the moment. Nothing of special interest, I have tried to keep the code clean-ish but I have been playing with more complex python so the results of my efforts might have resulted in overly complex sections. It used to use CPS to help tail call optimisiation and give call/cc but I changed it all back to make the code neater.

This is my 5th lisp implementation, the previous ones have been in C++, D, D again, and a previous version in Python.

I have just addded basic classes, these are unusual (for me) in that there is no difference between a class and an object. It's all crazy dynamic. 

Long Term Goal
=============

I would like a type-checked, objected-orientated lisp with a good module system and simple macros. If I was to ever used it for real coding I would need good error messages, a large library and integration with emacs at the least but as that will take forever I intend to focus on the interesting rather than the practicle. It is mearly a proof of concept. 

Main Goals
----

 + Objected Orientated 
 + Type Checked
 + Good Module System (import include etc.)
 + Simple Macros (as per arc-lisp)

Side Goals
----

 - Deal with errors better (see how plt-racket does things)
 - Add more built in functions and macros (looks at r5rs and python)
 - Emacs integration

Structure
====

 + *lex* - tokenise a string into a list of string tokens
 + *parse* - convert tokens into datatypes
 + *datatypes* - all the data in scheme is of one of these types
 + *environment* - anything defined in lipy get stored in an environment
 + *function* - all built in lipy function calls (including special forms) as well as the default environment
 + *main* - tests and misc
 + *prelude* - some default scheme functions taken from Haskell

2-min Tutorial (for those that known lisp)
====

1. Open `main.py` and make sure the tests are working.
2. Write something in `main().inp`, make sure it's running, and see the result.
3. Setting `datatypes.debug = True` is about as far as debugging as it gets

Special Forms
----

`function.py` defines all the special forms (there is only a few). Their descriptions should help, or look at the tests. In addition to the ones set in `function.py` any data types can dynamically create special forms. 

There are currently only two DataTypes that do this: 

 1. LispLambda is obviously the normal form of apply. It evaluares all the arguments and calls the closure with the environment that has bound the newly evaluated arguments. if it is created as a macro then it doesn't eval the args but evals the body in a new frame, it then evals the result in the old frame. 

 2. LispClass turns each class into a special form that looks up the specified name in the classes slots.

It is possible to make a new data-type that does anything when instance of it are called. The only caveat is that there is no distinction between compile time, macro time and run time as there is in other implementations. Everything is done when called. But as the call mechanism as described is so dynamic it *should* be able to cope. In fact the only thing needed to create simple macros (other than make quasiquote etc.) is to not evaluate the arguments before a lambda is called. 


Adding a data-type
----

There is no eval or apply function. Each data-type deals with these seperatly. Hence here are 3 things a new datatypes should have:

    __str__  :: None -> Str
    __call__ :: LispPair 'args' -> Environment 'env' -> LispBase
    scm_eval :: Environment 'env' -> LispBase

To add a new datatype in addition to making it as above it should be included in the `lexer` & `parser` as well as defining the function that create and mainpulate it in `function.py`.

Classes
----

Classes are simple stored as three parameters:

 + parents - a list of classes with all parents (including grandparents etc.)
 + parameters - the things that can be set in this class (inherited from all parents)
 + slots - things that cannot be set in this class but become parameters of child-classes.

To create a class you do the following:
                                                                            
    (define point (class (class-base) (x y) (length total thing)))          
    (class-set! point length 2)                                             
    (class-set! point total (lambda (self) (+ (self _x) (self _y))))        
    (class-set! point thing (lambda (self mm) (+ mm ((self total) self))))  

This makes an abstract class (because it has 2 slots (x & y)) with 3 parameters (length, total & thing). These parameters are initially nil but then are set of the following lines. Note how there is no distinction between data and a function but that functions must take the class as its first parameter (here called self). 

To make an instance of the class all you do is make a new class that has no new slots. 

    (define p1 (class (point) () ()))

Because it has no slots the functions can be called as follows:

    (class-set! p1 _x 4)
    (class-set! p1 _y 6)
    (p1 _x)
    (p1 _y)
    ((p1 total) p1)

Note how calling a function you must use the class(instance) name twice -- this is messy and should change. 

In the child class that was defined there are now 5 parameters and no slots. Any of the parameters can be changed including functions but it doesn't change it for the base class or indeed other derived points hence calling the folling two may give completly different results even if they are both a subclass of `point`:

    ((p1 sum) p1 p2)
    ((p2 sum) p1 p2)


To Do
=====

1. Data-types should own their own functions. Move the maths into
LispInteger. Have function.py do all the type checking. 

1. It would be nice to make classes a bit less dynamic. Maybe something like 

    (class-final point length)  

means that the point.length cannot be changed in this or in any subclasses created after it was set.

1. Think about a import function that create a (finalised) class containing all the functions of that file.

1. The syntax for call a class function classes is messy. Dot syntax would be great ;)


Links
====

http://hyperpolyglot.wikidot.com/lisp
http://people.csail.mit.edu/jaffer/r5rs_toc.html
