from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

from datastar.tasks.task_import import ImportTask
from datastar.tasks.task_export import ExportTask
from datastar.tasks.task_run_sql import RunSQLTask
from datastar.tasks.task_run_python import RunPythonTask
from datastar.tasks.task_start import StartTask


class ConnStub:
    def __init__(self, id_value: str) -> None:
        self._id = id_value


def test_task_save_and_update_flow(macro, api, tmp_path: Path):
    # Arrange
    src, dst = ConnStub("src-1"), ConnStub("dst-1")

    # Arrange: Build without persistence first
    t = ImportTask(
        macro,
        name="Imp",
        description="d",
        source_connection=src,
        destination_connection=dst,
        source_table="s",
        destination_table="d",
        persist=False,
    )
    # Assert
    assert not t._is_persisted()

    # Act: Persist via save; should call create_task
    t.save()
    # Assert
    api.create_task.assert_called()
    assert t._is_persisted()

    # Act: Save again; should call update_task
    t.description = "updated"
    t.save()
    # Assert
    api.update_task.assert_called()


def test_task_delete_calls_api(macro, api):
    # Arrange
    src, dst = ConnStub("src-2"), ConnStub("dst-2")
    t = macro.add_import_task(
        name="ToDelete",
        description="",
        source_connection=src,
        destination_connection=dst,
        source_table="s",
        destination_table="d",
    )
    # Act
    t.delete()
    # Assert
    api.delete_task.assert_called_with(macro.project._id, t._id)


def test_get_and_remove_dependencies(macro, api):
    # Arrange
    src, dst = ConnStub("src-4"), ConnStub("dst-4")
    first = macro.add_import_task(
        name="First",
        description="",
        source_connection=src,
        destination_connection=dst,
        source_table="s",
        destination_table="d",
    )
    second = macro.add_import_task(
        name="Second",
        description="",
        source_connection=src,
        destination_connection=dst,
        source_table="s",
        destination_table="d",
    )

    # Arrange: Ensure task name lookup can resolve ids -> names
    def get_tasks(project_id: str, macro_id: str):
        return {
            "items": [
                {
                    "id": "start-1",
                    "name": "Start",
                    "taskType": "start",
                    "workflowId": macro_id,
                    "configuration": {},
                },
                {
                    "id": first._id,
                    "name": "First",
                    "taskType": "import",
                    "workflowId": macro_id,
                    "configuration": {},
                },
                {
                    "id": second._id,
                    "name": "Second",
                    "taskType": "import",
                    "workflowId": macro_id,
                    "configuration": {},
                },
            ]
        }

    api.get_tasks.side_effect = get_tasks

    # Arrange: Simulate an existing dependency from second -> first
    api.get_task_dependencies.return_value = {
        "items": [
            {
                "id": "dep-1",
                "name": "First",
                "dependencyTaskId": first._id,
            }
        ]
    }

    # Act
    names = second.get_dependencies()
    # Assert
    assert names == ["First"]

    # Act: Remove by name should call delete_task_dependency with dep id
    second.remove_dependency("First")
    # Assert
    api.delete_task_dependency.assert_called_with(macro.project._id, "dep-1")

    # Arrange: Add by name: ensure our lookup returns an id that we interpret as the previous task id
    api.get_task_dependencies.return_value = {
        "items": [
            {
                "id": first._id,  # treated as dependency task id by our test harness
                "name": "First",
                "dependencyTaskId": first._id,
            }
        ]
    }
    # Act
    second.add_dependency("First")
    # Assert
    api.create_task_dependency.assert_called_with(
        macro.project._id, second._id, first._id
    )


def test_get_task_type_for_each_subclass(macro, api):
    src, dst = ConnStub("src-x"), ConnStub("dst-x")

    # Import
    t_import = ImportTask(
        macro,
        source_connection=src,
        destination_connection=dst,
        source_table="s",
        destination_table="d",
        persist=False,
    )
    assert t_import.get_task_type() == "import"

    # Export (to connector)
    t_export = ExportTask(
        macro,
        source_connection=src,
        destination_connection=dst,
        persist=False,
    )
    assert t_export.get_task_type() == "export"

    # Run SQL
    t_sql = RunSQLTask(macro, connection=src, persist=False)
    assert t_sql.get_task_type() == "runsql"

    # Run Python
    t_py = RunPythonTask(macro, persist=False)
    assert t_py.get_task_type() == "runpython"

    # Start
    t_start = StartTask(macro)
    assert t_start.get_task_type() == "start"
