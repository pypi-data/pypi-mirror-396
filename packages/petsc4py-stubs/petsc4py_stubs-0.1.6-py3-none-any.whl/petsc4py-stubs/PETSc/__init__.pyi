"""Type stubs for petsc4py.PETSc module."""

# Re-export all types from submodules

# Base types
# Application Ordering types
from .AO import AO, AOType

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
from .Device import Device, DeviceContext, DeviceJoinMode, DeviceType, StreamType
from .DM import DM, DMBoundaryType, DMPolytopeType, DMReorderDefaultFlag, DMType
from .DMComposite import DMComposite
from .DMDA import DA, DMDA, DMDAElementType, DMDAInterpolationType, DMDAStencilType

# DMLabel types
from .DMLabel import DMLabel
from .DMPlex import DMPlex, DMPlexTransform, DMPlexTransformType
from .DMShell import DMShell
from .DMStag import DMStag, DMStagStencilLocation, DMStagStencilType
from .DMSwarm import (
    CellDM,
    DMSwarm,
    DMSwarmCollectType,
    DMSwarmMigrateType,
    DMSwarmPICLayoutType,
    DMSwarmType,
)
from .DMUtils import DMInterpolation
from .DS import DS, DSType
from .DT import Quad

# Error module
from .Error import Error

# FE module
from .FE import FE, FEType

# Index Set types
from .IS import IS, ISType, LGMap
from .KSP import KSP, KSPConvergedReason, KSPHPDDMType, KSPNormType, KSPType

# Log module
from .Log import Log, LogClass, LogEvent, LogStage
from .Mat import (
    Mat,
    MatAssemblyType,
    MatDuplicateOption,
    MatFactorShiftType,
    MatInfoType,
    MatOption,
    MatOrderingType,
    MatSolverType,
    MatSORType,
    MatStencil,
    MatStructure,
    MatType,
    NullSpace,
)

# MatPartitioning module
from .MatPartitioning import MatPartitioning, MatPartitioningType
from .Object import Object

# Options
from .Options import Options

# Partitioner module
from .Partitioner import Partitioner, PartitionerType
from .PC import (
    PC,
    PCASMType,
    PCCompositeType,
    PCDeflationSpaceType,
    PCFailedReason,
    PCFieldSplitSchurFactType,
    PCFieldSplitSchurPreType,
    PCGAMGType,
    PCGASMType,
    PCHPDDMCoarseCorrectionType,
    PCMGCycleType,
    PCMGType,
    PCPatchConstructType,
    PCSide,
    PCType,
)
from .Random import Random, RandomType

# Regressor module
from .Regressor import Regressor, RegressorLinearType, RegressorType
from .Scatter import Scatter, ScatterMode, ScatterType

# Section types
from .Section import Section

# Star Forest types
from .SF import SF, SFType
from .SNES import (
    SNES,
    SNESConvergedReason,
    SNESLineSearch,
    SNESLineSearchType,
    SNESNewtonALCorrectionType,
    SNESNormSchedule,
    SNESType,
)

# Space module
from .Space import DualSpace, DualSpaceType, Space, SpaceType

# Sys module
from .Sys import Sys

# TAO module
from .TAO import (
    TAO,
    TAOALMMType,
    TAOBNCGType,
    TAOConvergedReason,
    TAOLineSearch,
    TAOLineSearchConvergedReason,
    TAOLineSearchType,
    TAOType,
)

