from __future__ import annotations

from typing import Any, Dict
from unittest.mock import MagicMock

import pytest

from datastar.project import Project


def test_create_and_persist_project(api: MagicMock):
    # Arrange
    p = Project(name="MyProj", description="Desc")
    # Assert (initial persistence)
    assert p._is_persisted()
    # Act
    p.name = "Renamed"
    p.save()
    # Assert
    api.update_project.assert_called_once_with(
        p._id, name="Renamed", description=p.description
    )


def test_delete_project_calls_api(api: MagicMock):
    # Arrange
    p = Project(name="DeleteMe")
    # Act
    p.delete()
    # Assert
    api.delete_project.assert_called_once_with(p._id)


def test_get_projects_classmethod(api: MagicMock, monkeypatch: pytest.MonkeyPatch):
    # Arrange
    api._get_projects_json.return_value = [
        {"id": "p1", "name": "A"},
        {"id": "p2", "name": "B"},
    ]
    # Act
    names = Project.get_projects()
    # Assert
    assert names == ["A", "B"]


def test_connect_to_uses_lookup(api: MagicMock):
    # Arrange
    api.build_project_lookup.return_value = {
        "myproj": {"id": "p123", "name": "MyProj", "description": "D"}
    }
    # Act
    p = Project.connect_to("MyProj")
    # Assert
    assert isinstance(p, Project)
    assert p._is_persisted()


def test_connect_to_raises_when_not_found(api: MagicMock):
    # Arrange
    api.build_project_lookup.return_value = {
        "other": {"id": "p2", "name": "Other", "description": "D"}
    }
    # Act / Assert
    with pytest.raises(ValueError):
        Project.connect_to("Missing")


def test_macro_lifecycle_methods(api: MagicMock):
    # Arrange: get_macros list drives get_macro/delete_macro
    api.get_macros.return_value = {
        "items": [
            {"id": "m1", "name": "M1", "description": "desc"},
        ]
    }
    p = Project(name="MacrosProj")
    # Act: Add macro uses create_macro under Macro
    m = p.add_macro(name="NewM")
    # Assert
    assert m._id == "macro-1"
    # Act: get_macros returns names
    names = p.get_macros()
    # Assert
    assert names == ["M1"]
    # Act: get_macro finds by name
    got = p.get_macro("M1")
    # Assert
    assert got is not None and got._id == "m1"
    # Act: delete_macro deletes the found macro
    p.delete_macro("M1")
    # Assert
    api.delete_macro.assert_called_with(p._id, "m1")


def test_get_sandbox_returns_connection(api: MagicMock):
    # Arrange
    p = Project(name="SB")
    # Act
    sb = p.get_sandbox()
    # Assert: Sandbox connection uses a special id; no API call expected for creation here
    from datastar.datastar_api import DatastarAPI

    assert sb._id == DatastarAPI.SANDBOX_CONNECTOR_ID
