#
# Copyright (C) 2015-2020  Amirouche Boubekki <amirouche.boubekki@gmail.com>
#
# https://github.com/amirouche/copernic
#
from itertools import permutations

from immutables import Map

import fdb
from fdb.tuple import pack
from fdb.tuple import unpack
from copernic.nstore.indices import compute_indices


# hoply! hoply! hoply!


class  NStoreBase:
    pass


class  NStoreException(Exception):
    pass


class Variable:

    __slots__ = ("name",)

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return "<var %r>" % self.name


# XXX: use `var` only in `NStore.FROM`, and `NStore.where` queries
var = Variable


def stringify(list):
    return "".join(str(x) for x in list)


def is_permutation_prefix(combination, index):
    index = stringify(index)
    out = any(index.startswith(stringify(x)) for x in permutations(combination))
    return out


class NStore(NStoreBase):

    def __init__(self, prefix, items):
        self._prefix = prefix
        self._items = items
        self._indices = compute_indices(len(items))

    def add(self, tr, *items):
        assert len(items) == len(self._items), "invalid item count"
        for subspace, index in enumerate(self._indices):
            permutation = list(items[i] for i in index)
            key = (self._prefix, subspace, permutation)
            tr.add(pack(key), b"")

    def delete(self, tr, *items):
        assert len(items) == len(self._items), "invalid item count"
        for subspace, index in enumerate(self._indices):
            permutation = list(items[i] for i in index)
            key = (self._prefix, subspace, permutation)
            del tr[pack(key)]

    def ask(self, tr, *items):
        assert len(items) == len(self._items), "invalid item count"
        subspace = 0
        key = (self._prefix, subspace, items)
        out = tr.get(pack(key))
        out = out is not None
        return out

    def FROM(self, tr, *pattern, seed=Map()):  # seed is immutable
        """Yields bindings that match PATTERN"""
        assert len(pattern) == len(self._items), "invalid item count"
        variable = tuple(isinstance(x, Variable) for x in pattern)
        # find the first index suitable for the query
        combination = tuple(x for x in range(len(self._items)) if not variable[x])
        for subspace, index in enumerate(self._indices):
            if is_permutation_prefix(combination, index):
                break
        else:
            raise NStoreException("Oops!")
        # `index` variable holds the permutation suitable for the
        # query. `subspace` is the "prefix" of that index.
        prefix = tuple(pattern[i] for i in index if not isinstance(pattern[i], Variable))
        prefix = (self._prefix, subspace, prefix)
        for key, _ in tr.get_range_startswith(pack(prefix)[:-1]):
            key = unpack(key)
            items = key[2]
            # re-order the items
            items = tuple(items[index.index(i)] for i in range(len(self._items)))
            # seed is immutable
            bindings = seed
            for i, item in enumerate(pattern):
                if isinstance(item, Variable):
                    bindings = bindings.set(item.name, items[i])
            yield bindings

    def where(self, tr, *pattern):
        assert len(pattern) == len(self._items), "invalid item count"

        def _where(iterator):
            for bindings in iterator:
                # bind PATTERN against BINDINGS
                bound = []
                for item in pattern:
                    # if ITEM is variable try to bind
                    if isinstance(item, Variable):
                        try:
                            value = bindings[item.name]
                        except KeyError:
                            # no bindings
                            bound.append(item)
                        else:
                            # pick the value from bindings
                            bound.append(value)
                    else:
                        # otherwise keep item as is
                        bound.append(item)
                # hey!
                yield from self.FROM(tr, *bound, seed=bindings)

        return _where


def select(seed, *wheres):
    out = seed
    for where in wheres:
        out = where(out)
    return out
