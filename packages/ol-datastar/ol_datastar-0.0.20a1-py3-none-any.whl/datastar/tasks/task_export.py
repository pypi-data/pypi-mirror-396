"""Task type for exporting data."""

from __future__ import annotations

from typing import Any, Dict, List, Tuple, Optional, TYPE_CHECKING

from ..connection import Connection

from ..task import Task
from ..datastar_api import DatastarAPI

if TYPE_CHECKING:
    from ..macro import Macro


class ExportTask(Task):
    """Exports project data to an external destination."""

    def __init__(
        self,
        macro: "Macro",
        *,
        name: str = "",
        description: str = "",
        source_connection: Optional[Connection] = None,
        destination_connection: Optional[Connection] = None,
        source_table: Optional[str] = None,
        destination_table: Optional[str] = None,
        destination_table_type: Optional[str] = None,
        destination_table_action: Optional[str] = None,
        condition: Optional[str] = None,
        mappings: Optional[List[Tuple[str, str]]] = None,
        file_name: Optional[str] = None,
        run_configuration: Optional[Dict[str, Any]] = None,
        auto_join: bool = True,
        previous_task: Optional[Task] = None,
        persist: bool = True,
    ):
        self._source_connection_id = (
            source_connection._id if source_connection is not None else None
        )
        if destination_connection is not None:
            self._destination_connection_id = destination_connection._id
        else:
            self._destination_connection_id = None

        # Optional fields use None when unset to allow transparent round-trips
        self.source_table = source_table or None
        self.destination_table = destination_table or None
        self.destination_table_type = destination_table_type or None
        self.destination_table_action = destination_table_action or None
        self.condition = condition or None
        if mappings:
            self.mappings = list(mappings)
        else:
            self.mappings = None
        self.file_name = file_name or None
        self.run_configuration = (
            dict(run_configuration) if run_configuration is not None else None
        )

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
        return "export"

    def _to_configuration(self) -> Dict[str, Any]:
        configuration: Dict[str, Any] = {}

        # Source connection: include only provided fields
        source_section: Dict[str, Any] = {}
        self._put_attrs(
            source_section,
            [
                ("connectorId", "_source_connection_id"),
                ("table", "source_table"),
            ],
        )
        if source_section:
            configuration["source"] = source_section

        # Destination (emit only when there is data to send)
        if self._destination_connection_id is not None:
            dest: Dict[str, Any] = {"type": "dataConnection"}
            self._put_attrs(
                dest,
                [
                    ("connectorId", "_destination_connection_id"),
                    ("tableAction", "destination_table_action"),
                    ("tableType", "destination_table_type"),
                ],
            )

            # Only emit table naming if we know the type and name
            if (
                self.destination_table_type == "new"
                and self.destination_table is not None
            ):
                dest["newTableName"] = self.destination_table
            elif (
                self.destination_table_type is not None
                and self.destination_table_type != "new"
                and self.destination_table is not None
            ):
                dest["table"] = self.destination_table

            configuration["destination"] = dest
        elif self.file_name is not None:
            configuration["destination"] = {"type": "file", "fileName": self.file_name}
        # else: omit destination entirely

        self._put_attrs(configuration, ["condition", "mappings"])

        if self.run_configuration is not None:
            configuration["runConfiguration"] = dict(self.run_configuration)

        return configuration

    def _from_configuration(self, configuration: Dict[str, Any]) -> None:

        # Be tolerant of missing sections in legacy or partial payloads
        source_section = configuration.get("source") or {}
        destination_section = configuration.get("destination")

        self._source_connection_id = source_section.get("connectorId")
        self.source_table = source_section.get("table")

        if destination_section is not None:
            dest_type_raw = destination_section.get("type")
            if not dest_type_raw:
                dest_type_raw = (
                    "dataConnection"
                    if destination_section.get("connectorId")
                    else "file"
                )
            dest_type = dest_type_raw.lower()
            if dest_type == "file":
                # File mode
                self.file_name = destination_section.get("fileName")
                self._destination_connection_id = None
                self.destination_table = None
                self.destination_table_type = None
                self.destination_table_action = None
            else:
                # Connector mode
                self.file_name = None
                self._destination_connection_id = destination_section.get("connectorId")
                self.destination_table = destination_section.get(
                    "newTableName"
                ) or destination_section.get("table")
                self.destination_table_type = destination_section.get("tableType")
                self.destination_table_action = destination_section.get("tableAction")
        else:
            # No destination section provided; ensure attributes exist
            self._destination_connection_id = None
            self.file_name = None
            self.destination_table = None
            self.destination_table_type = None
            self.destination_table_action = None

        self.condition = configuration.get("condition")

        self.mappings = configuration.get("mappings")
        self.run_configuration = configuration.get("runConfiguration")

    def _get_sub_type(self) -> Optional[str]:
        if self._destination_connection_id:
            return "db"
        if self.file_name:
            return "dsv"
        return None

    # ------------------------------------------------------------------
    # Connection properties

    @property
    def source_connection(self) -> Optional[Connection]:
        if not self._source_connection_id:
            return None
        if self._source_connection_id == DatastarAPI.SANDBOX_CONNECTOR_ID:
            return self.macro.project.get_sandbox()
        return Connection._read_by_id(self._source_connection_id)

    @source_connection.setter
    def source_connection(self, value: Connection) -> None:
        self._source_connection_id = value._id

    @property
    def destination_connection(self) -> Optional[Connection]:
        if not self._destination_connection_id:
            return None
        if self._destination_connection_id == DatastarAPI.SANDBOX_CONNECTOR_ID:
            return self.macro.project.get_sandbox()
        return Connection._read_by_id(self._destination_connection_id)

    @destination_connection.setter
    def destination_connection(self, value: Optional[Connection]) -> None:
        self._destination_connection_id = value._id if value is not None else None
