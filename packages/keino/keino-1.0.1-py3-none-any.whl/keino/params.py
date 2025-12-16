# Handy class for containing parameters.
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

from collections.abc import Mapping
import ast
import copy
import numpy as np
from .hash_dict import hash_dict

class Params(Mapping):
    def __init__(self, params, excluded_keys=[]):
        """
        Converts a dict of parameters into a friendly object.

        Example:
            params = Params(dict(
                # Some parameters for a calculation
                mu = 1,
                Delta = 0.1,
                alpha = 0.5,
                sub = dict(
                    beta = 2,
                    kappa = -0.1
                    ),
                ))

            # can now access elements as attributes
            mu = params.mu
            kappa = params.sub.kappa
            # or as strings (useful for metaprogramming)
            beta = params["sub.beta"]

            # can similarly add elements
            params.foo = "foo"
            params.sub.bar = "bar"

            # and remove items
            params.pop("Delta")

            # unique id
            hash = params.hash()

        Parameters
        ----------
        params: dict | str | numpy.ndarray
            Create a params object from a dict, or a str representation,
            or a numpy-encoded representation. The latter, for example,
            might come from np.savez("data.npz", params=params.items()).
        excluded_keys: list
            All subdictionaries are also converted to params objects,
            unless their key is in this list. Handy for exceptionally
            complicated parameters objects.
        """
        if isinstance(params, str):
            params = self.from_str(params)
        if isinstance(params, np.ndarray):
            params = dict(params.tolist())

        self.excluded_keys = excluded_keys
        for k, v in params.items():
            if type(v) == dict and k not in self.excluded_keys:
                setattr(self, k, Params(v))
            elif type(v) == list:
                setattr(self, k, np.array(v))
            else:
                setattr(self, k, v)

    def from_str(self, params):
        tmp = str(params)
        tmp = tmp[10:len(tmp)-1]
        tmp = tmp.replace("array(", "")
        tmp = tmp.replace("])", "]")
        params = ast.literal_eval(tmp)
        return params

    def __len__(self):
        return len(vars(self))

    def get(self, key, value=None):
        if "." in key:
            key, *rest = key.split(".")
            rest = ".".join(rest)
            if key in vars(self):
                try:
                    return vars(self)[key].get(rest, value)
                except:
                    return vars(self)[key]
        if key in vars(self):
            value = vars(self)[key]
        return value

    def __iter__(self):
        for k in vars(self):
            yield k

    def __getitem__(self, key):
        if "." in key:
            key, *rest = key.split(".")
            rest = ".".join(rest)
            if key in vars(self):
                return vars(self)[key][rest]
        return vars(self)[key]

    def __setitem__(self, key, value):
        if "." in key:
            key, *rest = key.split(".")
            rest = ".".join(rest)
            vars(self)[key][rest] = value
        else:
            if type(value) == dict and key not in self.excluded_keys:
                setattr(self, key, Params(value))
            else:
                setattr(self, key, value)

    def to_dict(self):
        tmp = {}
        for k in vars(self):
            v = vars(self)[k]
            if type(v) == Params:
                v = v.to_dict()
            if type(v) == dict:
                v = v.copy()
            if type(v) == np.ndarray:
                v = v.tolist()
            tmp[k] = v
        return tmp

    def hash(self):
        tmp = self.to_dict()
        return hash_dict(tmp)

    def copy(self):
        return self.__copy__()

    def __copy__(self):
        return Params(vars(self))

    def __deepcopy__(self):
        return Params(copy.deepcopy(vars(self)))

    def __repr__(self):
        return f"{vars(self)}"

    def pop(self, key):
        v = self[key]
        delattr(self, key)
        return v

    def pretty(self, units):
        """Pretty-print the parameters"""
        string = "Parameters(\n"
        l = len(vars(self))
        r = len(units)
        assert  l == r, f"{l}, {r}"
        for k,u in zip(vars(self), units):
            u = u if u is not None else ""
            v = self[k]
            string = f"{string}\t{k}: {v}{u}\n"
        string = f"{string})"
        return string.expandtabs(4)
