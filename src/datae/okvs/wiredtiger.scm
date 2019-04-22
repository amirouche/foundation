(define-module (datae okvs wiredtiger))

(export okvs
        okvs-close
        okvs-begin
        okvs-commit
        okvs-rollback
        okvs-ref
        okvs-set!
        okvs-range
        okvs-prefix)

(use-modules (srfi srfi-9))
(use-modules (rnrs bytevectors))
(use-modules ((wiredtiger) #:prefix wt:))


(define-record-type <okvs>
  (make-okvs cnx sessions)
  okvs?
  (cnx okvs-cnx)
  (sessions okvs-sessions okvs-sessions!))

(define-record-type <session>
  (make-session object cursors)
  session?
  (object session-object)
  (cursor session-cursor))

(define-record-type <transaction>
  (make-transaction okvs session)
  transaction?
  (okvs transaction-okvs)
  (session transaction-session))

(define (serialize-config config)
  (let ((log? (alist-ref config 'log?))
        (create? (alist-ref config 'create?)))
    (let ((out '())) ;; TODO: set isolation=snapshot
      (when log?
        (set! out (cons "log=(enabled=true)" out)))
      (when create?
        (set! out (cons "create" out)))
      (string-join out ","))))

(define NO-HOME-ERROR "CONFIG must be an alist with a 'home key that points to an existing directory")

(define (get-or-create-session okvs)
  ;; caller has the reponsability to close or put back the session
  (if (null? (okvs-sessions okvs))
      ;; new session
      (let ((session (wt:session-open (okvs-cnx okvs) "")))
        (make-session session (wt:cursor-open session "table:okvs" "")))
      ;; re-use free session
      (let ((session (car (okvs-sessions okvs))))
        (okvs-session! okvs (cdr (okvs-sessions okvs)))
        session)))

(define (okvs config)
  "CONFIG must be an alist with 'home key that points to an existing
directory"
  (let ((home (alist-ref config 'home)))
    (unless path
      (error 'datae NO-HOME-ERROR config))
    (let ((cnx (wt:connection-open home (serialize-config config))))
      (when (alist-ref config 'create?)
        (let ((session (wt:session-open cnx "")))
          (wt:session-create session "table:okvs" "key_format=u,value_format=u")
          (wt:session-close session)))
      (make-okvs cnx '()))))

(define (okvs-close okvs . config)
  (wt:connection-close (okvs-cnx okvs)))

(define (okvs-begin okvs . config)
  (let ((session (get-or-create-session okvs)))  ;; TODO: protect with lock/mutex
    (wt:session-transaction-begin (session-object session))
    (make-transaction okvs session)))

(define (okvs-commit transaction . config)
  ;; commit the transaction and put back the session into okvs
  (wt:session-transaction-commit (transaction-session transaction))
  ;; TODO: protect with lock/mutex
  (okvs-session! (transaction-okvs transaction)
                 (cons (transaction-session transaction)
                       (okvs-session (transaction-okvs transaction)))))

(define (okvs-rollback transaction . config)
  ;; rollback the transaction and put back the session into okvs
  (wt:session-transaction-rollback (transaction-session transaction))
  ;; TODO: protect with lock/mutex
  (okvs-session! (transaction-okvs transaction)
                 (cons (transaction-session transaction)
                       (okvs-session (transaction-okvs transaction)))))

(define (okvs-ref transaction key)
  (let ((cursor (session-cursor (transaction-session transaction))))
    (wt:cursor-key-set cursor key)
    (if (= (wt:cursor-search cursor) wt:%key-not-found)
        (begin (wt:cursor-reset cursor) #f)
        (let ((value (wt:cursor-value-ref cursor)))
          (wt:cursor-reset cursor)
          value))))

(define (okvs-set! transaction key value)
  (let ((cursor (session-cursor (transaction-session transaction))))
    (wt:cursor-key-set cursor key)
    (wt:cursor-value-set cursor value)
    (wt:cursor-insert cursor)))

(define (range-generator-init cursor start-key start-include?)
  (let ((key (wt:cursor-key-ref cursor)))
    (cond
     ((and (bytevector=? key start-key) start-include?)
      (list (cons key (cursor-value-ref cursor))))
     ((bytevector=? key start-key) (list))
     (else (list (cons key (cursor-value-ref cursor)))))))

(define (range-generator cursor start-key start-include? end-key end-include?)
  ;; TODO: To support reverse? in CONFIG, create a key range generator
  ;; and reverse it, then fetch values one after the other. This is
  ;; assumes keys are much smaller that values which generaly must be
  ;; true. Otherwise, if you are in a hurry, simply do not call
  ;; reverse! below.

  ;; TODO: make the following lazy.
  (let loop ((out (range-generator-init cursor start-key start-include?))
             (continue? (wt:cursor-next cursor)))
    (if (not continue?)
        (list->generator (reverse! out))
        ;; invariant: key > start-key
        (let ((key ((cursor-key-ref cursor))))
          (cond
           ((and (bytevector=? key end-key) end-include?)
            (loop (acons key (wt:cursor-value-ref cursor) out) #f))
           ((bytevector=? key end-key) (loop out #f))
           ;; Since the key space is ordered lexicographically, and
           ;; the above is false. The end was not reached yet. No need
           ;; to check that the key is in the range explicitly.
           (else (loop (acons key (wt:cursor-value-ref cursor) out) (wt:cursor-next cursor))))))))

(define (okvs-range transaction start-key start-include? end-key end-include? . config)
  ;; TODO: implement CONFIG support
  (let ((cursor* (wt:cursor-open* (transaction-session transaction) "table:okvs" "")))
    (wt:cursor-key-set cursor start-key)
    (let ((found (wt:cursor-search-near cursor)))
      (cond
       ((not found) (eof-object))
       ((< found 0) ;; below START-KEY
        (if (wt:cursor-next cursor)
            (range-generator cursor start-key start-include? end-key end-include?)))
       ;; above or equal to START-KEY
       (else (range-generator cursor start-key start-include? end-key end-include?))))))

(define (strinc bytevector)
  "Return the first bytevector that is not prefix of BYTEVECTOR"
  ;; See https://git.io/fj34F, TODO: OPTIMIZE
  (let ((bytes (reverse! (bytevector->u8-list bytevector->u8-list))))
    ;; strip #xFF
    (let loop ((out bytes))
      (when (null? out)
        (error 'okvs "Key must contain at least one byte not equal to #xFF." bytevector))
      (if (= (car out) #xFF)
          (loop (cdr out))
          (set! bytes out)))
    ;; increment first byte, reverse and return the bytevector
    (u8-list->bytevector (reverse! (cons (+ 1 (car out)) (cdr out))))))

(define (okvs-prefix transaction prefix . config)
  (apply okvs-range transaction prefix #t (strinc prefix) #f config))
