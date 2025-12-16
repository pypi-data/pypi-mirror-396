# Creates a grid of matplotlib axes.
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
    from matplotlib import colors
    cont = True
except:
    cont = False

if cont:
    import numpy as np
    def build_axes_grid(fig, nx, ny, width=None, height=None, xoff=0.05, yoff=0.05, xspace=None, yspace=None, aspect=None, axes_args=None, share=True):
        """
        Build a grid of matplotlib axes

        Parameters
        ----------
        fig: matplotlib.figure.Figure
        nx, ny: int
            number of axes in the x and y directions
        width, height: float
            width and height of each axis
        xoff, yoff: float | pair of floats
            margin between the boundaries of the figure and the extremal axes.
            If a float, then the same margin is applied to the left/right or top/bottom.
            Otherwise, if a pair than the appropriate values are applied.
        xspace, yspace: float
            Spacing between axes
        aspect: float
            Aspect ratio of the axes
        axes_args:
            additional arguments passed to figure.add_axes
        share: bool
            if the axes should be shared, so that x/y ticklabels are only shown on the left and bottom axes

        Returns
        ----------
        axes: numpy array of matplotlib.axis.Axis
            Note that the origin coresponds to the bottom left axis.
        """
        if isinstance(xoff, int) or isinstance(xoff, float):
            xoff = (xoff, xoff)
        if isinstance(yoff, int) or isinstance(yoff, float):
            yoff = (yoff, yoff)
        if not xspace is not None:
            xspace = 0.1/nx
        if not yspace is not None:
            yspace = 0.1/ny
        if not width is not None:
            width = (1-xoff[0]-xoff[1]-(nx-1)*xspace)/nx
        if not height is not None:
            height = (1-yoff[0]-yoff[1]-(ny-1)*yspace)/ny

        fig_width, fig_height = fig.bbox_inches._points[1]

        if aspect is not None:
            if fig_width < fig_height:
                height = width * aspect * fig_width / fig_height
            else:
                width = height * aspect * fig_height / fig_width

        if nx == ny == 1:
            if axes_args is not None:
                kwargs = axes_args[i, j]
            else:
                kwargs = {}
            i = 0
            j = 0
            axis = fig.add_axes([xoff[0]+i*(xspace+width), yoff[0]+j*(yspace+height), width, height], **kwargs)
            return axis

        axes = np.empty((nx, ny), dtype=object)
        for i, j in np.ndindex(nx, ny):
            if axes_args is not None:
                kwargs = axes_args[i, j]
            else:
                kwargs = {}
            axes[i, j] = fig.add_axes([xoff[0]+i*(xspace+width), yoff[0]+j*(yspace+height), width, height], **kwargs)
        if share:
            for i, j in np.ndindex(nx, ny):
                if i > 0:
                    axes[i, j].sharey(axes[0, j])
                    axes[i, j].tick_params(axis="y", labelleft=False)
                if j > 0:
                    axes[i, j].sharex(axes[i, 0])
                    axes[i, j].tick_params(axis="x", labelbottom=False)

        return np.squeeze(axes) 
else:
    def build_axes_grid(fig, nx, ny, width=None, height=None, xoff=0.05, yoff=0.05, xspace=None, yspace=None, aspect=None, axes_args=None, share=True):
        raise NotImplementedError("matplotlib not installed!")
