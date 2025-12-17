from __future__ import annotations

from typing import Any, Dict, Type

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


def build_and_roundtrip(cls: Type[Task], original: Task) -> Dict[str, Any]:
    payload = original._to_json()
    macro = MacroStub()
    fresh = cls.__new__(cls)  # type: ignore[misc]
    Task.__init__(
        fresh, macro, task_id="temp", name="temp", description="temp", persist=False
    )
    fresh._from_json(payload)
    return {"payload": payload, "restored": fresh._to_json(), "fresh": fresh}


def test_import_task_json_contract() -> None:
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
        mappings=[{"sourceColumn": "a", "targetColumn": "b"}],
        persist=False,
    )
    # Act
    data = build_and_roundtrip(ImportTask, t)
    # Assert
    assert data["payload"] == data["restored"]


def test_export_task_connector_mode_json_contract() -> None:
    # Arrange
    macro = MacroStub()
    src = ConnStub("src-2")
    dst = ConnStub("dst-2")
    t = ExportTask(
        macro,
        name="ExpConn",
        description="Export conn",
        source_connection=src,
        destination_connection=dst,
        source_table="s_table",
        destination_table="d_table",
        destination_table_type="existing",
        destination_table_action="append",
        condition="y < 10",
        mappings=[{"sourceColumn": "c", "targetColumn": "d"}],
        file_name="",
        persist=False,
    )
    # Act
    data = build_and_roundtrip(ExportTask, t)
    # Assert
    assert data["payload"] == data["restored"]


def test_export_task_file_mode_json_contract() -> None:
    # Arrange
    macro = MacroStub()
    src = ConnStub("src-3")
    t = ExportTask(
        macro,
        name="ExpFile",
        description="Export file",
        source_connection=src,
        destination_connection=None,
        source_table="s_table",
        destination_table="",
        destination_table_type="",
        destination_table_action="",
        condition="",
        mappings=[],
        file_name="output.csv",
        persist=False,
    )
    # Act
    data = build_and_roundtrip(ExportTask, t)
    # Assert
    assert data["payload"] == data["restored"]


def test_run_sql_task_json_contract() -> None:
    # Arrange
    macro = MacroStub()
    conn = ConnStub("conn-4")
    t = RunSQLTask(
        macro,
        name="SQL",
        description="SQL desc",
        query="select 1",
        connection=conn,
        persist=False,
    )
    # Act
    data = build_and_roundtrip(RunSQLTask, t)
    # Assert
    assert data["payload"] == data["restored"]


def test_run_python_task_json_contract() -> None:
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
    data = build_and_roundtrip(RunPythonTask, t)
    # Assert
    assert data["payload"] == data["restored"]


def test_start_task_json_contract() -> None:
    # Arrange
    macro = MacroStub()
    t = StartTask(macro)
    # Act
    data = build_and_roundtrip(StartTask, t)
    # Assert
    assert data["payload"] == data["restored"]
