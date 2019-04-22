# datae: an application of versioned quadstore

![data](https://raw.githubusercontent.com/awesome-data-distribution/datae/master/data.jpg)

## Author

Amirouche Boubekki

## Abstract

datae is web application that is (mostly) implemented with Scheme
programming language. It is supported by an versioned database that is
a quadstore versioned in a direct-acyclic-graph. It is possible to do
queries at any point in history while still being efficient to do
queries and modify the latest version of the data when snapshots are
used. The versioned quadstore is implemented using a novel approach
dubbed generic tuple store. datae application goal is to demonstrate
that versioned databases allow to implement workflows that ease
cooperation.

## Keywords

- data management system
- data science
- distributed version control system
- knowledge base
- open data
- quality assurance
- reproducible science
- scheme programming language

## Introduction

Versioning in production systems is a trick everybody knows about
whether it is through backup, logging systems and ad-hoc audit
trails. It allows to inspect, debug and in worst cases rollback to
previous states. There is not need to explain the great importance of
versioning in software management as tools like mercurial, git and
fossil have shaped modern computing. Having the power of multiple
branch versioning open the door to manyfold applications. It allows to
implement a mechanic similar to gitlab's merge requests in any
domains. That very mechanic is explicit about the actual human
workflow in entreprise settings in particular when seniors validate
changes by less senior persons.

The versioned quadstore make the implementation of such mechanics more
systematic and less error prone as the implementation can be shared
across various tools and organisations.

The use of a version control system to store open data is a good thing
as it draws a clear path for reproducible science. But none, meets all
the expectations. datae aims to replace the use of git and make
practical cooperation around the creation, publication, storage,
re-use and maintenance of knowledge bases that are possibly bigger
than memory.

Resource Description Framework (RDF) offers a good canvas for
cooperation around open data but there is no solution that is good
enough. [1] (TODO: explain what are those features required for cooperation
and why those features are important.) (TODO: cite an article about the
importance of git and git hosting solutions in the context of software
development). datae use a novel approach to query versioned data based
on a topological graph ordering of changes. datae only stores changes
between versions. datae does not rely on the Theory of Patches
introduced by Darcs but re-use some its vocabulary. datae use
WiredTiger database storage engine, an ordered key-value store, to
deliver a pragmatic ACID-compliant versioned quadstore.

[1]

The first part will present some background knowledge, the second part
will describe the implementation, the next part will present
benchmarks and at last we will conclude with summary of the work and
what remains to be explored.

## Background

### Resource Description Framework

#### Linked Data

#### Tripe and Quad Store

#### SPARQL

### Version Control System

#### git, mercurial and fossil

#### Wikibase and Wikidata

### Ordered Key-Value Store

Key-value stores offers a rather high level primitive to build high
performance, multi-model and domain specific databases. The common
denominator of key-value stores is that they are mappings of bytes
where keys are always in the lexicographic order. Even if they do not
all expose a cursor interface, they certainly allow movements inside
the mapping or prefix range queries (also known as slices).

Nowdays there is numerous libraries offering a similar interface among
them there is FoundationDB. Similar software include Tokyo Cabinet,
Kyoto Cabinet, LMDB, LevelDB and RocksDB. They offer different
trade-offs and features.  datae use WiredTiger because it is not a bad
choice. It performs well on some benchmarks [2]. It takes in charge
the difficult matter of guaranting Atomicity, Consistency, Isolation
and Durability (ACID) and also handle in-memory caching.  WiredTiger
is the component that allows to build a durable version control system
for bigger than memory datasets.

[2] http://www.lmdb.tech/bench/ondisk/

### Scheme Programming Language

According to Wikipedia:

> Scheme is a programming language that supports multiple paradigms,
> including functional and imperative programming. It is one of the
> three main dialects of Lisp, alongside Common Lisp and
> Clojure. Unlike Common Lisp, Scheme follows a minimalist design
> philosophy, specifying a small standard core with powerful tools for
> language extension.

High-level languages like Scheme are not the prefered tools to build
database abstraction, so far. That said, some had success with Java,
Go and Clojure [3]. With the advent of ordered key-value stores the
situation is different. Key-value stores solve the performance
problems while Scheme allows to express quickly high level
abstractions that fit exactly the domain problem.

[3] https://docs.datomic.com/

Chez Scheme is (prolly) the fatest Scheme implementation [4] and in
particular it is faster than Racket [5]. Which makes Chez probably the
fastest dynamic language in the known Universe. Scheme community has
good scientifical culture. It has been the inspiration that allowed
datae to take the current form.

[4] https://ecraven.github.io/r7rs-benchmarks/
[5] https://benchmarksgame-team.pages.debian.net/benchmarksgame/faster/racket-python3.html

## Implementation

In the spirit of Scheme programming language, datae try to solve the
problem using a minimalist core of powerful primitives upon which one
can build abstractions to solve bigger problems. The generic tuple
store is such an abstraction. It allows to take advantage of
WiredTiger without scarifying expressiveness. Generic Tuple Store is a
set of procedures that generalize triple and quad store respectively
3-tuples and 4-tuples to n-tuples. In turn, it allows to share code to
implement the versioned database to represent its components:

- The repository metadata as a 3-tuple store,
- the versioned quads as a 6-tuple store,
- and the 4-tuple stores that are snapshots of branches

That section is split into four parts. The first part is a tentative
formalisation of the problem of finding a smallest table set that
allows to bind any pattern in one hop to implement the generic tuple
store. The third part will dive into the specifics of the
implementation of versioned 4-tuples using the generic store and how
the concept of history significance makes querying versioned tuples in
a direct-acyclic-graph algorithmically less complex. The fourth and
last part of this section explain how to model various datastructures
in terms of quads to take advantage of versioning.

### Generic Tuple Store

The literature seems to be void from attempts to build tuple stores
based on Ordered Key-Value store. Even if similar work exsists like
hexastore they don't try to generalize the concept of triple and quad
store so that it possible to create a database that can host tuple of
n items where n is bigger than 3.

Given a 4-tuple store:

```scheme
(define store (nstore engine '(collection uid key value)))
```

We need to bind any pattern in one hop. That is for instance the
following query:

```
(select (from 'blog (var 'uid) 'title (var 'title)))
```

Will return:

```scheme
((uid . P4X432) (title . "hyper.dev"))
```

It is possible to do that with a single query using and an index that is:

```scheme
(collection key uid value)
```

But the following index is also valid:

```scheme
(collection key value uid)
```

We could consider every permutation of the `(collection uid key
value)` tuple as indices but it counts as 24 indices which would
translate into 24 times the size of the original data. Whereas there
is an algorithm that provides an optimal solution that only requires 6
permutations (instead of 24) in the case of 4-tuple store and 20
permutations (instead of 720) in the case of 6-tuple store.

The problem was stated on
[math.stackexchange.com](https://math.stackexchange.com/q/3146568/23663).
Two answers were provided including an algorithm that allows to
compute the minimal set of indices that allows to query any pattern in
one hop.

**Note:** we only consider the case where the pattern is bound in one
hop because otherwise it would require two or more database calls
which are more costly. We trade some space on disk, to avoid to ask
the database engine another join that could be expensive. Building a
generic tuple store database without that constraint was not tried but
it seems like downstream the code for querying is also more complex.

Here is the algorithm to compute the minimal set of permutations that
allows to bind any pattern in one hop:

```scheme
    (define (permutation-prefix? c o)
      (any (lambda (p) (prefix? p o)) (permutations c)))

    (define (ok? combinations candidate)
      (every (lambda (c) (any (lambda (p) (permutation-prefix? c p)) candidate))
		     combinations))

    (define (findij L)
      (let loop3 ((x L)
                  (y '()))
        (if (or (null? x) (null? (cdr x)))
            (values #f (append (reverse! y) x) #f #f)
            (if (and (not (cdr (list-ref x 0))) (cdr (list-ref x 1)))
                (values #t
                        (append (cddr x) (reverse! y))
                        (car (list-ref x 0))
                        (car (list-ref x 1)))
                (loop3 (cdr x) (cons (car x) y))))))

    (define (bool v)
      (not (not v)))

    (define (lex< a b)
      (let loop ((a a)
                 (b b))
        (if (null? a)
            #t
            (if (not (= (car a) (car b)))
                (< (car a) (car b))
                (loop (cdr a) (cdr b))))))

    (define (make-indices n)
      (let* ((tab (iota n))
             (cx (combination (floor (/ n 2)) tab)))
        (let loop1 ((cx cx)
                    (out '()))
          (if (null? cx)
              (begin (assert (ok? (combinations tab) out))
                     (sort! lex< out))
              (let loop2 ((L (map (lambda (i) (cons i (bool (memv i (car cx))))) tab))
                          (a '())
                          (b '()))
                (call-with-values (lambda () (findij L))
                  (lambda (continue? L i j)
                    (if continue?
                        (loop2 L (cons j a) (cons i b))
                        (loop1 (cdr cx)
                               (cons (append (reverse! a) (map car L) (reverse! b))
                                     out))))))))))
```


### Quadstore versioned in a direct-acyclic-graph

#### History Significance

Merge commits will resolve conflicts in a way that makes it possible
to define a history significance measure that allows to linearize with
a topological sort the direct-acyclic-graph of changes. Without that,
querying versions at any point is not pratical as seen in the
litterature [x].

[x]

### How to model data?

#### Versioned Tabular Data

Frictionless data.

#### Git Kernel

OK

#### Wikidata

TODO

#### Versioned Hacker New

TODO?

## Benchmark

### Git

### Versioned HackerNews

## Annexe

### versioned quadstore reference

#### `(make . config)`

#### `(close . database)`

#### `(metadata database)`

#### `(merge! database branch other)`

#### `(reverse! database revision)`

#### `(make-branch! database name revision snapshot?)`

#### `(snapshot! database branch)`

#### `(transactional proc) → procedure`

#### `(branch transaction name)`

#### `(ask? transaction revision collection uid key value)`

#### `(add transaction revision collection uid key value)`

#### `(rm transaction revision collection uid key value)`
