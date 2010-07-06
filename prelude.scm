
(define (not x) (if x false true))

(define (null obj) (is obj nil))

(define (id x) x)

(define (flip f) (lambda(x y) f y x))

(define (list . x) x)

(define (curry f x) (lambda(y) (apply f (cons x y))))

(define (compose f g) (lambda(x) f (apply g x)))

(define (foldr f x xs)
  (if (null xs)
    x
    (f
      (car xs)
      (foldr f x (cdr xs)))))

(define (foldl f x xs)
  (if (null xs)
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

(define (pick f) (lambda(x y) if (f x y) x y))

(define zero              (curry = 0))

(define positive          (curry < 0))

(define negative          (curry > 0))

(define (odd num)         (= (mod num 2) 1))

(define (even num)        (= (mod num 2) 0))

(define assert
  (lambda(m x y)
    (if (= x y)
        true
        (display (cons m (cons x y))))))

(define concat
  (lambda(x y)
    (foldr
     (lambda(a b)(cons a b))
     y
     x)))


(display (concat '(1 2 3) '(4 5 6)))

(define (length lst)
  (foldr (lambda (a b) (+ 1 b)) 0 lst))


;; (display (length '()))
;; (display (length '(a)))
;; (display (length '(a b)))
              

;; (define (mac and . args)
;;   (if (is nil args)
;;       true
;;       (if (is nil (cdr args))
;;           (eval (car args))
;;           (if (eval (car args)
;;                     (and (cdr args)))))))

(define when   (mac (<cond>.<body>) (list 'if <cond> (cons 'begin <body>))))
(define unless (mac (<cond>.<body>) (list 'if <cond> nil (cons 'begin <body>))))

(unless true 'wont-be-called)
(when false 'wont-be-called)

(unless false 'will-be-called)
(when true 'will-be-called)

(display "----a------")

;; (class-set-many! p1 '(x 1 y 2))
(define (class-set-many! name things)
  (unless (is things nil)
      (class-set! name (car things) (car (cdr things)))
      (class-set-many! name (cdr (cdr things)))))

;; (new p1 point x 1 y 2)
(define new (mac (<name> <parent> . <data>)
                 `(begin
                    (define ,<name> (class (,<parent>) nil nil))
                    (class-set-many! ,<name> ',<data>))))



(define point (class (class-base) (x y) (str thing)))
(class-set! point 'str (lambda(self) (display (list (p1 x) " " (p1 y)))))
(new p1 point x 123 y 456)              ; nil 
((point str) p1)                        ; ( 123 " " 456 )


(display "-------------------------------------------------------------------")

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

(display (gather-args '((a1 v1) (a2 v2))))

;; let is a lambda whixch is called instantly
;; 
;; (let ((x 2) (y 3))(* x y)) --> ((lambda (x y) (* x y)) 2 3)
;;  
;; (let ((a1 v1) (a2 v2) ... ) b1 ...)
;; ((lambda (a1 a2 ...) b1 ...)) v1 v2 ...)

(define let (mac (<bindings> <body>)
                 ;; (car (gather-args <bindings>)) ;; a's
                 ;; (cdr (gather-args <bindings>)) ;; v's
                 (cons (list 'lambda (car (gather-args <bindings>))
                       <body>)
                       (cdr (gather-args <bindings>)))))

(let ((a 1) (b 2)) (begin (display a) (display b)))

(display "-------------------------------------------------------------------")

