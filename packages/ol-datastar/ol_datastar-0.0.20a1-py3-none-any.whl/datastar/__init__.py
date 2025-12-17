from .connection import Connection
from .project import Project
from .macro import Macro
from .task import Task

# Re-export convenient subpackages
from . import connections as connections
from . import tasks as tasks

# Also expose common connection subclasses at top-level for convenience
from .connections import (
    DelimitedConnection,
    ExcelConnection,
    FrogModelConnection,
    OptiConnection,
    SandboxConnection,
)

# Also expose task subclasses at top-level for convenience
from .tasks import (
    DeleteTask,
    ExportTask,
    ImportTask,
    RunUtilityTask,
    RunPythonTask,
    RunSQLTask,
    UpdateTask,
)

# Single source of truth for version
from ._version import __version__

# Public API of the package
__all__ = [
    "Project",
    "Macro",
    "Task",
    "Connection",
    # Subpackages
    "connections",
    "tasks",
    # Connection subclasses
    "DelimitedConnection",
    "ExcelConnection",
    "FrogModelConnection",
    "OptiConnection",
    "SandboxConnection",
    # Task subclasses
    "ExportTask",
    "ImportTask",
    "RunUtilityTask",
    "RunPythonTask",
    "RunSQLTask",
    "UpdateTask",
    "DeleteTask",
    # Version
    "__version__",
]
