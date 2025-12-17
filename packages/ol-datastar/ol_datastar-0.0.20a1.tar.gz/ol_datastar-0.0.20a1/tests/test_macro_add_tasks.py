from __future__ import annotations

from datastar.macro import Macro


class ConnStub:
    def __init__(self, id_value: str) -> None:
        self._id = id_value


def test_add_tasks_chains_in_order(project, api):
    # Arrange: build source tasks in a separate macro
    src = Macro(project)
    conn = ConnStub("c-1")
    t1 = src.add_export_task(
        name="A1",
        source_connection=conn,
        destination_connection=None,
        file_name="a1.csv",
    )
    t2 = src.add_export_task(
        name="A2",
        source_connection=conn,
        destination_connection=None,
        file_name="a2.csv",
    )

    dst = Macro(project)

    # Act: add both to destination with default chaining
    created = dst.add_tasks([t1, t2])

    # Assert: two new tasks created and chained: first after Start, second after first
    assert len(created) == 2

    # Check the last two dependency calls correspond to chaining semantics
    calls = api.create_task_dependency.call_args_list[-2:]
    # First added depends on Start
    assert calls[0].args == (project._id, created[0]._id, dst._get_start_task_id())
    # Second added depends on the first created in this call
    assert calls[1].args == (project._id, created[1]._id, created[0]._id)


def test_add_tasks_with_previous_task_fans_out(project, api):
    # Arrange: predecessor in destination macro
    dst = Macro(project)
    conn = ConnStub("c-2")
    predecessor = dst.add_export_task(
        name="P", source_connection=conn, destination_connection=None, file_name="p.csv"
    )

    # Source tasks from another macro
    src = Macro(project)
    a = src.add_export_task(
        name="B1",
        source_connection=conn,
        destination_connection=None,
        file_name="b1.csv",
    )
    b = src.add_export_task(
        name="B2",
        source_connection=conn,
        destination_connection=None,
        file_name="b2.csv",
    )

    # Act: add both to destination, each depending on the same predecessor
    created = dst.add_tasks([a, b], previous_task=predecessor)

    # Assert: each new task depends on the specified predecessor
    assert len(created) == 2
    calls = api.create_task_dependency.call_args_list[-2:]
    assert calls[0].args == (project._id, created[0]._id, predecessor._id)
    assert calls[1].args == (project._id, created[1]._id, predecessor._id)
