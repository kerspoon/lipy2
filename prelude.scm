
(display "----common----------------------------------------------------------")

(define (list . x) x)

(define when   (mac (<cond>.<body>) (list 'if <cond> (cons 'begin <body>))))
(define unless (mac (<cond>.<body>) (list 'if <cond> nil
                                          (cons 'begin <body>))))

(define (assert-eq a b)
  (unless (equal? a b)
          (display (list "ERROR: assert-eq" a b))))

(define (not x) (if x false true))
(define (null? obj) (is? obj nil))
(define (id x) x)
(define (flip f) (lambda(x y) (f y x)))

(define (foldr f x xs)
  (if (null? xs)
    x
    (f
      (car xs)
      (foldr f x (cdr xs)))))

(define (foldl f x xs)
  (if (null? xs)
    x
    (foldl
      f
      (f x (car xs))
      (cdr xs))))

(define (unfold func init pred)
  (if (pred init)
      (cons init '())
      (cons init (unfold func (func init) pred))))


(define fold foldl)
(define (inject x f xs)  (foldl f x xs))
(define (reduce f xs)    (foldl f (car xs) (cdr xs)))


(define concat
  (lambda(x y)
    (foldr
     (lambda(a b)(cons a b))
     y
     x)))

(define (length lst)
  (foldr (lambda (a b) (+ 1 b)) 0 lst))
              

(display "----assert-eq-------------------------------------------------------")

(assert-eq (unless true 'wont-be-called) nil)
(assert-eq (when false 'wont-be-called) nil)
(assert-eq (unless false 'will-be-called) 'will-be-called)
(assert-eq (when true 'will-be-called) 'will-be-called)
(assert-eq (not false) true)
(assert-eq (not true) false)
(assert-eq (null? nil) true)
(assert-eq (null? 5) false)
(assert-eq (null? 'nil) true)
(assert-eq (null? '(a b)) false)

(display "-----let-forms-----------------------------------------------------")

(define (gather-args args)
  ;; take argument in the form (a1 v1) (a2 v2) ...
  ;; change them to the form (a1 a2 ...) (v1 v2 ...)
  (foldr
   (lambda (x xs)
     (cons
      (cons (car x) (car xs))   ; first part is the a's
      (cons (car (cdr x)) (cdr xs)))) ; first part is the v's
   '(nil . nil)
   args))

(assert-eq (gather-args '((a1 v1) (a2 v2))) '((a1 a2) v1 v2))

;; (let ((x 2) (y 3))(* x y)) --> ((lambda (x y) (* x y)) 2 3)
(define let (mac (<bindings> <body>)
                 ;; (let ((a1 v1) (a2 v2) ... ) b1 ...)
                 ;; ((lambda (a1 a2 ...) b1 ...)) v1 v2 ...)
                 ;; (car (gather-args <bindings>)) ;; a's
                 ;; (cdr (gather-args <bindings>)) ;; v's
                 (cons (list 'lambda (car (gather-args <bindings>))
                       <body>)
                       (cdr (gather-args <bindings>)))))

(assert-eq (let ((a 3) (b 2)) (* a b)) 6)

(display "----class-new------------------------------------------------------")

;; (class-set-many! p1 '(x 1 y 2))
(define (class-set-many! name things)
  (unless (is things nil)
      (class-set! name (car things) (car (cdr things)))
      (class-set-many! name (cdr (cdr things)))))

;; (new p1 point x 1 y 2)
(define new (mac (<name> <parent> . <data>)
                 `(begin
                    (define ,<name> (class ,<parent>))
                    (class-set-many! ,<name> ',<data>))))

(display "----test-class-----------------------------------------------------")


;; ---- New Class
(define Point (class BaseClass))
;; ---- Declare Members
(class-define! Point 'x  Int)
(class-define! Point 'y  Int)
;; ---- Declare Functions
(class-define! Point '+     (Lambda Point Point))
(class-define! Point 'str   (Lambda Str None))
(class-define! Point 'total (Lambda Int None))
;; ---- Define Functions
(class-set! Point '+     (lambda (other) (new tmp Point
                                        'x (+ (self x) (other x))
                                        'y (+ (self y) (other y))) tmp))
(class-set! Point 'str   (lambda () (list (self x) (self y))))
(class-set! Point 'total (lambda () (+ (self x) (self y))))
;; ---- Permissions
(class-chmod! Point '+   'read-only)
(class-chmod! Point 'str 'read-only)
(class-chmod! Point 'x   'virtual)
(class-chmod! Point 'y   'virtual)
;; ---- Finish
(class-finalize! Point)

;; ---- Create Instance
(display "here")
(define p1 (class Point BaseClass))
(class-set! p1 'x 1)
(class-set! p1 'y 2)
  
;; ---- Create Instance (using macro)
;; todo: fix broken `new` macro
;; (new p2 Point 'x 1 'y 2)

(define p2 (class Point BaseClass))
(class-set! p2 'x 10)
(class-set! p2 'y 20)

;; ---- Calling a function / getting a variable
; ((p1 + p2) str) ; p1.add(p2).str()
;; (p1 x)   ; p1.x

(assert-eq (p1 str) '(1 2))
(assert-eq (p2 str) '(10 20))
 



(display "---------------------------------------------------------------")
(display "-------------------------AAAAAAAAAAAAAAA-----------------------")
(display "---------------------------------------------------------------")

;; (display "---------------------------------------------------------------")
;; (display "-------------------------BBBBBBBBBBBBBBB-----------------------")
;; (display "---------------------------------------------------------------")


;; (display "---------------------------------------------------------------")
;; (display "-------------------------CCCCCCCCCCCCCCC-----------------------")
;; (display "---------------------------------------------------------------")


;; (display "---------------------------------------------------------------")
;; (display "-------------------------DDDDDDDDDDDDDDD-----------------------")
;; (display "---------------------------------------------------------------")
