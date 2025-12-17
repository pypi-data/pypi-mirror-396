from __future__ import annotations

from typing import Any, Dict, List

import pytest


def _start_task_item(macro_id: str) -> Dict[str, Any]:
    return {
        "id": "start-1",
        "name": "Start",
        "description": "",
        "taskType": "start",
        "workflowId": macro_id,
        "configuration": {},
    }


def _make_items(macro_id: str, task_item: Dict[str, Any]) -> Dict[str, Any]:
    # Always include a Start task plus the provided task item
    return {"items": [_start_task_item(macro_id), task_item]}


def _update_payload(api_mock) -> Dict[str, Any]:
    # Extract the last payload passed to update_task
    assert api_mock.update_task.call_count >= 1
    _, _, kwargs = api_mock.update_task.mock_calls[-1]
    return kwargs.get("data") or {}


@pytest.mark.parametrize(
    "task_type, name, configuration",
    [
        (
            "import",
            "ImpMinimal",
            {
                # minimal: source connector only
                "source": {"connectorId": "src-1"}
                # no destination, no condition, no mappings
            },
        ),
        (
            "export",
            "ExpMinimal",
            {
                # minimal: source connector only; no destination
                "source": {"connectorId": "src-2"}
            },
        ),
        (
            "runsql",
            "SqlMinimal",
            {
                # minimal: only query present, no target section
                "query": "select 1"
            },
        ),
        (
            "runpython",
            "PyMinimal",
            {
                # minimal: no file section at all
            },
        ),
    ],
)
def test_fields_pass_through_minimal_configs(
    api, project, task_type: str, name: str, configuration: Dict[str, Any]
) -> None:
    from datastar.macro import Macro

    macro = Macro(project)

    minimal_item = {
        "id": "task-min",
        "name": name,
        # Omit description intentionally to simulate partial state
        "taskType": task_type,
        "workflowId": macro._id,
        "configuration": configuration,
    }

    # Capture without normalizer side-effects by returning our minimal items
    def get_tasks(project_id: str, macro_id: str) -> Dict[str, Any]:
        assert project_id == project._id
        assert macro_id == macro._id
        return _make_items(macro_id, minimal_item)

    api.get_tasks.side_effect = get_tasks

    # Act: read, then save
    t = macro.get_task(name)
    assert t is not None
    t.save()

    # Assert: update payload configuration matches original exactly
    sent = _update_payload(api)

    # Top-level must reflect the same task type
    assert sent.get("taskType") == task_type

    # Configuration should not introduce fields that were not present
    assert sent.get("configuration") == configuration
