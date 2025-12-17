from __future__ import annotations

from typing import Any, Dict, List

from datastar.project import Project
from datastar.macro import Macro


def _build_tasks_list(macro_id: str, items: List[Dict[str, Any]]):
    return {"items": items}


def _start_item(macro_id: str, start_id: str = "start-1"):
    return {
        "id": start_id,
        "name": "Start",
        "description": "",
        "taskType": "start",
        "workflowId": macro_id,
        "configuration": {},
    }


def test_clone_within_same_project_preserves_tasks_and_dependencies(api):
    # Ensure unique IDs for macros and projects in this test
    api.create_project.side_effect = ["proj-a"]
    api.create_macro.side_effect = ["macro-src", "macro-dst"]

    # Create project and source macro
    project = Project.create("P1")
    src = Macro(project, name="SrcMacro")

    # Create tasks per create_a_task_chain pattern (chain of 5)
    sandbox = project.get_sandbox()
    first = src.add_run_sql_task(name="step_1", query="select 1", connection=sandbox)
    chain = [first]
    for i in range(2, 6):
        nxt = src.add_task(first)  # clone and auto-join to previous
        nxt.name = f"step_{i}"
        nxt.save(auto_join=False)
        chain.append(nxt)

    # Create tasks per raw_task_copy pattern (3 tasks joined to Start)
    start_task = src.get_task("Start")
    start_joined = []
    for i in range(1, 4):
        t = src.add_run_sql_task(
            name=f"src_step_{i}",
            query="select 1",
            connection=sandbox,
            auto_join=False,
            previous_task=start_task,
        )
        start_joined.append(t)

    # Synthesize dependencies for each source task id
    dep_map: Dict[str, List[str]] = {}
    # Chain dependencies: first->Start, then each -> previous in chain
    dep_map[chain[0]._id] = ["start-1"]
    for prev, curr in zip(chain[:-1], chain[1:]):
        dep_map[curr._id] = [prev._id]
    # Start-joined tasks: all depend on Start
    for t in start_joined:
        dep_map[t._id] = ["start-1"]

    # Build synthetic get_tasks for both source and future destination macros
    # Destination IDs are synthetic but consistent within this test
    dest_start_id = "dst-start-1"
    dest_task_ids_by_name: Dict[str, str] = {}
    for idx, t in enumerate(chain + start_joined, start=1):
        dest_task_ids_by_name[t.name] = f"dst-task-{idx}"

    def get_tasks(project_id: str, macro_id: str) -> Dict[str, Any]:
        if macro_id == src._id:
            items: List[Dict[str, Any]] = [_start_item(macro_id, "start-1")]
            for t in chain + start_joined:
                items.append(
                    {
                        "id": t._id,
                        "name": t.name,
                        "description": t.description,
                        "taskType": "runsql",
                        "workflowId": macro_id,
                        "configuration": {
                            "query": "select 1",
                            "target": {"connectorId": sandbox._id},
                        },
                    }
                )
            return _build_tasks_list(macro_id, items)
        else:
            # Destination macro: mirror the source names with synthetic IDs
            items: List[Dict[str, Any]] = [_start_item(macro_id, dest_start_id)]
            for t in chain + start_joined:
                items.append(
                    {
                        "id": dest_task_ids_by_name[t.name],
                        "name": t.name,
                        "description": t.description,
                        "taskType": "runsql",
                        "workflowId": macro_id,
                        "configuration": {
                            "query": "select 1",
                            "target": {"connectorId": sandbox._id},
                        },
                    }
                )
            return _build_tasks_list(macro_id, items)

    api.get_tasks.side_effect = get_tasks

    # Dependencies for both source and destination, keyed by task id
    dest_dep_map: Dict[str, List[str]] = {}
    # For destination, map by names to synthetic ids
    # Chain
    first_name = chain[0].name
    dest_dep_map[dest_task_ids_by_name[first_name]] = [dest_start_id]
    for prev, curr in zip(chain[:-1], chain[1:]):
        dest_dep_map[dest_task_ids_by_name[curr.name]] = [
            dest_task_ids_by_name[prev.name]
        ]
    # Start-joined
    for t in start_joined:
        dest_dep_map[dest_task_ids_by_name[t.name]] = [dest_start_id]

    def get_task_dependencies(project_id: str, task_id: str) -> Dict[str, Any]:
        if task_id in dep_map:
            deps = dep_map.get(task_id, [])
        else:
            deps = dest_dep_map.get(task_id, [])
        return {
            "items": [
                {"id": f"dep-{i}-{task_id}", "name": "", "dependencyTaskId": d}
                for i, d in enumerate(deps, start=1)
            ]
        }

    api.get_task_dependencies.side_effect = get_task_dependencies

    # Act: clone within same project
    dst = src.clone()

    # Assert: name updated with (copy) and project unchanged
    assert dst.project._id == project._id
    assert dst.name == "SrcMacro (copy)"
    # Compare full task payloads (names, details, dependencies) via macro JSON
    payload_src = src._to_json()["tasks"]
    payload_dst = dst._to_json()["tasks"]
    assert payload_src == payload_dst


