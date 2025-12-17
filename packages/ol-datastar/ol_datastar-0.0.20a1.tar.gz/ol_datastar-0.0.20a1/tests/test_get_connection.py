from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from datastar.connection import Connection
from datastar.connections.delimited_connection import DelimitedConnection
from datastar.connections.opti_connection import OptiConnection
from datastar.connections.frog_model_connection import FrogModelConnection


def _mock_api_for_single_connector(name: str, conn_id: str, payload: dict) -> MagicMock:
    api = MagicMock()
    # get_connectors used to resolve name -> id
    api.get_connectors.return_value = {
        "items": [
            {"id": conn_id, "name": name, "type": payload.get("type")},
        ]
    }
    # get_connector used to read full details
    api.get_connector.return_value = payload
    return api


def test_get_connection_returns_delimited_with_fields(monkeypatch: pytest.MonkeyPatch):
    name = "CSV Customers"
    conn_id = "c-dsv-1"
    payload = {
        "id": conn_id,
        "name": name,
        "description": "A delimited file",
        "type": "dsv",
        "path": "/data/customers.csv",
        "delimiter": ",",
        "encoding": "utf-8",
    }

    api = _mock_api_for_single_connector(name, conn_id, payload)
    monkeypatch.setattr(Connection, "_api", classmethod(lambda cls: api))

    conn = Connection.get_connection(name)
    assert isinstance(conn, DelimitedConnection)
    assert conn.name == name
    assert conn.description == "A delimited file"
    assert conn.path == "/data/customers.csv"
    assert conn.delimiter == ","
    assert conn.encoding == "utf-8"


def test_get_connection_returns_opti_with_fields(monkeypatch: pytest.MonkeyPatch):
    name = "Opti DB"
    conn_id = "c-opti-1"
    payload = {
        "id": conn_id,
        "name": name,
        "description": "Optilogic DB",
        "type": "optidb",
        "schema": "analytics",
        "storageId": "store-123",
    }

    api = _mock_api_for_single_connector(name, conn_id, payload)
    monkeypatch.setattr(Connection, "_api", classmethod(lambda cls: api))

    conn = Connection.get_connection(name)
    assert isinstance(conn, OptiConnection)
    assert conn.name == name
    assert conn.schema == "analytics"
    assert conn.storage_id == "store-123"
    assert conn.storage_name is None


def test_get_connection_returns_frog_with_fields(monkeypatch: pytest.MonkeyPatch):
    name = "Frog Model"
    conn_id = "c-frog-1"
    payload = {
        "id": conn_id,
        "name": name,
        "description": "Cosmic Frog",
        "type": "cosmicfrog",
        "modelName": "MyModel",
    }

    api = _mock_api_for_single_connector(name, conn_id, payload)
    monkeypatch.setattr(Connection, "_api", classmethod(lambda cls: api))

    conn = Connection.get_connection(name)
    assert isinstance(conn, FrogModelConnection)
    assert conn.name == name
    assert conn.model_name == "MyModel"
    assert conn.storage_id is None
