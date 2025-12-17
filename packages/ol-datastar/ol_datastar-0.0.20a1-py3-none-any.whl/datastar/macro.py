# pyright: reportPrivateUsage=false, reportPrivateImportUsage=false
# pylint: disable=protected-access, import-outside-toplevel
"""
Datastar library: Macro interface.
"""

from __future__ import annotations

import time
from typing import Any, Dict, List, Optional, Iterator, Type, TYPE_CHECKING

from .task import Task
from .task_registry import _get_task_class
from ._defaults import DEFAULT_DESCRIPTION

if TYPE_CHECKING:
    from .project import Project
    from .tasks import (
        DeleteTask,
        ExportTask,
        ImportTask,
        RunPythonTask,
        RunSQLTask,
        RunUtilityTask,
        UpdateTask,
    )


class Macro:
    """User-facing wrapper around a Datastar macro."""

    def __init__(
        self,
        project: "Project",
        *,
        macro_id: str = "",
        name: str = "",
        description: str = "",
    ):
        self.project: Project = project
        self.name: str = name or self.project._next_macro_name()
        self.description: str = description or DEFAULT_DESCRIPTION
        self._task_counter: int = 1
        self._run_id: Optional[str] = None

        if macro_id:
            self._id = macro_id
        else:
            self._id: str = self.project._api().create_macro(
                self.project._id, name=self.name, description=self.description
            )

        self._last_task_added_id: str = self._get_start_task_id()

    def save(self) -> None:
        """
        Persist macro details to database
        """
        self.project._api().update_macro(
            self.project._id, self._id, name=self.name, description=self.description
        )

    def delete(self) -> None:
        """
        Delete macro from project
        """
        self.project._api().delete_macro(self.project._id, self._id)

    # ------------------------------------------------------------------
    # Tasks

    def get_task(self, name: str) -> Optional[Task]:
        """
        Returns a task by name
        """

        # Note: This requires all task types are added in task_registry

        for task_data in self._get_task_data():

            if task_data["name"] == name:

                # Construct to correct subclass of Type per the type returned
                task_type = task_data["taskType"]
                class_to_create: Type[Task] = _get_task_class(task_type)
                return class_to_create._read_from(self, task_data)

        return None

    def get_tasks(self, *, type_filter: Optional[str] = None) -> List[str]:
        """
        Get a list of task names in the macro
        """

        data = self._get_task_data(type_filter=type_filter)

        task_list: List[str] = []
        for item in data:
            task_list.append(str(item.get("name")))

        return task_list

    def delete_task(self, name: str) -> None:
        """
        Delete a task by name from the macro
        """
        task = self.get_task(name)
        if task is not None:
            task.delete()

    # ------------------------------------------------------------------
    # Task creation helper functions

    def add_task(
        self,
        task: Task,
        *,
        auto_join: bool = True,
        previous_task: Optional[Task] = None,
    ) -> Task:
        """
        Persist a pre-configured task and add it to this macro.

        - If the task already belongs to this macro, a new copy is created in
          this macro using the same configuration but with name '<name> (copy)'.
        - If the task belongs to a different macro, a new task is created in
          this macro using the same name/description/configuration.
        - The original task is not modified. The new task is returned.
        """
        # Validate previous_task belongs to this macro if supplied
        if previous_task is not None and previous_task.macro is not self:
            raise ValueError("previous_task must belong to this macro")

        # Build payload from the original task
        payload = task._to_json()

        # Same-macro: create a copy with a suffixed name
        if task.macro is self:
            payload["name"] = f"{payload.get('name', task.name)} (copy)"

        # Create task in this macro
        response = self.project._api().create_task(
            self.project._id,
            self._id,
            data=payload,
        )
        new_task_id = response["item"]["id"]

        # Materialize a typed Task instance of the correct subclass
        task_type = payload["taskType"]
        class_to_create: Type[Task] = _get_task_class(task_type)
        task_data: Dict[str, Any] = {
            "id": new_task_id,
            "name": payload.get("name", task.name),
            "description": payload.get("description", task.description),
            "taskType": task_type,
            "workflowId": self._id,
            "configuration": payload.get("configuration", {}),
        }
        new_task = class_to_create._read_from(self, task_data)

        # Handle optional joining semantics within this macro
        if auto_join:
            self.project._api().create_task_dependency(
                self.project._id, new_task_id, self._last_task_added_id
            )
        elif previous_task is not None:
            self.project._api().create_task_dependency(
                self.project._id, new_task_id, previous_task._id
            )

        # Update last-added pointer
        self._last_task_added_id = new_task_id

        return new_task

    def add_tasks(
        self,
        tasks: List[Task],
        *,
        auto_join: bool = True,
        previous_task: Optional[Task] = None,
    ) -> List[Task]:
        """Add multiple tasks in order.

        - If previous_task is provided, each added task depends on it.
        - Otherwise, tasks are chained in the order provided.
        """

        if previous_task is not None and previous_task.macro is not self:
            raise ValueError("previous_task must belong to this macro")

        result: List[Task] = []
        if previous_task is not None:
            for t in tasks:
                result.append(
                    self.add_task(t, auto_join=False, previous_task=previous_task)
                )
        else:
            for t in tasks:
                result.append(self.add_task(t, auto_join=auto_join))

        return result

    def add_import_task(self, **kwargs: Any) -> "ImportTask":
        """
        Add a new ImportTask to this macro (db will be updated)
        """
        from .tasks import ImportTask

        return ImportTask(self, **kwargs)

    def add_export_task(self, **kwargs: Any) -> "ExportTask":
        """
        Add a new ExportTask to this macro (db will be updated)
        """
        from .tasks import ExportTask

        return ExportTask(self, **kwargs)

    def add_run_sql_task(self, **kwargs: Any) -> "RunSQLTask":
        """
        Add a new RunSQLTask to this macro (db will be updated)
        """
        from .tasks import RunSQLTask

        return RunSQLTask(self, **kwargs)

    def add_run_python_task(self, **kwargs: Any) -> "RunPythonTask":
        """
        Add a new RunPythonTask to this macro (db will be updated)
        """
        from .tasks import RunPythonTask

        return RunPythonTask(self, **kwargs)

    def add_run_utility_task(self, **kwargs: Any) -> "RunUtilityTask":
        """
        Add a new RunUtilityTask to this macro (db will be updated)
        """
        from .tasks import RunUtilityTask

        return RunUtilityTask(self, **kwargs)

    def add_update_task(self, **kwargs: Any) -> "UpdateTask":
        """
        Add a new UpdateTask to this macro (db will be updated)
        """
        from .tasks import UpdateTask

        return UpdateTask(self, **kwargs)

    def add_delete_task(self, **kwargs: Any) -> "DeleteTask":
        """
        Add a new DeleteTask to this macro (db will be updated)
        """
        from .tasks import DeleteTask

        return DeleteTask(self, **kwargs)

    # ------------------------------------------------------------------
    # Cloning

    def clone(
        self,
        project: Optional["Project"] = None,
        *,
        name: Optional[str] = None,
        description: Optional[str] = None,
    ) -> "Macro":
        """
        Clone this macro (tasks and dependencies) into a new macro.

        - If `project` is provided, the new macro is created in that project;
          otherwise it is created in the same project as this macro.
        - Task configurations are copied; the special Start task is not
          duplicated (each macro already has one). All non-start tasks and
          their dependencies are recreated.
        - Returns the newly created Macro.
        """

        target_project = project or self.project

        # Determine cloned macro name: add " (copy)" when cloning within same project
        if name is None:
            new_name = (
                f"{self.name} (copy)" if target_project is self.project else self.name
            )
        else:
            new_name = name

        # Create destination macro
        cloned = Macro(
            target_project,
            name=new_name,
            description=description or self.description,
        )

        # Map source task IDs to destination task IDs (include Start mapping)
        src_start_id = self._get_start_task_id()
        dst_start_id = cloned._get_start_task_id()
        id_map: Dict[str, str] = {src_start_id: dst_start_id}

        # First pass: create tasks without dependencies
        for item in self._get_task_data():
            if item.get("taskType") == "start":
                continue

            # Materialize a typed source task instance
            task_type = item["taskType"]
            class_to_create: Type[Task] = _get_task_class(task_type)
            src_task = class_to_create._read_from(self, item)

            # Create equivalent task in destination macro (no auto join)
            dst_task = cloned.add_task(src_task, auto_join=False)
            id_map[item["id"]] = dst_task._id

        # Second pass: replicate dependencies using the id map
        for item in self._get_task_data():
            if item.get("taskType") == "start":
                continue

            src_task_id = item["id"]
            deps = self.project._api().get_task_dependencies(
                self.project._id, src_task_id
            )
            for dep in deps.get("items", []):
                dep_src_id = dep.get("dependencyTaskId")
                if not dep_src_id:
                    continue
                # Map to destination IDs and create dependency
                dst_task_id = id_map[src_task_id]
                dst_dep_id = id_map.get(dep_src_id)
                if dst_dep_id:
                    cloned.project._api().create_task_dependency(
                        cloned.project._id, dst_task_id, dst_dep_id
                    )

        return cloned

    # ------------------------------------------------------------------
    # Running a macro

    def run(self, parameters: Optional[Dict[str, Any]] = None) -> None:
        """
        Run a macro as a job
        """

        parameters = parameters or {}

        if self._run_id is not None:
            status = self.get_run_status()
            if status == "pending" or status == "processing":
                raise RuntimeError("macro already running")

        response = self.project._api().execute_macro(
            self.project._id, self._id, parameters=parameters
        )

        self._run_id = response["item"]["id"]

    def get_run_status(self) -> str:
        """
        Get the current status of a job
        """
        if self._run_id is None:
            return "no_current_run"
        response = self.project._api().get_macro_run(self.project._id, self._run_id)

        return response["item"]["status"]

    def cancel(self) -> None:
        """
        Cancel the current running macro job. No-op if none.
        """
        if self._run_id is None:
            return

        self.project._api().cancel_job(self._run_id)

    def wait_for_done(
        self, *, verbose: bool = False, max_seconds: Optional[float] = None
    ) -> None:
        """
        Wait for a job to complete.

        - verbose: print periodic status updates while waiting.
        - max_seconds: maximum seconds to wait before timing out. If None,
          wait indefinitely. When the timeout is reached, a TimeoutError is
          raised and the current run is left intact so it can be inspected or
          cancelled by the caller.
        """

        status = self.get_run_status()
        counter = 0
        deadline: Optional[float] = None
        if max_seconds is not None:
            # Use monotonic clock for reliable timeout measurement
            deadline = time.monotonic() + float(max_seconds)

        while status == "pending" or status == "processing":

            # Polling 3 sec interval
            time.sleep(3)

            status = self.get_run_status()

            if verbose:
                counter += 1
                print(
                    f"Waiting for run completion ({counter}). Current run status = {status}"
                )

            if deadline is not None and time.monotonic() >= deadline:
                # Keep _run_id so the caller can cancel or check status later
                raise TimeoutError(
                    f"Macro run did not complete within {max_seconds} seconds; last status = {status}"
                )

        self._run_id = None

    # ------------------------------------------------------------------
    # Internal helpers

    @classmethod
    def _read_from(cls, project: Project, task_data: Dict[str, Any]) -> Macro:

        # Get parameters
        macro_id: str = task_data["id"]
        macro_name: str = task_data["name"]
        macro_description: str = task_data["description"]

        return Macro(
            project, macro_id=macro_id, name=macro_name, description=macro_description
        )

    def _get_task_data(
        self, *, type_filter: Optional[str] = None
    ) -> List[Dict[str, Any]]:

        response = self.project._api().get_tasks(self.project._id, self._id)

        result: List[Dict[str, Any]] = []
        for item in response.get("items", []):
            if type_filter and type_filter != item["taskType"]:
                continue
            result.append(item)

        return result

    def _get_start_task_id(self):

        tasks = self._get_task_data(type_filter="start")
        if not tasks:
            raise RuntimeError("No start task found in macro")

        return tasks[0]["id"]

    def _next_task_name(self) -> str:
        counter = self._task_counter
        self._task_counter += 1
        return f"Task {counter}"

    def _from_json(self, payload: Dict[str, Any]) -> None:
        self._id = str(payload["id"])
        self.name = str(payload["name"])
        self.description = payload.get("description") or DEFAULT_DESCRIPTION

    @classmethod
    def _from_existing(cls, project: "Project", payload: Dict[str, Any]) -> "Macro":
        instance: "Macro" = cls.__new__(cls)
        instance.project = project
        instance._task_counter = 0
        instance._from_json(payload)
        return instance

    # ------------------------------------------------------------------
    # Export (internal debugging helpers)

    def _to_json(self) -> Dict[str, Any]:
        """
        Build a JSON-serializable representation of this macro:
        - Macro details: name, description
        - Tasks: list of entries, one per non-start task, sorted by task name
          Each entry contains:
            - "task": the task details (same as Task.export_to_file/_to_json)
            - "dependencies": list of dependency task names for that task
        """

        # Collect task payloads (skip the special start task) using public helpers
        task_entries: List[Dict[str, Any]] = []
        for task_name in self.get_tasks():
            task = self.get_task(task_name)
            assert task

            if task.get_task_type() == "start":
                continue

            dependency_names: List[str] = task.get_dependencies()

            task_entries.append(
                {
                    "task": task._to_json(),
                    "dependencies": dependency_names,
                }
            )

        # Sort by task name for deterministic output
        task_entries.sort(key=lambda e: e.get("task", {}).get("name", ""))

        return {
            "name": self.name,
            "description": self.description,
            "tasks": task_entries,
        }

    def _export_to_file(self, folder: str = "", name: Optional[str] = None) -> str:
        """
        Write this macro representation to a .macro file (internal helper).

        - Defaults filename to the macro name
        - Appends .macro extension
        - Writes into the provided folder if given; does not create folders
        Returns the file path written.
        """
        import json
        import os

        base_name = name or self.name
        file_name = f"{base_name}.macro"
        path = os.path.join(folder, file_name) if folder else file_name

        with open(path, "w", encoding="utf-8") as f:
            json.dump(self._to_json(), f, indent=2)

        return path
