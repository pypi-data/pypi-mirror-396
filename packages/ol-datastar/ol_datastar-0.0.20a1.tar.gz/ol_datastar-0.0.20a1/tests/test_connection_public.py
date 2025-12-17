from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from datastar.connection import Connection
from datastar.connections.delimited_connection import DelimitedConnection
from datastar.connections.opti_connection import OptiConnection
from datastar.connections.frog_model_connection import FrogModelConnection
from datastar.project import Project


@pytest.fixture
def conn_api(monkeypatch: pytest.MonkeyPatch) -> MagicMock:
    api = MagicMock()
    # Create/update/delete (connector-based API)
    api.create_connector.return_value = {"id": "conn-1"}
    api.update_connector.return_value = None
    api.delete_connector.return_value = None
    # Collections
    api.get_connectors.return_value = {
        "items": [
            {"id": "c1", "name": "A", "type": "dsv"},
            {"id": "c2", "name": "B", "type": "optidb"},
        ]
    }
    # Patch Connection._api to return this mock
    monkeypatch.setattr(Connection, "_api", classmethod(lambda cls: api))
    return api


def test_get_connections_returns_all_names(conn_api: MagicMock):
    # Act
    all_names = Connection.get_connections()
    # Assert
    assert all_names == ["A", "B"]


def test_get_connections_filters_by_type_dsv(conn_api: MagicMock):
    # Act
    only_dsv = Connection.get_connections(connector_type="dsv")
    # Assert
    assert only_dsv == ["A"]


def test_get_connections_filters_by_type_dsv(conn_api: MagicMock):
    # Act
    only_dsv = Connection.get_connections(connector_type="optidb")
    # Assert
    assert only_dsv == ["B"]


def test_delimited_connection_persist_and_save_updates(conn_api: MagicMock):
    # Arrange
    c = DelimitedConnection(path="/tmp/file.csv", name="DSV1", description="Desc")
    # Assert (created/persisted)
    assert c._id == "conn-1"
    # Act
    c.description = "Updated"
    c.save()
    # Assert
    conn_api.update_connector.assert_called_once()


def test_delimited_connection_delete_calls_api(conn_api: MagicMock):
    # Arrange
    c = DelimitedConnection(path="/tmp/file.csv", name="DSV1", description="Desc")
    # Act
    c.delete()
    # Assert
    conn_api.delete_connector.assert_called_once_with("conn-1")


def test_project_get_sandbox_uses_special_id(api: MagicMock):
    # Arrange: Reuse the project fixture’s api monkeypatch from conftest for Project
    p = Project(name="SandboxProj")
    # Act
    sb = p.get_sandbox()
    from datastar.datastar_api import DatastarAPI

    assert sb._id == DatastarAPI.SANDBOX_CONNECTOR_ID


def test_get_connection_type_for_each_subclass(conn_api: MagicMock):
    # Delimited
    dsv = DelimitedConnection(path="/tmp/file.csv")
    assert dsv.get_connection_type() == "dsv"

    # Optilogic DB
    opti = OptiConnection(storage_id="store-1")
    assert opti.get_connection_type() == "optidb"

    # Cosmic Frog Model
    frog = FrogModelConnection(model_name="MyModel")
    assert frog.get_connection_type() == "cosmicfrog"
