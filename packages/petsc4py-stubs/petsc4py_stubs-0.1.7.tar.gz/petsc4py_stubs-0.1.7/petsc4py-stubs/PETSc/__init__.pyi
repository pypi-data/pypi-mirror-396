"""Type stubs for petsc4py.PETSc module."""

# Re-export all types from submodules

# Base types
# Application Ordering types
from .AO import AO

# Comm type
from .Comm import COMM_NULL, COMM_SELF, COMM_WORLD, Comm

# Const module (basic constants and enums)
from .Const import (
    CURRENT,
    DECIDE,
    DEFAULT,
    DETERMINE,
    INFINITY,
    NINFINITY,
    PINFINITY,
    UNLIMITED,
    InsertMode,
    NormType,
    ScatterMode,
)

# Device types
from .Device import Device, DeviceContext
from .DM import DM
from .DMComposite import DMComposite
from .DMDA import DMDA

# DMLabel types
from .DMLabel import DMLabel
from .DMPlex import DMPlex, DMPlexTransform, DMPlexTransformType
from .DMShell import DMShell
from .DMStag import DMStag
from .DMSwarm import (
    CellDM,
    DMSwarm,
)
from .DMUtils import DMInterpolation
from .DS import DS
from .DT import Quad

# Error module
from .Error import Error

# FE module
from .FE import FE

# Index Set types
from .IS import IS, LGMap
from .KSP import KSP

# Log module
from .Log import Log, LogClass, LogEvent, LogStage
from .Mat import (
    Mat,
    NullSpace,
)

# MatPartitioning module
from .MatPartitioning import MatPartitioning
from .Object import Object

# Options
from .Options import Options

# Partitioner module
from .Partitioner import Partitioner
from .PC import PC
from .Random import Random

# Regressor module
from .Regressor import Regressor, RegressorLinearType
from .Scatter import Scatter, ScatterMode

# Section types
from .Section import Section

# Star Forest types
from .SF import SF
from .SNES import (
    SNES,
    SNESLineSearch,
)

# Space module
from .Space import DualSpace, Space

# Sys module
from .Sys import Sys

# TAO module
from .TAO import (
    TAO,
    TAOLineSearch,
)

# TS module
from .TS import (
    TS,
)
from .Vec import Vec
from .Viewer import (
    Viewer,
    ViewerHDF5,
)

# Garbage collection functions
def garbage_cleanup(comm: Comm | None = ...) -> None:
    """Clean up unused PETSc objects.

    Collective.

    Parameters
    ----------
    comm : Comm | None, optional
        MPI communicator. If not provided or None, COMM_WORLD is used.

    Returns
    -------
    None
    """
    ...

def garbage_view(comm: Comm | None = ...) -> None:
    """Print summary of the garbage PETSc objects.

    Collective.

    Parameters
    ----------
    comm : Comm | None, optional
        MPI communicator for printing. If not provided, COMM_WORLD is used.

    Returns
    -------
    None
    """
    ...

__all__ = [
    # Base types
    "Object",
    # Const module
    "DECIDE",
    "DEFAULT",
    "DETERMINE",
    "CURRENT",
    "UNLIMITED",
    "INFINITY",
    "NINFINITY",
    "PINFINITY",
    "InsertMode",
    "ScatterMode",
    "NormType",
    # Comm module
    "Comm",
    "COMM_NULL",
    "COMM_SELF",
    "COMM_WORLD",
    # Device module
    "Device",
    "DeviceContext",
    # Options module
    "Options",
    # Index Set types
    "IS",
    "LGMap",
    # Application Ordering module
    "AO",
    # Section module
    "Section",
    # Star Forest module
    "SF",
    # DMLabel module
    "DMLabel",
    # Mat module
    "Mat",
    "NullSpace",
    # Vec module
    "Vec",
    # DM module
    "DM",
    "FE",
    # DMDA module
    "DMDA",
    # DMComposite module
    "DMComposite",
    # DMShell module
    "DMShell",
    # DMStag module
    "DMStag",
    # DMSwarm module
    "DMSwarm",
    "CellDM",
    # DMUtils module
    "DMInterpolation",
    # DMPlex module
    "DMPlex",
    "DMPlexTransformType",
    "DMPlexTransform",
    # DS module
    "DS",
    # DT module
    "Quad",
    # Log module
    "Log",
    "LogStage",
    "LogClass",
    "LogEvent",
    # Regressor module
    "Regressor",
    "RegressorLinearType",
    # KSP module
    "KSP",
    # PC module
    "PC",
    # Scatter module
    "Scatter",
    "ScatterMode",
    # Viewer module
    "Viewer",
    "ViewerHDF5",
    # Random module
    "Random",
    # SNES module
    "SNES",
    "SNESLineSearch",
    # Error module
    "Error",
    # MatPartitioning module
    "MatPartitioning",
    # Partitioner module
    "Partitioner",
    # Space module
    "Space",
    "DualSpace",
    # Sys module
    "Sys",
    # TAO module
    "TAO",
    "TAOLineSearch",
    # TS module
    "TS",
    # Garbage collection
    "garbage_cleanup",
    "garbage_view",
]