# TS module
from .TS import (
    TS,
    TSARKIMEXType,
    TSConvergedReason,
    TSDIRKType,
    TSEquationType,
    TSExactFinalTime,
    TSProblemType,
    TSRKType,
    TSType,
)
from .Vec import Vec, VecOption, VecType
from .Viewer import (
    Viewer,
    ViewerDrawSize,
    ViewerFileMode,
    ViewerFormat,
    ViewerHDF5,
    ViewerType,
)

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
    "DeviceType",
    "StreamType",
    "DeviceJoinMode",
    # Options module
    "Options",
    # Index Set types
    "IS",
    "ISType",
    "LGMap",
    # Application Ordering module
    "AO",
    "AOType",
    # Section module
    "Section",
    # Star Forest module
    "SF",
    "SFType",
    # DMLabel module
    "DMLabel",
    # Mat module
    "Mat",
    "MatType",
    "MatOption",
    "MatAssemblyType",
    "MatInfoType",
    "MatStructure",
    "MatDuplicateOption",
    "MatOrderingType",
    "MatSolverType",
    "MatFactorShiftType",
    "MatSORType",
    "MatStencil",
    "NullSpace",
    # Vec module
    "Vec",
    "VecType",
    "VecOption",
    # DM module
    "DM",
    "DMType",
    "DMBoundaryType",
    "DMPolytopeType",
    "DMReorderDefaultFlag",
    "FE",
    # DMDA module
    "DMDA",
    "DMDAStencilType",
    "DMDAInterpolationType",
    "DMDAElementType",
    "DA",
    # DMComposite module
    "DMComposite",
    # DMShell module
    "DMShell",
    # DMStag module
    "DMStag",
    "DMStagStencilType",
    "DMStagStencilLocation",
    # DMSwarm module
    "DMSwarm",
    "DMSwarmType",
    "DMSwarmMigrateType",
    "DMSwarmCollectType",
    "DMSwarmPICLayoutType",
    "CellDM",
    # DMUtils module
    "DMInterpolation",
    # DMPlex module
    "DMPlex",
    "DMPlexTransformType",
    "DMPlexTransform",
    # DS module
    "DS",
    "DSType",
    # DT module
    "Quad",
    # FE module
    "FEType",
    # Log module
    "Log",
    "LogStage",
    "LogClass",
    "LogEvent",
    # Regressor module
    "Regressor",
    "RegressorType",
    "RegressorLinearType",
    # KSP module
    "KSP",
    "KSPType",
    "KSPNormType",
    "KSPConvergedReason",
    "KSPHPDDMType",
    # PC module
    "PC",
    "PCType",
    "PCSide",
    "PCASMType",
    "PCGASMType",
    "PCMGType",
    "PCMGCycleType",
    "PCGAMGType",
    "PCCompositeType",
    "PCFieldSplitSchurPreType",
    "PCFieldSplitSchurFactType",
    "PCPatchConstructType",
    "PCHPDDMCoarseCorrectionType",
    "PCDeflationSpaceType",
    "PCFailedReason",
    # Scatter module
    "Scatter",
    "ScatterType",
    "ScatterMode",
    # Viewer module
    "Viewer",
    "ViewerType",
    "ViewerFormat",
    "ViewerFileMode",
    "ViewerDrawSize",
    "ViewerHDF5",
    # Random module
    "Random",
    "RandomType",
    # SNES module
    "SNES",
    "SNESType",
    "SNESNormSchedule",
    "SNESConvergedReason",
    "SNESNewtonALCorrectionType",
    "SNESLineSearch",
    "SNESLineSearchType",
    # Error module
    "Error",
    # MatPartitioning module
    "MatPartitioning",
    "MatPartitioningType",
    # Partitioner module
    "Partitioner",
    "PartitionerType",
    # Space module
    "Space",
    "SpaceType",
    "DualSpace",
    "DualSpaceType",
    # Sys module
    "Sys",
    # TAO module
    "TAO",
    "TAOType",
    "TAOConvergedReason",
    "TAOBNCGType",
    "TAOALMMType",
    "TAOLineSearch",
    "TAOLineSearchType",
    "TAOLineSearchConvergedReason",
    # TS module
    "TS",
    "TSType",
    "TSRKType",
    "TSARKIMEXType",
    "TSDIRKType",
    "TSProblemType",
    "TSEquationType",
    "TSExactFinalTime",
    "TSConvergedReason",
]
