from __future__ import annotations

from datastar.macro import Macro


class ConnStub:
    def __init__(self, id_value: str) -> None:
        self._id = id_value


def test_export_task_to_json_sets_db_subtype(project, api):
    macro = Macro(project)
    source = ConnStub("sandbox-1")
    destination = ConnStub("cf-1")

    macro.add_export_task(
        name="Export CF",
        source_connection=source,
        destination_connection=destination,
        destination_table="export_table",
        destination_table_type="existing",
        destination_table_action="replace",
    )

    payload = api.create_task.call_args.kwargs["data"]
    assert payload["taskType"] == "export"
    assert payload["taskSubType"] == "db"
    assert payload["configuration"]["destination"]["type"] == "dataConnection"


def test_export_task_to_json_sets_dsv_subtype(project, api):
    macro = Macro(project)
    source = ConnStub("sandbox-1")

    macro.add_export_task(
        name="Export CSV",
        source_connection=source,
        destination_connection=None,
        file_name="customers.csv",
    )

    payload = api.create_task.call_args.kwargs["data"]
    assert payload["taskType"] == "export"
    assert payload["taskSubType"] == "dsv"
    assert payload["configuration"]["destination"]["type"] == "file"
