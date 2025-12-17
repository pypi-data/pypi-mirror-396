"""Task type for SQL execution."""

from __future__ import annotations

from typing import Any, Dict, Optional, TYPE_CHECKING

from ..connection import Connection
from ..task import Task
from ..datastar_api import DatastarAPI

if TYPE_CHECKING:
    from ..macro import Macro


class RunSQLTask(Task):
    """Executes SQL statements as part of a macro."""

    def __init__(
        self,
        macro: "Macro",
        *,
        name: str = "",
        description: str = "",
        query: str = "",
        connection: Connection,
        auto_join: bool = True,
        previous_task: Optional[Task] = None,
        persist: bool = True,
    ):
        self.query = query
        self._connection_id = connection._id

        # Note: base will persist, which calls back into subclass, so call init here at end
        super().__init__(
            macro=macro,
            name=name,
            description=description,
            auto_join=auto_join,
            previous_task=previous_task,
            persist=persist,
        )

    # ------------------------------------------------------------------
    # Abstract method implementation

    def get_task_type(self) -> str:
        return "runsql"

    def _to_configuration(self) -> Dict[str, Any]:
        configuration: Dict[str, Any] = {"query": self.query}

        # Only emit target section when we have a connection id
        if self._connection_id is not None:
            configuration["target"] = {"connectorId": self._connection_id}

        return configuration

    def _from_configuration(self, configuration: Dict[str, Any]) -> None:
        # Be tolerant of missing fields/sections
        self.query = configuration.get("query")

        target_section = configuration.get("target")
        if target_section is not None:
            self._connection_id = target_section.get("connectorId")
        else:
            self._connection_id = None

    # ------------------------------------------------------------------
    # Connection property (uncached)

    @property
    def connection(self) -> Optional[Connection]:
        if not self._connection_id:
            return None
        if self._connection_id == DatastarAPI.SANDBOX_CONNECTOR_ID:
            return self.macro.project.get_sandbox()
        return Connection._read_by_id(self._connection_id)

    @connection.setter
    def connection(self, value: Connection) -> None:
        self._connection_id = value._id

    def _get_sub_type(self) -> Optional[str]:
        return None
