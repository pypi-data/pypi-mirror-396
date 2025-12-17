from __future__ import annotations

from typing import Any, Dict

from datastar.tasks.task_import import ImportTask
from datastar.tasks.task_export import ExportTask
from datastar.macro import Macro


class ConnStub:
    def __init__(self, id_value: str) -> None:
        self._id = id_value


def test_add_import_task_persists_and_auto_joins(macro, api):
    # Arrange
    src, dst = ConnStub("src-1"), ConnStub("dst-1")

    # Act
    t = macro.add_import_task(
        name="Imp",
        description="desc",
        source_connection=src,
        destination_connection=dst,
        source_table="s",
        destination_table="d",
    )
    # Assert
    assert isinstance(t, ImportTask)
    api.create_task.assert_called_once()
    api.create_task_dependency.assert_called_once_with(
        macro.project._id, "task-1", "start-1"
    )


def test_add_import_task_no_auto_join(macro, api):
    # Arrange
    src, dst = ConnStub("src-2"), ConnStub("dst-2")

    # Act
    macro.add_import_task(
        name="Imp2",
        description="",
        source_connection=src,
        destination_connection=dst,
        source_table="s",
        destination_table="d",
        auto_join=False,
    )
    # Assert
    api.create_task.assert_called_once()
    api.create_task_dependency.assert_not_called()


def test_get_task_returns_correct_subclass(macro, api, monkeypatch):
    # Arrange
    def get_tasks(project_id: str, macro_id: str) -> Dict[str, Any]:
        return {
            "items": [
                {
                    "id": "start-1",
                    "name": "Start",
                    "description": "",
                    "taskType": "start",
                    "workflowId": macro_id,
                    "configuration": {},
                },
                {
                    "id": "t1",
                    "name": "Exp",
                    "description": "d",
                    "taskType": "export",
                    "workflowId": macro_id,
                    "configuration": {
                        "source": {"connectorId": "s", "table": ""},
                        "destination": {"type": "file", "fileName": "out.csv"},
                    },
                },
            ]
        }

    api.get_tasks.side_effect = get_tasks
    # Act
    task = macro.get_task("Exp")
    # Assert
    assert isinstance(task, ExportTask)
    assert task._is_persisted()


def test_delete_task_invokes_api(macro, api):
    # Arrange
    def get_tasks(project_id: str, macro_id: str) -> Dict[str, Any]:
        return {
            "items": [
                {
                    "id": "start-1",
                    "name": "Start",
                    "description": "",
                    "taskType": "start",
                    "workflowId": macro_id,
                    "configuration": {},
                },
                {
                    "id": "sql-1",
                    "name": "SQL",
                    "description": "",
                    "taskType": "runsql",
                    "workflowId": macro_id,
                    "configuration": {
                        "query": "select 1",
                        "target": {"connectorId": "c"},
                    },
                },
            ]
        }

    api.get_tasks.side_effect = get_tasks
    # Act
    macro.delete_task("SQL")
    # Assert
    api.delete_task.assert_called_once_with(macro.project._id, "sql-1")


def test_get_tasks_filtering(macro, api):
    # Arrange: Return an export task so filtering yields it by name
    def get_tasks(project_id: str, macro_id: str) -> Dict[str, Any]:
        return {
            "items": [
                {
                    "id": "start-1",
                    "name": "Start",
                    "description": "",
                    "taskType": "start",
                    "workflowId": macro_id,
                    "configuration": {},
                },
                {
                    "id": "e1",
                    "name": "E1",
                    "description": "",
                    "taskType": "export",
                    "workflowId": macro_id,
                    "configuration": {
                        "source": {"connectorId": "s", "table": "t"},
                        "destination": {"type": "file", "fileName": "out.csv"},
                    },
                },
            ]
        }

    api.get_tasks.side_effect = get_tasks
    # Act
    names = macro.get_tasks(type_filter="export")
    # Assert
    assert "E1" in names


def test_run_and_wait_for_done(macro, api):
    # Arrange
    # (no special arrange beyond fixtures)
    # Act
    macro.run({"x": 1})
    # Assert
    # Act
    macro.wait_for_done()
    # Assert
    api.execute_macro.assert_called_once()
    assert api.get_macro_run.call_count >= 1


def test_macro_save_and_delete(macro, api):
    # Arrange
    macro.name = "SavedName"
    macro.description = "SavedDesc"
    # Act: Save should call update_macro with current fields
    macro.save()
    # Assert
    api.update_macro.assert_called_once_with(
        macro.project._id, macro._id, name="SavedName", description="SavedDesc"
    )

    # Act: Delete should call delete_macro
    macro.delete()
    # Assert
    api.delete_macro.assert_called_once_with(macro.project._id, macro._id)


def test_adding_to_same_macro_clones(macro, api, conn):
    # Arrange: create an initial task in the macro using the helper (consumes task-1)
    t1 = macro.add_export_task(
        name="E1",
        source_connection=conn,
        destination_connection=None,
        file_name="out.csv",
    )

    # Act: add the same task object back into the same macro
    t2 = macro.add_task(t1)

    # Assert: type is preserved and IDs/macro link are correct
    assert isinstance(t2, ExportTask)
    assert t2.macro._id == macro._id
    assert t2._id == "task-2"  # second create_task call in this test
    assert t2.name == "E1 (copy)"  # same-macro clone uses suffixed name


def test_adding_to_new_macro_clones(project, api, conn):
    # Arrange: two macros in the same project
    m1 = Macro(project)
    m2 = Macro(project)

    # Create a task in the first macro using the helper (consumes task-1)
    t1 = m1.add_export_task(
        name="E2",
        source_connection=conn,
        destination_connection=None,
        file_name="out2.csv",
    )

    # Act: add the existing task to a different macro
    t2 = m2.add_task(t1)

    # Assert: new task belongs to the new macro, keeps type/name, and has next id
    assert isinstance(t2, ExportTask)
    assert t2.macro._id == m2._id
    assert t2._id == "task-2"
    assert t2.name == "E2"  # cross-macro clone keeps original name
