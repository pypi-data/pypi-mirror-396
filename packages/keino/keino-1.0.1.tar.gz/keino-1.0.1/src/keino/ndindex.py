# Similar to numpy.ndindex, but allows specifying both lower and upper points of the iterators.
# Copyright (C) 2025 Dan Crawford
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

def ndindex(*args):
    """
    Similar to numpy.ndindex but both lower and upper bounds can be specified.

    Example:
        ndindex(10, 20, (-3, 15), (-19, 21), 4)

    """
    def product(*iterables):
        pools = [tuple(pool) for pool in iterables]

        result = [[]]
        for pool in pools:
            result = [x+[y] for x in result for y in pool]

        for prod in result:
            yield tuple(prod)

    ranges = []
    for _range in args:
        if hasattr(_range, "__len__"):
            ranges.append(range(_range[0], _range[1]))
        else:
            ranges.append(range(_range))

    return product(*ranges)
