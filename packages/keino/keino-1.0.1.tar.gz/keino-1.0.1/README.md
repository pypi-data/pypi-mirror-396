# keino

Useful tools and utilities I use for scientific programming.

# Summary of utilities

* `Params`: Handy class for containing parameters.
* `RoundedPolygon`: Matplotlib patch object corresponding to a rectangle with rounded corners.
* `add_colourbar`: Create a matplotlib colourbar, with the orientation, scale, and position tunable.
* `build_axes_grid`: Create a grid of matplotlib axes, with the spacings, offsets, and aspect ratios tunable.
* `colours`: Various colourmaps and related utilities.
* `copy_artist`: Copy a matplotlib artist.
* `hash_dict`: Creates a unique hash for a dict
* `int_path`: Creates a list of indices between the given points.
* `kpath`: Discretises the Brillouin zone between certain momenta points.
* `ndindex`: Similar to numpy.ndindex, but allows also for specifying the lower as well as upper point of the iterators.
* `pprint`: Prints a matrix nicely in a Jupyter notebook.
* `vectorize_parallel`: Decorator which allows a function to take vector arguments, and also enables parallel processing with caching to disk.
* `versioned_import`: Allows for importing a library function, with a particular version enforced.

# Licences

rounded_polygon.py: CC BY-SA 4.0

vectorize_parallel.py: AGPL v2

All other code: GPL v3+
