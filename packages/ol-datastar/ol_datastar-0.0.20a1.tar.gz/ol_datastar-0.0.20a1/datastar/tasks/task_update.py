"""Task type for update task."""

from __future__ import annotations

from typing import Any, Dict, List, Optional, TYPE_CHECKING

from ..connection import Connection
from ..datastar_api import DatastarAPI

from ..task import Task

if TYPE_CHECKING:
    from ..macro import Macro


class UpdateTask(Task):
    """Update rows as part of a macro."""

    def __init__(
        self,
        macro: "Macro",
        *,
        name: str = "",
        description: str = "",
        target_connection: Optional[Connection] = None,
        target_table: Optional[str] = None,
        assignments: Optional[List[Dict[str, Any]]] = None,
        condition: Optional[str] = None,
        column_options: Optional[Dict[str, Any]] = None,
        run_configuration: Optional[Dict[str, Any]] = None,
        auto_join: bool = True,
        previous_task: Optional[Task] = None,
        persist: bool = True,
    ) -> None:
        self._target_connection_id = (
            target_connection._id if target_connection is not None else None
        )
        self.target_table = target_table or None
        self.assignments = list(assignments) if assignments is not None else None
        self.condition = condition or None
        self.column_options = (
            dict(column_options) if column_options is not None else None
        )
        self.run_configuration = (
            dict(run_configuration) if run_configuration is not None else None
        )

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
        return "update"

    def _to_configuration(self) -> Dict[str, Any]:
        configuration: Dict[str, Any] = {}

        target_section: Dict[str, Any] = {}
        self._put_attrs(
            target_section,
            [
                ("connectorId", "_target_connection_id"),
                ("table", "target_table"),
            ],
        )
        if target_section:
            configuration["target"] = target_section

        if self.assignments is not None:
            configuration["assignments"] = list(self.assignments)

        condition_section: Dict[str, Any] = {}
        if self.condition is not None:
            condition_section["expressionStr"] = self.condition
        if condition_section:
            configuration["condition"] = condition_section

        if self.column_options is not None:
            configuration["columnOptions"] = dict(self.column_options)

        if self.run_configuration is not None:
            configuration["runConfiguration"] = dict(self.run_configuration)

        return configuration

    def _from_configuration(self, configuration: Dict[str, Any]) -> None:
        target_section = configuration.get("target") or {}
        self._target_connection_id = target_section.get("connectorId")
        self.target_table = target_section.get("table")

        self.assignments = configuration.get("assignments")

        condition_section = configuration.get("condition")
        if condition_section is not None:
            self.condition = condition_section.get("expressionStr")
        else:
            self.condition = None

        self.column_options = configuration.get("columnOptions")
        self.run_configuration = configuration.get("runConfiguration")

    def _get_sub_type(self) -> Optional[str]:
        return None

    # ------------------------------------------------------------------
    # Connection property (uncached)

    @property
    def target_connection(self) -> Optional[Connection]:
        if not self._target_connection_id:
            return None
        if self._target_connection_id == DatastarAPI.SANDBOX_CONNECTOR_ID:
            return self.macro.project.get_sandbox()
        return Connection._read_by_id(self._target_connection_id)

    @target_connection.setter
    def target_connection(self, value: Connection) -> None:
        self._target_connection_id = value._id
