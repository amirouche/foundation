# copernic (https://github.com/amirouche/copernic)

# Copyright (C) 2015-2020 Amirouche Boubekki

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.

# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
from itertools import permutations
import struct

from immutables import Map

import fdb
import fdb.tuple
from nstore.indices import compute_indices


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


ONE = struct.pack('<q', 1)
MINUS_ONE = struct.pack('<q', -1)


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
        self._counter_key = fdb.tuple.pack((self._prefix, "counter"))

    def add(self, tr, *items):
        assert len(items) == len(self._items), "invalid item count"
        if any(isinstance(x, fdb.tuple.Versionstamp) for x in items):
            pack = fdb.tuple.pack_with_versionstamp
            set = tr.set_versionstamped_key
        else:
            pack = fdb.tuple.pack
            set = tr.set
        for subspace, index in enumerate(self._indices):
            permutation = list(items[i] for i in index)
            key = (self._prefix, subspace, permutation)
            set(pack(key), b"")

        # increment the count of triples
        tr.add(self._counter_key, ONE)

    def delete(self, tr, *items):
        assert len(items) == len(self._items), "invalid item count"
        for subspace, index in enumerate(self._indices):
            permutation = list(items[i] for i in index)
            key = (self._prefix, subspace, permutation)
            del tr[fdb.tuple.pack(key)]

        # decrement count of tuples
        tr.add(self._counter_key, MINUS_ONE)

    def count(self, tr):
        value = tr.get(self._counter_key)
        if value == None:
            return 0
        else:
            return struct.unpack('<q', value[:])[0]

    def ask(self, tr, *items):
        assert len(items) == len(self._items), "invalid item count"
        subspace = 0
        key = (self._prefix, subspace, items)
        out = tr.get(fdb.tuple.pack(key))
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
        for key, _ in tr.get_range_startswith(fdb.tuple.pack(prefix)[:-1]):
            key = fdb.tuple.unpack(key)
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
