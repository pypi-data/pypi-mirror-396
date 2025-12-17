"""
High-level Connection helper.
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any, ClassVar, Dict, Optional

from .datastar_api import DatastarAPI
from ._defaults import DEFAULT_DESCRIPTION


class Connection(ABC):
    """Represents a connection scoped to a project."""

    _connection_counter: ClassVar[int] = 1
    _api_client: ClassVar[Optional[DatastarAPI]] = None

    def __init__(
        self,
        *,
        name: Optional[str] = None,
        description: Optional[str] = None,
        sandbox: Optional[bool] = False,
    ):
        super().__init__()
        self.name = name or self._next_connection_name()
        self.description = description or DEFAULT_DESCRIPTION

        # Note: Sandbox is a special case, it is not persisted
        if sandbox:
            self._id = DatastarAPI.SANDBOX_CONNECTOR_ID
        else:
            self._id: str = self._persist_new()

    @classmethod
    def get_connections(cls, connector_type: Optional[str] = None) -> list[str]:
        """
        Return the list of connection names.
        """
        response = cls._api().get_connectors()
        items = response["items"]

        # Apply filter
        if connector_type:
            items = [item for item in items if item["type"] == connector_type]

        return [item["name"] for item in items]

    @classmethod
    def get_connection(cls, name: str) -> "Connection":
        """
        Construct and return a Connection instance by its display name.

        Args:
            name: The display name of the existing connection.

        Returns:
            A Connection instance matching the connector's type.

        Raises:
            ValueError: If name is empty or no connection with that name exists.
        """

        connector_id = cls._name_to_id(name)
        if not connector_id:
            raise ValueError(f"Connection '{name}' not found.")

        return cls._read_by_id(connector_id)

    def save(self) -> None:
        """
        Persist connection changes to the server.
        """
        assert self._id

        # Build configuration payload similar to creation, excluding top-level fields
        self._api().update_connector(self._id, self._to_json())

    def delete(self) -> None:

        if not self._id:
            return

        self._api().delete_connector(self._id)

    def get_connection_type(self) -> str:
        """Return the connector type string for this connection."""
        return self._to_configuration()["type"]

    # ------------------------------------------------------------------
    # Internal

    @classmethod
    def _next_connection_name(cls) -> str:
        counter = cls._connection_counter
        cls._connection_counter += 1
        return f"Connection {counter}"

    @classmethod
    def _api(cls) -> DatastarAPI:
        if cls._api_client is None:
            cls._api_client = DatastarAPI()
        return cls._api_client

    @classmethod
    def _name_to_id(cls, name: str) -> str | None:
        """
        Resolve a connector identifier from its display name.

        Args:
            name: Connector name to search for.

        Returns:
            The connector UUID as a string.

        Raises:
            ValueError: If the name is empty or no connector matches.
        """

        if not name or not name.strip():
            raise ValueError("Connector name is required.")

        target = name.strip().lower()
        response = cls._api().get_connectors()
        items = response.get("items")
        if not isinstance(items, list):
            raise ValueError("Expected 'items' list in connectors response.")
        for entry in items:
            candidate = entry.get("name")
            if isinstance(candidate, str) and candidate.strip().lower() == target:
                connector_id = entry.get("id")
                if connector_id:
                    return str(connector_id)

        return None

    # ------------------------------------------------------------------
    # Lifecycle helpers

    def _persist_new(self) -> str:
        resp = self._api().create_connector(self._to_json())
        # create_connector returns the created object; return its id for consistency
        return resp["id"]

    # ------------------------------------------------------------------
    # JSON translation helpers

    def _to_json(self) -> Dict[str, Any]:

        configuration: Dict[str, Any] = {
            "name": self.name,
            "description": self.description,
        }

        # Note: Unlike Task, connection format is flattened
        configuration.update(self._to_configuration())

        return configuration

    def _from_json(self, payload: Dict[str, Any]) -> None:

        self._id = payload["id"]
        self.name = payload["name"]
        self.description = payload.get("description")

        # Add subclass data via overridden method
        self._from_configuration(payload)

    # ------------------------------------------------------------------
    # Factory helpers

    @classmethod
    def _from_payload(cls, payload: Dict[str, Any]) -> "Connection":
        """
        Construct a Connection subclass instance from an API payload
        without invoking the subclass __init__ (no persistence).

        The payload is expected to be a flattened connector JSON that includes
        at least: id, name, description, type, and fields relevant to the
        specific connection type.
        """

        # Determine subclass from connection type using central registry
        conn_type = payload.get("type")
        if not isinstance(conn_type, str) or not conn_type:
            raise ValueError("Connector payload missing 'type'.")

        # Late import to avoid circular dependencies during module import
        from .connection_registry import _get_connection_class

        subclass = _get_connection_class(conn_type)

        # Allocate instance without calling __init__
        instance = subclass.__new__(subclass)

        # Populate fields via the base JSON loader which delegates to subclass
        # _from_configuration without persisting
        Connection._from_json(instance, payload)

        return instance

    @classmethod
    def _read_by_id(cls, connector_id: str) -> "Connection":
        """
        Retrieve connector details by id and construct the appropriate
        Connection subclass instance without persisting.
        """

        payload = cls._api().get_connector(connector_id)

        # Expect a single connector object; handle optional {"item": {...}} wrapper
        if isinstance(payload, dict) and isinstance(payload.get("item"), dict):
            payload = payload["item"]
        if not isinstance(payload, dict):
            raise ValueError("Expected connector payload object.")

        return cls._from_payload(payload)

    # ------------------------------------------------------------------
    # Abstract methods

    @abstractmethod
    def _from_configuration(self, payload: Dict[str, Any]) -> None:
        assert False

    @abstractmethod
    def _to_configuration(self) -> Dict[str, Any]:
        assert False
