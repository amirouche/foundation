# datae: an application of versioned quad store

![data](https://raw.githubusercontent.com/awesome-data-distribution/datae/master/data.jpg)

## Author

Amirouche Boubekki

## Abstract

datae is web application that is (mostly) implemented with Scheme
programming language. It is supported by a database that is a quad
store versioned in a direct-acyclic-graph. It is possible to do time
traveling queries at any point in history while still being efficient
to query and modify the latest version. The versioned quad store is
implemented using a novel approach dubbed generic n-tuple store. datae
application goal is to demonstrate that versioned databases allow to
implement workflows that ease cooperation.

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
implement a mechanic similar to github's pull requests and gitlab's
merge requests in many domains. That very mechanic is explicit about
the actual human workflow in entreprise settings in particular when
a senior person validates a change by a less senior person.

The versioned quad store make the implementation of such mechanics more
systematic and less error prone as the implementation can be shared
across various tools and organisations.

datae takes the path of versioning data and apply the pull request
mechanic to collaborate around the making of a knowledge base, similar
in spirit to wikidata and inspired from existing data management
systems like CKAN.

The use of a version control system to store open data is a good thing
as it draws a clear path for reproducible science. But none, meets all
the expectations. datae aims to replace the use of git and make
practical cooperation around the creation, publication, storage,
re-use and maintenance of knowledge bases that are possibly bigger
than memory. Resource Description Framework (RDF) offers a good canvas
for cooperation around open data but there is no solution that is good
enough according to Canova et al. [1]

[1] [Collaborative Open Data versioning: a pragmatic approach using
Linked Data](https://core.ac.uk/download/pdf/76527782.pdf)

datae use a novel approach to store quads in an ordered key-value
store. It use WiredTiger database storage engine to deliver a
pragmatic versatile ACID-compliant versioned quad store. It also rely
on a new algorithm to query versioned tuples based on a topological
graph ordering of changes. datae only stores changes between
versions. datae does not rely on the theory of patches introduced by
Darcs but re-use some its vocabulary.

The first part will present some background knowledge, the second part
will describe the implementation, the next part will present
benchmarks and at last we will conclude with summary of the work and
what remains to be explored.

The code is hosted at [source hut](https://git.sr.ht/~amz3/chez-scheme-arew).

## Background

This section will describe a few concept upon which datae is built or
take inspiration.

### Resource Description Framework

[RDF](https://www.w3.org/TR/2014/REC-rdf11-concepts-20140225/) is
World Wide Web Consortium (W3C) set of standards that aims to
facilitating cooperation around data by specifying several
tools. Among other things it specified means to exchange, query and
somewhat how to store data. datae only takes inspiration from this
standards. It doesn't forcefully implement (for the time being) the
different RDF specifications (that are by the way in the process of a
rework). datae takes what is good and leave aside what is not.

The following sections dive into several part of the RDF framework and
explain how they relate to datae.

#### SPARQL

SPARQL is a query language part of RDF that specify the language that
must be used by RDF databases to store and query data. It also
provides ways to do federated queries. That is, queries across several
databases. Like it is explained in the literature SPARQL can be
difficult at times to implement . Instead of aiming for direct
interoperability, datae take the stance to primarly deliver its main
feature that is *cooperation around the making of knowledge bases*.
The main drawback could be that the learning curve to join the datae
party could be more steep. But that is not the case, for two reasons:
a) datae internal query language is similar in principle to SPARQL
even if it is not exact same syntax b) the primary user interface of
data is not SPARQL. Instead, the interact with datae, an user will
rely on an graphical user interface or command line tool to upload and
download a given version of some data. For some advanced use cases a
subset of SPARQL will be available.

SPARQL specify various data types based on XML specification.  datae
doesn't conform to that specification. Instead, datae can store
anything that has a JSON representation which is superset of RDF base
data types.

#### Vocabularies, Ontologies and Linked Data

With RDF comes a specification to describe the content of a
database. For instance, the
[INSPIRE](https://github.com/inspire-eu-rdf) initiative is an
interesting project that aims that standarzing across organisation a
vocabulary to exchange spatial data. There is many competing
vocabulary.

Settling on particular vocabulary is not necessary and the choice of a
vocabulary can be made later.

### Version Control System

datae is about versioning data. That is keeping a record of how the
data looks like in a very precise way and how it evolves over time.
It also about exchanging data. Not just querying remote databases, but
getting the actual data locally to be able to fix it, refine it,
improve it and more generally collaborate.

In general, a VCS is a particular system that draws a canvas for
collaboration around the making of software products.  VCS are things
like git, mercurial and fossil. That said, it is not the only
instances of versioning in the wild. There is also wikis!  And among
them there is wikibase the software that sports wikidata.

Compared to git, mercurial or fossil, datae aims to achieve a very
similar user-experience. That is commit-push-pull mechanic and the, so
called, pull requests. The problem with git, in particular, because it
is the main competitor, is that it doesn't support well bigger than
memory data. Otherwise said, it is bad at handling large
datasets. Unlike git, datae handles bigger than RAM structured data.
This made possible thanks to WiredTiger which is a real
database. WiredTiger is a database engine that is widespread in the
industry. It is used at MongoDB and Amazon.

Compared to wikibase and wikidata, datae aims to be much more easy to
setup and operate. To achieve something similar to datae, one need
both to setup wikibase with MySQL to allow edition and store history
and blazegraph to do querying. datae will simplify collaboration
around the making of large knowledge bases.

datae is collaboration tool that is a mix a of git and wikibase. Like
git, it is portable, easy to setup. Like wikibase, it allows to edit
and query efficently structured data.

### Ordered Key-Value Store

Key-value stores offers a rather high level primitive to build high
performance, multi-model and domain specific databases. The common
denominator of key-value stores is that they are mappings of bytes
where keys are always sorted in the lexicographic order. Even if they
do not all expose a cursor interface, they certainly allow movements
inside the mapping or range queries (also known as slices).

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
can build abstractions to solve bigger problems. The generic n-tuple
store is such an abstraction. It allows to take advantage of
WiredTiger without scarifying expressiveness. Generic n-tuple store is
a set of procedures that generalize triple and quad store respectively
3-tuples and 4-tuples to n-tuples. In turn, it allows to share code to
implement the versioned database to represent its components:

- The repository metadata as a 4-tuple store,
- the versioned quads as a 6-tuple store,
- and the 4-tuple stores that are snapshots of branches.

That section is split into four parts. The first part is a tentative
formalisation of the problem of finding a smallest set of indices that
allows to bind any pattern in one hop to implement the generic tuple
store. The third part will dive into the specifics of the
implementation of versioned 4-tuples using the generic n-tuple store
and how the concept of history significance makes querying versioned
tuples in a direct-acyclic-graph algorithmically less complex. The
fourth and last part of this section explain how to model various
datastructures in terms of quads to take advantage of versioning.

### Generic n-tuple store

The literature seems to be void from attempts to build tuple stores
based on Ordered Key-Value store. Even if similar work exsists like
hexastore they don't try to generalize the concept of triple and quad
store so that it possible to create a database that can host tuple of
n items.

Given a 4-tuple store:

```scheme
(define quadstore (nstore engine prefix '(collection uid key value)))
```

We need to bind any pattern in one hop. That is, the following query:

```
(nstore-select (nstore-from 'blog (nstore-var 'uid) 'title (nstore-var 'title)))
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
compute the minimal set of indices allowing to query any pattern in
one hop.

**Note:** we only consider the case where the pattern is bound in one
hop because otherwise it would require two or more database calls
which are more costly. We trade some space on disk, to avoid to ask
the database engine another join that is expensive. Building a generic
n-tuple store database without that constraint was not tried. Also
downstream the code for querying is more complex.

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


### Quad store versioned in a direct-acyclic-graph

#### History Significance

Merge commits will resolve conflicts in a way that makes it possible
to define a history significance measure that allows to linearize with
a topological sort the direct-acyclic-graph of changes.

### How to model data?

#### Versioned Tabular Data

Frictionless data: https://frictionlessdata.io/data-packages/

#### Linux kernel's git repository

#### Wikidata

#### Versioned hackernews

http://news.ycombinator.com/

## Benchmarks

### Versioned Tabular Data

### Wikidata

### Versioned hackernews

## Annexes

### SRFI-167: Ordered key-value store (okvs)

[https://srfi.schemers.org/srfi-167/](https://srfi.schemers.org/srfi-167/)

### SRFI-168: Generic n-tuple store (nstore)

[https://srfi.schemers.org/srfi-168/](https://srfi.schemers.org/srfi-168/)

### Functional store (fstore)

#### `(make-fstore engine prefix)`

Return a `fstore` object.

#### `(fstore-bigbang)`

Return the null identifier that is used to create orphan branches.

#### `(fstore-branch-create fstore some name parent)`

Create a branch in `FSTORE` named `NAME` that has `PARENT` as parent
using `SOME`. `SOME` can be an `okvs` object or transaction. Return
the identifier of the created branch.

To create an orphan branch, one can do the following:

```scheme
(define main (fstore-branch-create fstore okvs "main" (fstore-bigbang)))
```

#### `(fstore-branch fstore some name)`

Return the unique identifier of the branch `NAME` in `FSTORE` using
`SOME`. `SOME` can be an `okvs` object or transaction. Return `#f` if
there is no existing branch `NAME`.

#### `(fstore-merge fstore transaction branch other)`

Merge in `FSTORE` the branch `OTHER` in `BRANCH` using `TRANSACTION`.

#### `(fstore-ask? some fstore branch quad)`

Return `#t` if `QUAD` exists in `FSTORE`'s `BRANCH`. Otherwise, it
return `#f`.

#### `(fstore-add! some fstore branch quad)`

Add `QUAD` to `FSTORE` in `BRANCH` using `SOME`. `SOME` can be an
`okvs` object or transaction.

#### `(fstore-rm! some fstore branch quad)`

Remove `QUAD` from `FSTORE` in `BRANCH` using `SOME`. `SOME` can be an
`okvs` object or transaction.

#### `(fstore-from transaction fstore branch pattern [config])`

#### `(fstore-where transaction fstore branch pattern)`

#### `(fstore-select <from> <where> ...)` syntax
