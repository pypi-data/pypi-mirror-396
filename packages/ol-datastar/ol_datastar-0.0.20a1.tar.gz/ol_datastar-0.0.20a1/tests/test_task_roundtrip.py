from __future__ import annotations

from typing import Any, Dict, Type

import json

from datastar.tasks.task_import import ImportTask
from datastar.tasks.task_export import ExportTask
from datastar.tasks.task_run_sql import RunSQLTask
from datastar.tasks.task_run_python import RunPythonTask
from datastar.tasks.task_start import StartTask
from datastar.task import Task


class MacroStub:
    def __init__(self) -> None:
        self._counter = 1

    def _next_task_name(self) -> str:
        name = f"Task {self._counter}"
        self._counter += 1
        return name


class ConnStub:
    def __init__(self, id_value: str) -> None:
        self._id = id_value


def round_trip(cls: Type[Task], original: Task) -> Dict[str, Any]:
    payload = original._to_json()

    # Create a fresh instance without running subclass __init__
    macro = MacroStub()
    new_task = cls.__new__(cls)  # type: ignore[misc]
    Task.__init__(
        new_task,
        macro,
        task_id="test-id",
        name="temp",
        description="temp",
        persist=False,
    )
    new_task._from_json(payload)

    return {
        "original": original._to_json(),
        "restored": new_task._to_json(),
    }


def test_round_trip_import_task() -> None:
    # Arrange
    macro = MacroStub()
    src = ConnStub("src-1")
    dst = ConnStub("dst-1")
    t = ImportTask(
        macro,
        name="Imp",
        description="Import desc",
        source_connection=src,
        destination_connection=dst,
        source_table="s_table",
        destination_table="d_table",
        destination_table_type="new",
        destination_table_action="replace",
        condition="x > 1",
        mappings=[("a", "b")],
        persist=False,
    )
    # Act
    data = round_trip(ImportTask, t)
    # Assert
    assert data["original"] == data["restored"]


def test_round_trip_export_task() -> None:
    # Arrange
    macro = MacroStub()
    src = ConnStub("src-2")
    dst = ConnStub("dst-2")
    t = ExportTask(
        macro,
        name="Exp",
        description="Export desc",
        source_connection=src,
        destination_connection=dst,
        source_table="s_table",
        destination_table="d_table",
        destination_table_type="existing",
        destination_table_action="append",
        condition="y < 10",
        mappings=[("c", "d")],
        file_name="",  # use connector destination variant
        persist=False,
    )
    # Act
    data = round_trip(ExportTask, t)
    # Assert
    assert data["original"] == data["restored"]


def test_round_trip_run_sql_task() -> None:
    # Arrange
    macro = MacroStub()
    conn = ConnStub("conn-3")
    t = RunSQLTask(
        macro,
        name="SQL",
        description="SQL desc",
        query="select 1",
        connection=conn,
        persist=False,
    )
    # Act
    data = round_trip(RunSQLTask, t)
    # Assert
    assert data["original"] == data["restored"]


def test_round_trip_run_python_task() -> None:
    # Arrange
    macro = MacroStub()
    t = RunPythonTask(
        macro,
        name="Py",
        description="Py desc",
        filename="script.py",
        directory_path="/path/to",
        persist=False,
    )
    # Act
    data = round_trip(RunPythonTask, t)
    # Assert
    assert data["original"] == data["restored"]


def test_round_trip_start_task() -> None:
    # Arrange
    macro = MacroStub()
    t = StartTask(macro)
    # Act
    data = round_trip(StartTask, t)
    # Assert
    assert data["original"] == data["restored"]
