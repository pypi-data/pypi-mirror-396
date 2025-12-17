from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List


def test_macro_internal_export_json_and_file(macro, api, tmp_path: Path):
    # Arrange: create three tasks with specific names so sorting is deterministic
    from datastar.tasks.task_import import ImportTask

    a = ImportTask(
        macro,
        name="A_first",
        description="",
        source_connection=type("C", (), {"_id": "src-a"})(),
        destination_connection=type("C", (), {"_id": "dst-a"})(),
        source_table="s_a",
        destination_table="d_a",
    )

    b = ImportTask(
        macro,
        name="B_second",
        description="",
        source_connection=type("C", (), {"_id": "src-b"})(),
        destination_connection=type("C", (), {"_id": "dst-b"})(),
        source_table="s_b",
        destination_table="d_b",
    )

    c = ImportTask(
        macro,
        name="C_third",
        description="",
        source_connection=type("C", (), {"_id": "src-c"})(),
        destination_connection=type("C", (), {"_id": "dst-c"})(),
        source_table="s_c",
        destination_table="d_c",
    )

    # Override get_tasks to include start + the created tasks
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
                    "id": a._id,
                    "name": a.name,
                    "description": a.description,
                    "taskType": "import",
                    "workflowId": macro_id,
                    "configuration": a._to_json().get("configuration", {}),
                },
                {
                    "id": b._id,
                    "name": b.name,
                    "description": b.description,
                    "taskType": "import",
                    "workflowId": macro_id,
                    "configuration": b._to_json().get("configuration", {}),
                },
                {
                    "id": c._id,
                    "name": c.name,
                    "description": c.description,
                    "taskType": "import",
                    "workflowId": macro_id,
                    "configuration": c._to_json().get("configuration", {}),
                },
            ]
        }

    api.get_tasks.side_effect = get_tasks

    # Set dependencies: B depends on A, C depends on B (chain)
    def get_task_dependencies(project_id: str, task_id: str) -> Dict[str, Any]:
        if task_id == a._id:
            return {"items": []}
        if task_id == b._id:
            return {
                "items": [{"id": "dep-ab", "name": a.name, "dependencyTaskId": a._id}]
            }
        if task_id == c._id:
            return {
                "items": [{"id": "dep-bc", "name": b.name, "dependencyTaskId": b._id}]
            }
        return {"items": []}

    api.get_task_dependencies.side_effect = get_task_dependencies

    # Act: build JSON via internal helper
    payload = macro._to_json()

    # Assert: macro details
    assert payload["name"] == macro.name
    assert "description" in payload

    # Assert: tasks sorted by name
    names: List[str] = [t["task"]["name"] for t in payload["tasks"]]
    assert names == sorted([a.name, b.name, c.name])

    # Assert: each task contains dependencies by name
    deps_by_name = {t["task"]["name"]: t["dependencies"] for t in payload["tasks"]}
    assert deps_by_name[a.name] == []
    assert deps_by_name[b.name] == [a.name]
    assert deps_by_name[c.name] == [b.name]

    # Act: write to file
    out_path = macro._export_to_file(folder=str(tmp_path))
    p = Path(out_path)
    assert p.exists()
    text = p.read_text(encoding="utf-8")
    # Simple content checks
    assert '"tasks"' in text
    assert a.name in text and b.name in text and c.name in text
