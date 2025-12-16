"""Type stubs for PETSc Const module."""

from enum import IntEnum

# Basic constants
DECIDE: int
"""Use a default value for an `int` or `float` parameter."""

DEFAULT: int
"""Use a default value chosen by PETSc."""

DETERMINE: int
"""Compute a default value for an `int` or `float` parameter.
For tolerances this uses the default value from when
the object's type was set."""

CURRENT: int
"""Do not change the current value that is set."""

UNLIMITED: int
"""For a parameter that is a bound, such as the maximum
number of iterations, do not bound the value."""

# Float constants
INFINITY: float
"""Very large real value."""

NINFINITY: float
"""Very large negative real value."""

PINFINITY: float
"""Very large positive real value, same as `INFINITY`."""

class InsertMode(IntEnum):
    """Insertion mode.

    Most commonly used insertion modes are:

    `INSERT`
        Insert provided value/s discarding previous value/s.
    `ADD`
        Add provided value/s to current value/s.
    `MAX`
        Insert the maximum of provided value/s and current value/s.

    See Also
    --------
    petsc.InsertMode
    """

    # native
    NOT_SET_VALUES = ...
    INSERT_VALUES = ...
    ADD_VALUES = ...
    MAX_VALUES = ...
    INSERT_ALL_VALUES = ...
    ADD_ALL_VALUES = ...
    INSERT_BC_VALUES = ...
    ADD_BC_VALUES = ...

    # aliases
    INSERT = ...
    ADD = ...
    MAX = ...
    INSERT_ALL = ...
    ADD_ALL = ...
    INSERT_BC = ...
    ADD_BC = ...

class ScatterMode(IntEnum):
    """Scatter mode.

    Most commonly used scatter modes are:

    `FORWARD`
        Scatter values in the forward direction.
    `REVERSE`
        Scatter values in the reverse direction.

    See Also
    --------
    Scatter.create, Scatter.begin, Scatter.end
    petsc.ScatterMode
    """

    # native
    SCATTER_FORWARD = ...
    SCATTER_REVERSE = ...
    SCATTER_FORWARD_LOCAL = ...
    SCATTER_REVERSE_LOCAL = ...

    # aliases
    FORWARD = ...
    REVERSE = ...
    FORWARD_LOCAL = ...
    REVERSE_LOCAL = ...

class NormType(IntEnum):
    """Norm type.

    Commonly used norm types:

    `N1`
        The one norm.
    `N2`
        The two norm.
    `FROBENIUS`
        The Frobenius norm.
    `INFINITY`
        The infinity norm.

    See Also
    --------
    petsc.NormType
    """

    # native
    NORM_1 = ...
    NORM_2 = ...
    NORM_1_AND_2 = ...
    NORM_FROBENIUS = ...
    NORM_INFINITY = ...
    NORM_MAX = ...

    # aliases
    N1 = ...
    N2 = ...
    N12 = ...
    MAX = ...
    FROBENIUS = ...
    INFINITY = ...

    # extra aliases
    FRB = ...
    INF = ...
