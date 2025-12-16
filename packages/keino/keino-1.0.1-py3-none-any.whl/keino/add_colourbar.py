# Creates a matplotlib colourbar.
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

try:
    from matplotlib import *
    cont = True
except:
    cont = False

if cont:
    def add_colourbar(fig, axis, im, xoff=0.05, yoff=0, xscale=0.05, yscale=1, horizontal=False, **kwargs):
        """
        Create a matplotlib colourbar

        Parameters
        ----------
        fig: matplotlib.figure.Figure
        axis: matplotlib.axes.Axis
        im: matplotlib.collections.QuadMesh or similar
            matplotlib object which can have a colourbar
        xoff: float
            distance between the right edge of the axis and the left edge of the colourbar
        yoff: float
            distance between the bottom edge of the axis and the bottom edge of the colourbar
        xscale: float
            width of the colourbar = xscale x width of axis
        yscale: float
            height of the colourbar = yscale x height of axis
        horizontal: bool
            if the colourbar should have vertical or horizontal orientation
        kwargs:
            additional arguments to figure.colorbar

        Returns
        ----------
        cb: matplotlib.colorbar.Colorbar
        cax: matplotlib.axes.Axis
            the axis corresponding to the colorbar
        """
        if horizontal:
            xoff = 0
            yoff = 0.05
            xcale = 1
            yscale = 0.05

            pos = axis.get_position()
            cax = fig.add_axes([pos.x0 + xoff, pos.y1 + yoff, xscale * (pos.x1 - pos.x0), yscale * (pos.y1 - pos.y0)])
            cb = fig.colorbar(im, cax=cax, orientation="horizontal", **kwargs)
            cb.ax.xaxis.set_ticks_position("top")
        else:
            pos = axis.get_position()
            cax = fig.add_axes([pos.x1 + xoff, pos.y0 + yoff, xscale * (pos.x1 - pos.x0), yscale * (pos.y1 - pos.y0)])
            cb = fig.colorbar(im, cax=cax, **kwargs)
        return cb, cax
else:
    def add_colourbar(fig, axis, im, xoff=0.05, yoff=0, xscale=0.05, yscale=1, horizontal=False, **kwargs):
        raise NotImplementedError("matplotlib not installed!")
