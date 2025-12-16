# Creates a list of indices between the given points
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

def int_path(points, wrap=False):
    """
    Create a list of indices (a path of integers) between
    the given points.
    wrap = True wraps the path on itself, including indices 
    between the last and first point
    """
    path = []
    for (x0, y0), (x1, y1) in zip(points, points[1:]):
        if y0 == y1:
            if x0 > x1:
                for x in range(x0, x1, -1):
                    path.append((x, y0))
            else:
                for x in range(x0, x1):
                    path.append((x, y0))
        if x0 == x1:
            if y0 > y1:
                for y in range(y0, y1, -1):
                    path.append((x0, y))
            else:
                for y in range(y0, y1):
                    path.append((x0, y))
    if wrap:
        x0, y0 = points[-1]
        x1, y0 = points[0]
        if y0 == y1:
            if x0 > x1:
                for x in range(x0, x1, -1):
                    path.append((x, y0))
            else:
                for x in range(x0, x1):
                    path.append((x, y0))
        if x0 == x1:
            if y0 > y1:
                for y in range(y0, y1, -1):
                    path.append((x0, y))
            else:
                for y in range(y0, y1):
                    path.append((x0, y))
        # path.append((x1, y1))
    return path
