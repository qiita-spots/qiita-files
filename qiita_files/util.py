# -----------------------------------------------------------------------------
# Copyright (c) 2014--, The Qiita Development Team.
#
# Distributed under the terms of the BSD 3-clause License.
#
# The full license is in the file LICENSE, distributed with this software.
# -----------------------------------------------------------------------------

from contextlib import contextmanager

import h5py


# deprecated sind h5py 3.3,
# see https://docs.h5py.org/en/stable/whatsnew/3.6.html
h5py_version = list(map(int, h5py.__version__.split('.')))
if h5py_version < [3, 3, 0]:
    # not present in all 2.x series
    if hasattr(h5py.get_config(), 'default_file_mode'):
        h5py.get_config().default_file_mode = 'r'


def _is_string_or_bytes(s):
    """Returns True if input argument is string (unicode or not) or bytes.
    """
    return isinstance(s, str) or isinstance(s, bytes)


def _get_filehandle(filepath_or, *args, **kwargs):
    """Open file if `filepath_or` looks like a string/unicode/bytes, else
    pass through.
    """
    if _is_string_or_bytes(filepath_or):
        if h5py.is_hdf5(filepath_or):
            fh, own_fh = h5py.File(filepath_or, *args, **kwargs), True
        else:
            fh, own_fh = open(filepath_or, *args, **kwargs), True
    else:
        fh, own_fh = filepath_or, False
    return fh, own_fh


@contextmanager
def open_file(filepath_or, *args, **kwargs):
    """Context manager, like ``open``, but lets file handles and file like
    objects pass untouched.

    It is useful when implementing a function that can accept both
    strings and file-like objects (like numpy.loadtxt, etc).

    This method differs slightly from scikit-bio's implementation in that it
    handles HDF5 files appropriately.

    Parameters
    ----------
    filepath_or : str/bytes/unicode string or file-like
         If string, file to be opened using ``h5py.File`` if the file is an
         HDF5 file, otherwise builtin ``open`` will be used. If it is not a
         string, the object is just returned untouched.

    Other parameters
    ----------------
    args, kwargs : tuple, dict
        When `filepath_or` is a string, any extra arguments are passed
        on to the ``open`` builtin.

    Examples
    --------
    >>> with open_file('filename') as f:  # doctest: +SKIP
    ...     pass
    >>> fh = open('filename')             # doctest: +SKIP
    >>> with open_file(fh) as f:          # doctest: +SKIP
    ...     pass
    >>> fh.closed                         # doctest: +SKIP
    False
    >>> fh.close()                        # doctest: +SKIP

    """
    fh, own_fh = _get_filehandle(filepath_or, *args, **kwargs)
    try:
        yield fh
    finally:
        if own_fh:
            fh.close()
