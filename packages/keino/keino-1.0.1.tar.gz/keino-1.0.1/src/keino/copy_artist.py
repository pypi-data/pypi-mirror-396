# Copy a matplotlib artist
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

def copy_artist(from_artist, to_artist, ignore_attributes=[], extra_fields=None):
    """
    Copy a matplotlib artist.
    Currently, artists do not have a built-in method copy(); this function rectifies this oversight.

    Parameters
    ----------
    from_artist: matplotlib.artist.Artist
        artist to copy
    to_artist: matplotlib.artist.Artist
        destination artist. Must be pre-allocated
    ignore_attributes: list[str]
        attributes that should not be copied
    extra_fields: list[str] | None
        additional fields to copy
    """
    # Basic idea from <https://stackoverflow.com/a/59325029>

    def copy_attributes(from_artist, to_artist, attributes):
        for i_attribute  in attributes:
            getattr(to_artist, 
                    'set_' + i_attribute)( getattr(from_artist, 'get_' + i_attribute)() )

    def get_attributes(obj, ignore_attributes):
        obj_methods_list = dir(obj)

        obj_get_attr = []
        obj_set_attr = []
        obj_transf_attr =[]

        for name in obj_methods_list:
            if len(name) > 4:
                prefix = name[0:4]
                if prefix == 'get_':
                    obj_get_attr.append(name[4:])
                elif prefix == 'set_':
                    obj_set_attr.append(name[4:])

        for attribute in obj_set_attr:
            if attribute in obj_get_attr and attribute not in ignore_attributes:
                obj_transf_attr.append(attribute)

        return obj_transf_attr

    attributes = get_attributes(from_artist, ignore_attributes)

    copy_attributes(from_artist, to_artist, attributes)

    if extra_fields is not None:
        for field in extra_fields:
            setattr(to_artist, field, getattr(from_artist, field))
