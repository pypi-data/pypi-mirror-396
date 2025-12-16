# Adds a decorator which enables a function to take vector arguments, and runs in parallel with caching.
# Author: Pauli Virtanen, Dan Crawford
# License: GNU Affero General Public License, see AGPL.txt for details

import functools
import joblib
import inspect
from tqdm.auto import tqdm
import numpy as np


class _ParallelSafeMemFunc:
    """
    Function that updates inspect.linecache when called.
    Required to make joblib.Memory work with parallel execution
    with IPython cells.
    """

    def __init__(self, func, mem):
        self._orig_func = func
        self._func = mem.cache(func)
        inspect.linecache.checkcache()
        inspect.getsourcelines(func)
        self._linecache = inspect.linecache.cache

    def __call__(self, *args, **kwargs):
        if self._linecache is not None:
            inspect.linecache.cache = self._linecache
            self._linecache = None

        self._old_checkcache = inspect.linecache.checkcache
        try:
            inspect.linecache.checkcache = lambda fn=None: None
            return self._func(*args, **kwargs)
        finally:
            inspect.linecache.checkcache = self._old_checkcache


def _unarray(x):
    if isinstance(x, np.ndarray):
        return x.item()
    return x

class ProgressParallel(joblib.Parallel):
    # https://stackoverflow.com/a/61027781
    def __init__(self, *args, **kwargs):
        self.total = kwargs.pop("total")
        self._progress = kwargs.pop("progress", False)
        super().__init__(**kwargs)

    def __call__(self, *args, **kwargs):
        if self._progress:
            with tqdm(total=self.total) as self._pbar:
                return joblib.Parallel.__call__(self, *args, **kwargs)
        return joblib.Parallel.__call__(self, *args, **kwargs)

    def print_progress(self):
        if self._progress:
            self._pbar.n = self.n_completed_tasks
            self._pbar.refresh()


def vectorize_parallel(
    func=None,
    backend=None,
    n_jobs=-1,
    returns_object=False,
    batch_size="auto",
    included=None,
    excluded=None,
    noarray=False,
):
    """
    Decorator to vectorize and function to evaluate elements in parallel.
    Uses *joblib* for parallelization.

    Parameters
    ----------
    func : function
    backend : str
        Joblib backend
    n_jobs : int
        Number of jobs, -1 means number of CPUs.
    returns_object : bool
        Put function return values to an object array.
    batch_size : {"auto", int}
    included : tuple
        Function argument names to include in vectorization.
    excluded : tuple
        Function argument names to exclude from vectorization.
    noarray : bool
        Convert array-valued return values to scalars.
    """

    if func is None:

        def deco(func):
            return vectorize_parallel(
                func,
                backend=backend,
                n_jobs=n_jobs,
                returns_object=returns_object,
                batch_size=batch_size,
                included=included,
                excluded=None,
                noarray=noarray,
            )

        return deco

    argspec = inspect.signature(func)

    excluded = list(excluded) if excluded else []
    excluded += ["params", "mem", "parallel", "verbose",  "progress", "refresh_cache"]
    if included is not None:
        excluded += [
            x.name for x in argspec.parameters.values() if x.name not in included
        ]

    arg_names = [
        x.name
        for x in argspec.parameters.values()
        if x.kind
        in (inspect.Parameter.POSITIONAL_ONLY, inspect.Parameter.POSITIONAL_OR_KEYWORD)
    ]
    vararg_names = [
        x.name
        for x in argspec.parameters.values()
        if x.kind == inspect.Parameter.VAR_POSITIONAL
    ]
    if vararg_names:
        vararg_name = vararg_names[0]
    else:
        vararg_name = None

    star_kwargs_name = None
    for x in argspec.parameters.values():
        if x.kind == inspect.Parameter.VAR_KEYWORD:
            star_kwargs_name = x.name
            break

    nonvec_arg_names = []
    for name in list(arg_names):
        if name in excluded:
            arg_names.remove(name)
            nonvec_arg_names.append(name)

    if noarray:
        unarray = _unarray
        unarray_many = lambda x: map(_unarray, x)
    else:
        unarray = lambda x: x
        unarray_many = lambda x: x

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        parallel = kwargs.get("parallel", True)
        if "parallel" not in nonvec_arg_names:
            kwargs.pop("parallel", None)

        mem = kwargs.get("mem", None)
        if "mem" not in nonvec_arg_names:
            kwargs.pop("mem", None)

        verbose = kwargs.get("verbose", False)
        if "verbose" not in nonvec_arg_names:
            kwargs.pop("verbose", False)

        progress = kwargs.get("progress", False)
        if "progress" not in nonvec_arg_names:
            kwargs.pop("progress", False)

        refresh_cache = kwargs.get("refresh_cache", False)
        if "refresh_cache" not in nonvec_arg_names:
            kwargs.pop("refresh_cache", None)

        if refresh_cache:
            cache_validation_callback = lambda x: False
        else:
            cache_validation_callback = lambda x: True

        if mem is not None:
            filename = inspect.getsourcefile(func)
            if parallel and filename.startswith("<") and filename.endswith(">"):
                # Lambdas etc. require saving inspect.linecache
                call_func = _ParallelSafeMemFunc(func, mem)
            else:
                call_func = mem.cache(func, cache_validation_callback=cache_validation_callback, verbose=int(verbose))
        else:
            call_func = func

        boundspec = argspec.bind(*args, **kwargs)
        boundspec.apply_defaults()
        callargs = boundspec.arguments
        args = tuple(callargs.pop(name) for name in arg_names)
        if vararg_name:
            args += callargs.pop(vararg_name)

        if star_kwargs_name is not None:
            extra_kwargs = callargs.pop(star_kwargs_name)
            callargs.update(extra_kwargs)

        v = tuple(map(np.asarray, args))
        v_broadcast = np.broadcast_arrays(*v)

        if len(v_broadcast) > 0:
            total = v_broadcast[0].size
            if total == 1:
                parallel = False
        else:
            total = 0
            parallel = False

        if total > 1:
            it = np.nditer(v, ["refs_ok"])

            if parallel:
                delayed = joblib.delayed
            else:
                delayed = lambda x: x

            # Parallelize
            if len(v) == 1:
                jobs = (delayed(call_func)(unarray(w), **callargs) for w in it)
            else:
                jobs = (delayed(call_func)(*unarray_many(w), **callargs) for w in it)

            if parallel:
                results = ProgressParallel(
                    total=total,
                    n_jobs=n_jobs,
                    backend=backend,
                    batch_size=batch_size,
                    progress=progress,
                )(jobs)
            else:
                results = list(jobs)
        else:
            if len(v) == 0:
                results = [call_func(**callargs)]
            else:
                # Single point
                it = np.nditer(v, ["refs_ok"])
                if len(v) == 1:
                    results = [call_func(unarray(w), **callargs) for w in it]
                else:
                    results = [call_func(*unarray_many(w), **callargs) for w in it]

        if not returns_object:
            results = np.array(results)
        else:
            results_arr = np.zeros(len(results), dtype=object)
            results_arr[:] = results
            results = results_arr
            del results_arr
        results_shape = results.shape[1:]

        if results.shape == (1,):
            return results

        if len(v_broadcast) == 0:
            return results[0]

        if results.ndim > 0:
            results = np.rollaxis(results, 0, results.ndim)
        return results.reshape(results_shape + v_broadcast[0].shape)

    return wrapper