def test_clone_to_new_project_preserves_tasks_and_dependencies(api):
    # Unique IDs across two projects/macros
    api.create_project.side_effect = ["proj-a", "proj-b"]
    api.create_macro.side_effect = ["macro-src", "macro-dst"]

    # Create two projects and a source macro
    p1 = Project.create("P1")
    p2 = Project.create("P2")
    src = Macro(p1, name="SrcMacro2")

    sandbox = p1.get_sandbox()

    # Build a small mixed graph: chain of 3 and two start-joined
    a = src.add_run_sql_task(name="a1", query="select 1", connection=sandbox)
    b = src.add_task(a)
    b.name = "a2"
    b.save(auto_join=False)
    c = src.add_task(a)
    c.name = "a3"
    c.save(auto_join=False)

    start_task = src.get_task("Start")
    x = src.add_run_sql_task(
        name="x1",
        query="select 1",
        connection=sandbox,
        auto_join=False,
        previous_task=start_task,
    )
    y = src.add_run_sql_task(
        name="x2",
        query="select 1",
        connection=sandbox,
        auto_join=False,
        previous_task=start_task,
    )

    # Provide dependencies for source
    dep_map = {
        a._id: ["start-1"],
        b._id: [a._id],
        c._id: [a._id],
        x._id: ["start-1"],
        y._id: ["start-1"],
    }

    # Build synthetic destination task id map by name
    dest_start_id = "dst-start-2"
    order = [a, b, c, x, y]
    dest_task_ids_by_name = {t.name: f"dst2-{i}" for i, t in enumerate(order, start=1)}

    # Provide get_tasks for both macros
    def get_tasks(project_id: str, macro_id: str) -> Dict[str, Any]:
        if macro_id == src._id:
            items = [_start_item(macro_id, "start-1")]
            for t in order:
                items.append(
                    {
                        "id": t._id,
                        "name": t.name,
                        "description": t.description,
                        "taskType": "runsql",
                        "workflowId": macro_id,
                        "configuration": {
                            "query": "select 1",
                            "target": {"connectorId": sandbox._id},
                        },
                    }
                )
            return _build_tasks_list(macro_id, items)
        else:
            items = [_start_item(macro_id, dest_start_id)]
            for t in order:
                items.append(
                    {
                        "id": dest_task_ids_by_name[t.name],
                        "name": t.name,
                        "description": t.description,
                        "taskType": "runsql",
                        "workflowId": macro_id,
                        "configuration": {
                            "query": "select 1",
                            "target": {"connectorId": sandbox._id},
                        },
                    }
                )
            return _build_tasks_list(macro_id, items)

    api.get_tasks.side_effect = get_tasks

    # Provide dependencies side effect that handles both source and dest ids
    dest_dep_map = {
        dest_task_ids_by_name["a1"]: [dest_start_id],
        dest_task_ids_by_name["a2"]: [dest_task_ids_by_name["a1"]],
        dest_task_ids_by_name["a3"]: [dest_task_ids_by_name["a1"]],
        dest_task_ids_by_name["x1"]: [dest_start_id],
        dest_task_ids_by_name["x2"]: [dest_start_id],
    }

    def get_task_dependencies(project_id: str, task_id: str) -> Dict[str, Any]:
        deps = dep_map.get(task_id)
        if deps is None:
            deps = dest_dep_map.get(task_id, [])
        return {
            "items": [
                {"id": f"dep-{i}-{task_id}", "name": "", "dependencyTaskId": d}
                for i, d in enumerate(deps, start=1)
            ]
        }

    api.get_task_dependencies.side_effect = get_task_dependencies

    # Record existing dependency creations from building the source graph
    before_dep_calls = api.create_task_dependency.call_count

    # Act: clone to a different project
    dst = src.clone(project=p2)

    # Assert: project changed and name kept
    assert dst.project._id == p2._id
    assert dst.name == "SrcMacro2"
    # Compare full task payloads via macro JSON
    payload_src = src._to_json()["tasks"]
    payload_dst = dst._to_json()["tasks"]
    assert payload_src == payload_dst
