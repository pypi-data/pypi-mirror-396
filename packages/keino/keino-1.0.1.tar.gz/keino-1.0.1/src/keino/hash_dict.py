# Creates a unique hash for a dict
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

import hashlib

def hash_dict(d):
    """
    Creates a unique hash for an (arbitrarily complicated) dict.
    """
    for k,v in d.items():
        if type(v) == list:
            d[k] = str(v)
        if type(v) == dict:
            d[k] = hash_dict(v)

    h = hashlib.sha224(
        str(
            sorted(
                list(
                    frozenset(d.items())
                )
            )
        ).encode('utf-8')
    ).hexdigest()[:20]
    return h
