# copernic (https://github.com/amirouche/copernic)

# Copyright (C) 2020 Amirouche Boubekki

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
from uuid import uuid4

import fdb
import fdb.tuple

from immutables import Map
import nstore



class VNStoreBase:
    pass


class VNStoreExcpetion(Exception):
    pass


class VNStore(VNStoreBase):

    def __init__(self, subspace, items):
        assert isinstance(subspace, (tuple, list))
        assert isinstance(items, (tuple, list))
        self._subspace = subspace
        self._items = items = list(items)
        # A change can have two key:
        #
        # - "message": that is a small description of the change
        #
        # - "significance": once the change is applied, it has an
        #    history significance VersionStamp that allows to order
        #    the changes.
        #
        self._changes = nstore.open(
            subspace + ['changes'],
            ('uid', 'key', 'value')
        )
        # self.tuples contains the tuples associated with the change
        # identifier (changeid) that created or removed the tuple
        # (alive?).
        self._tuples = nstore.open(
            subspace + ['tuples'],
            items + ['alive?', 'changeid']
        )

    def change_create(self, tr):
        # TODO: XXX: In theory, uuid4 can clash, replace with
        # VersionStamp.
        tr._vnstore_changeid = changeid = uuid4()
        # With significance as `None` the change is invisible to
        # VNStore.ask.
        self._changes.add(tr, changeid, 'significance', None)
        self._changes.add(tr, changeid, 'message', None)

        return changeid

    def change_continue(self, tr, changeid):
        tr._vnstore_changeid = changeid

    def change_message(self, tr, changeid, message):
        # Remove existing message if any
        bindings = self._changes.FROM(tr, changeid, 'message', nstore.var('message'))
        for binding in bindings:
            self._changes.delete(tr, changeid, 'message', binding['message'])
        # add message
        self._changes.add(tr, changeid, 'message', message)

    def change_apply(self, tr, changeid):
        # apply change by settings a verionstamp
        self._changes.delete(tr, changeid, 'significance', None)
        self._changes.add(tr, changeid, 'significance', fdb.tuple.Versionstamp())

    def ask(self, tr, *items):
        assert len(items) == len(self._items), "Incorrect count of ITEMS"
        # Complexity is O(n), where n is the number of times the exact
        # same ITEMS was added and deleted.  In pratice, n=0, n=1 or
        # n=2, and of course it always possible that it is more...
        bindings = self._tuples.FROM(tr, *items, nstore.var('alive?'), nstore.var('changeid'))
        found = False
        significance_max = fdb.tuple.Versionstamp(b'\x00' * 10)
        for binding in bindings:
            changeid = binding['changeid']
            significance = self._changes.FROM(
                tr,
                changeid, 'significance', nstore.var('significance')
            )
            significance = next(significance)
            significance = significance['significance']
            if (significance is not None) and (significance > significance_max):
                found = binding['alive?']
        return found

    def add(self, tr, *items):
        assert len(items) == len(self._items)
        if self.ask(tr, *items):
            # ITEMS already exists.
            return False
        # Add it
        items = list(items) + [True, tr._vnstore_changeid]
        self._tuples.add(tr, *items)
        return True

    def delete(self, tr, *items):
        assert len(items) == len(self._items)
        if not self.ask(tr, *items):
            # ITEMS does not exists.
            return False
        # Delete it
        items = list(items) + [False, tr._vnstore_changeid]
        self._tuples.add(tr, *items)
        return True

    def FROM(self, tr, *pattern, seed=Map()):  # seed is immutable
        """Yields bindings that match PATTERN"""
        assert len(pattern) == len(self._items), "invalid item count"
        # TODO: validate that pattern does not have variables named
        # `alive?` or `changeid`.

        def bind(pattern, binding):
            for item in pattern:
                if isinstance(item, Variable):
                    yield binding[item.name]
                else:
                    yield item

        # The complexity really depends on the pattern.  A pattern
        # only made of variables will scan the whole database.  In
        # practice, the user will seldom do time traveling queries, so
        # it should rarely hit this code path.
        pattern = list(pattern) + [nstore.var('alive?'), nstore.var('changeid')]
        bindings = self._tuples.FROM(tr, *pattern, seed=seed)
        for binding in bindings:
            if not binding['alive?']:
                # The associated tuple is dead, so the bindings are
                # not valid in all cases.
                continue
            elif self.ask(self, *bind(pattern, binding)):
                # The bound pattern exist, so the bindings are valid
                binding = binding.delete('alive?')
                binding = binding.delete('changeid')
                yield binding
            else:
                continue

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



open = VNStore


def select(seed, *wheres):
    out = seed
    for where in wheres:
        out = where(out)
    return out
