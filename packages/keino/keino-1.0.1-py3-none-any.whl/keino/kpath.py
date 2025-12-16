# Discretises the Brillouin zone between certain momenta points.
# Copyright (C) 2025 Dan Crawford, Harald Jeschke
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

import numpy as np

def kpath(npoints, points, endpoint=True):
    """Discretises the BZ into `npoints` between endpoints  `points`"""
    nsegments = len(points) - 1
    points_per_segment = []
    for i in range(nsegments):
        if i == nsegments - 1:
            points_per_segment.append(
                npoints - int(npoints/nsegments)*(nsegments - 1)
            )
        else:
            points_per_segment.append(int(npoints/nsegments))

    path = []
    endpoint = 1 if endpoint else 0
    for i in range(nsegments):
        if i == nsegments - 1:
            distance = (np.array(points[i+1]) - np.array(points[i])) / (points_per_segment[i] - endpoint)
        else:
            distance = (np.array(points[i+1]) - np.array(points[i])) / (points_per_segment[i])

        for j in range(int(points_per_segment[i])):
            path_point = points[i] + j * distance
            path.append(path_point)
    return path

k_path = kpath
