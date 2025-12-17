"""Task type for data import operations."""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple, TYPE_CHECKING

from ..connection import Connection
from ..task import Task
from ..datastar_api import DatastarAPI

if TYPE_CHECKING:
    from ..macro import Macro


class ImportTask(Task):
    """Loads data into the project environment."""

    def __init__(
        self,
        macro: "Macro",
        *,
        task_id: str = "",
        name: str = "",
        description: str = "",
        auto_join: bool = True,
        previous_task: Optional[Task] = None,
        source_connection: Connection,
        destination_connection: Connection,
        source_table: str = "",
        destination_table: str = "",
        destination_table_type: str = "new",
        destination_table_action: str = "replace",
        condition: Optional[str] = None,
        mappings: Optional[List[Tuple[str, str]]] = None,
        run_configuration: Optional[Dict[str, Any]] = None,
        persist: bool = True,
    ) -> None:
        from ..connections.delimited_connection import DelimitedConnection

        # No source table needed for a dsv connection
        assert source_table or isinstance(source_connection, DelimitedConnection)

        self._source_connection_id = source_connection._id
        self._destination_connection_id = destination_connection._id

        # For delimited-file sources, always use the connection path as the
        # source table. Any provided source_table is ignored for this type.
        if isinstance(source_connection, DelimitedConnection):
            self.source_table = str(source_connection.path)
        else:
            self.source_table = str(source_table)
        self.destination_table = destination_table
        self.destination_table_type = destination_table_type
        self.destination_table_action = str(
            destination_table_action or "replace"
        ).lower()
        self.condition = condition or None
        if mappings:
            self.mappings = list(mappings)
        else:
            self.mappings = None
        self.run_configuration = (
            dict(run_configuration) if run_configuration is not None else None
        )

        # Note: base will persist, which calls back into subclass, so call init here at end
        super().__init__(
            task_id=task_id,
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
        return "import"

    def _to_configuration(self) -> Dict[str, Any]:
        configuration: Dict[str, Any] = {}

        # Source: include only provided fields
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

        # Destination: include only provided fields
        if self._destination_connection_id is not None:
            dest: Dict[str, Any] = {"type": "connector"}
            self._put_attrs(
                dest,
                [
                    ("connectorId", "_destination_connection_id"),
                    ("tableAction", "destination_table_action"),
                    ("tableType", "destination_table_type"),
                ],
            )

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

        # Top-level optionals
        self._put_attrs(configuration, ["condition", "mappings"])
        if self.run_configuration is not None:
            configuration["runConfiguration"] = dict(self.run_configuration)

        return configuration

    def _from_configuration(self, configuration: Dict[str, Any]) -> None:

        # Be tolerant of missing sections
        source_section = configuration.get("source") or {}
        destination_section = configuration.get("destination")

        self._source_connection_id = source_section.get("connectorId")
        self.source_table = source_section.get("table")

        if destination_section is not None:
            self._destination_connection_id = destination_section.get("connectorId")
            self.destination_table = destination_section.get(
                "newTableName"
            ) or destination_section.get("table")
            self.destination_table_type = destination_section.get("tableType")
            self.destination_table_action = destination_section.get("tableAction")
        else:
            self._destination_connection_id = None
            self.destination_table = None
            self.destination_table_type = None
            self.destination_table_action = None

        self.condition = configuration.get("condition")
        # Preserve absence (None) when mappings key is not present
        self.mappings = configuration.get("mappings")
        self.run_configuration = configuration.get("runConfiguration")

    # ------------------------------------------------------------------
    # Connection properties

    @property
    def source_connection(self) -> Connection:
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
    def destination_connection(self, value: Connection) -> None:
        self._destination_connection_id = value._id

    def _get_sub_type(self) -> Optional[str]:
        return None
