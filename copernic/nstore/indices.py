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
"""Compute the (perfect?) minimal set of indices required to bind any
pattern in one hop.

Based on https://stackoverflow.com/a/55148433/140837

"""
import itertools
from math import factorial


bc = lambda n, k: factorial(n) // factorial(k) // factorial(n - k) if k < n else 0


def pk(*args):
    print(*args)
    return args[-1]


def stringify(iterable):
    return "".join(str(x) for x in iterable)


def combinations(tab):
    out = []
    for i in range(1, len(tab) + 1):
        out.extend(stringify(x) for x in itertools.combinations(tab, i))
    assert len(out) == 2 ** len(tab) - 1
    return out


def ok(solutions, tab):
    """Check that SOLUTIONS of TAB is a correct solution"""
    cx = combinations(tab)

    px = [stringify(x) for x in itertools.permutations(tab)]

    for combination in cx:
        pcx = ["".join(x) for x in itertools.permutations(combination)]
        # check for existing solution
        for solution in solutions:
            if any(solution.startswith(p) for p in pcx):
                # yeah, there is an existing solution
                break
        else:
            print("failed with combination={}".format(combination))
            break
    else:
        return True
    return False


def _compute_indices(n):
    tab = list(range(n))
    cx = list(itertools.combinations(tab, n // 2))
    for c in cx:
        L = [(i, i in c) for i in tab]
        A = []
        B = []
        while True:
            for i in range(len(L) - 1):
                if (not L[i][1]) and L[i + 1][1]:
                    A.append(L[i + 1][0])
                    B.append(L[i][0])
                    L.remove((L[i + 1][0], True))
                    L.remove((L[i][0], False))
                    break
            else:
                break
        l = [i for (i, _) in L]
        yield tuple(A + l + B)


def compute_indices(n):
    return list(_compute_indices(n))


if __name__ == "__main__":
    for i in range(7):
        tab = stringify(range(i))
        solutions = [stringify(x) for x in compute_indices(i)]
        assert ok(solutions, tab)
        print("n={}, size={}, solutions={}".format(i, len(solutions), solutions))
