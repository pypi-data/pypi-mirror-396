# pyright: reportPrivateUsage=false, reportPrivateImportUsage=false
# pylint: disable=protected-access, import-outside-toplevel
"""
High-level Task utilities for Datastar.
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Type, TypeVar, Iterator, TYPE_CHECKING
import json
import os
from ._defaults import DEFAULT_DESCRIPTION, START_TASK_NAME

if TYPE_CHECKING:
    from .macro import Macro

T = TypeVar("T", bound="Task")


class Task(ABC):
    """Representation of a Datastar task."""

    # Public constant: canonical name of the Start task
    START_NAME: str = START_TASK_NAME

    def __init__(
        self,
        macro: "Macro",
        *,
        task_id: str = "",
        name: str = "",
        description: str = "",
        auto_join: bool = True,
        previous_task: Optional[Task] = None,
        persist: bool = True,
    ):
        self.macro: Macro = macro
        self.name: str = name or self.macro._next_task_name()
        self.description: str = description or DEFAULT_DESCRIPTION
        # Initialize position attributes
        self.x: Optional[int] = None
        self.y: Optional[int] = None
        # If no id is supplied then create
        if task_id:
            self._id = task_id
        elif persist:
            # Defer to save() to avoid duplicating creation logic
            self._id = ""
            self.save(auto_join=auto_join, previous_task=previous_task)
        else:
            # Construct without persisting
            self._id = ""

    def _is_persisted(self) -> bool:
        return bool(self._id)

    def save(
        self,
        *,
        auto_join: bool = True,
        previous_task: Optional[Task] = None,
    ) -> None:

        # If already persisted, update
        if self._is_persisted():
            self.macro.project._api().update_task(
                self.macro.project._id,
                self._id,
                data=self._to_json(),
            )
            return

        # Otherwise, create a new task on the server
        self._id = self._persist_new()

        # Join task to either previous task (auto) or specified task, or leave unconnected
        if auto_join:
            self._add_dependency_id(self.macro._last_task_added_id)
        elif previous_task:
            self._add_dependency_id(previous_task._id)

        self.macro._last_task_added_id = self._id

    def delete(self) -> None:
        """
        Delete this task
        """
        self.macro.project._api().delete_task(self.macro.project._id, self._id)

    def add_dependency(self, previous_task_name: str) -> None:
        """
        Connect this task to a previous task
        """
        # Resolve the previous task id
        if previous_task_name == self.START_NAME:
            previous_task_id = self.macro._get_start_task_id()
        else:
            previous_task_id: Optional[str] = None
            for item in self.macro._get_task_data():
                if item.get("name") == previous_task_name:
                    previous_task_id = item.get("id")
                    break

        if not previous_task_id:
            raise ValueError(
                f"Previous task '{previous_task_name}' not found in macro '{self.macro.name}'"
            )

        # Create the dependency edge from the resolved task to this task
        self.macro.project._api().create_task_dependency(
            self.macro.project._id, self._id, previous_task_id
        )

    def remove_dependency(self, previous_task_name: str) -> None:
        """
        Remove the connection between this task and a previous task.
        Supports removing the edge from the special Start node as well.
        """

        dependency_id = self._get_dependency_by_name(previous_task_name)
        if dependency_id is None:
            return

        self.macro.project._api().delete_task_dependency(
            self.macro.project._id, dependency_id
        )

    def get_dependencies(self) -> List[str]:
        """
        List all tasks, that have incoming connections to this one, by name
        """

        response = self.macro.project._api().get_task_dependencies(
            self.macro.project._id, self._id
        )

        task_data = self.macro._get_task_data()

        task_list: List[str] = []
        items = response.get("items") or []
        for item in items:
            task_id = item["dependencyTaskId"]
            name: str = self._get_task_name_from_data(task_data, task_id)
            task_list.append(name)

        return task_list

    # ------------------------------------------------------------------
    # Internals

    def _put_attrs(self, d: Dict[str, Any], specs) -> None:
        """Set keys in dict from this task's attributes when not None.

        specs can be:
        - a string: use it as both key and attribute name
        - a (key, attr_name) tuple: map a different attribute to the key
        """
        for spec in specs:
            if isinstance(spec, str):
                key = attr = spec
            else:
                key, attr = spec
            value = getattr(self, attr)
            if value is not None:
                d[key] = value

    def _export_to_file(self, folder: str = "", name: Optional[str] = None) -> str:
        """
        Export this task to a .task file using API-compatible JSON.

        - Defaults filename to the task name.
        - Always appends .task.
        - Writes into the provided folder if given; no validation or directory creation.

        Returns the final file path written.
        """

        base_name = name or self.name
        file_name = f"{base_name}.task"
        path = os.path.join(folder, file_name) if folder else file_name

        with open(path, "w", encoding="utf-8") as f:
            json.dump(self._to_json(), f, indent=2)

        return path

    def _add_dependency_id(self, previous_task_id: str) -> None:

        self.macro.project._api().create_task_dependency(
            self.macro.project._id, self._id, previous_task_id
        )

    def _persist_new(self) -> str:
        assert self.macro is not None

        response = self.macro.project._api().create_task(
            self.macro.project._id,
            self.macro._id,
            data=self._to_json(),
        )
        return response["item"]["id"]

    def _get_task_data_by_id(self, task_id: str) -> Optional[Dict[str, Any]]:

        task_data = self.macro._get_task_data()

        for item in task_data:
            if item["id"] == task_id:
                return item

        return None

    def _get_task_name_from_data(
        self, data: Iterator[Dict[str, Any]], task_id: str
    ) -> str:

        for item in data:
            if item["id"] == task_id:
                return item["name"]

        assert False

    def _get_dependency_by_name(self, name: str) -> Optional[str]:
        response = self.macro.project._api().get_task_dependencies(
            self.macro.project._id, self._id
        )

        items = response.get("items") or []

        # Start is a special case, else build a lookup to get the task ID
        if name == self.START_NAME:
            target_id = self.macro._get_start_task_id()
        else:
            all_tasks = self.macro._get_task_data()
            name_to_id = {t.get("name", ""): t.get("id", "") for t in all_tasks}
            target_id = name_to_id.get(name)

        # If the name matches no tasks, there cant be a dependency
        if not target_id:
            return None

        # Else look for dependency matching the id
        for item in items:
            if item.get("dependencyTaskId") == target_id:
                return item.get("id")

        return None

    @classmethod
    def _read_from(cls: Type[T], macro: Macro, task_data: Dict[str, Any]) -> Task:

        assert cls is not Task  # Cannot construct parent, only subclasses
        assert macro is not None  # A task cannot exist outside of a macro

        # Construct instance of subclass without invoking __init__ yet
        new_task = cls.__new__(cls)

        # Read base parameters (allow missing id for not-yet-persisted tasks)
        task_id: str = task_data.get("id", "")
        task_name: str = task_data.get("name", "")
        task_description: str = task_data.get("description", "")

        if task_id:
            # Existing task loaded from API:
            assert macro._id == task_data.get(
                "workflowId"
            )  # Ensure it belongs to this macro
            Task.__init__(
                new_task,
                macro,
                task_id=task_id,
                name=task_name,
                description=task_description,
            )
        else:
            # No id. Task should be persisted.
            Task.__init__(
                new_task,
                macro,
                name=task_name,
                description=task_description,
            )

        new_task._from_json(task_data)

        return new_task

    # ------------------------------------------------------------------
    # JSON translation helpers (for import export via API or file)

    def _to_json(self) -> Dict[str, Any]:

        payload: Dict[str, Any] = {
            "name": self.name,
            "description": self.description,
            "taskType": self.get_task_type(),
            "configuration": self._to_configuration(),
        }
        sub_type = self._get_sub_type()
        if sub_type is not None:
            payload["taskSubType"] = sub_type

        # Add uiMetadata if position coordinates are set
        if self.x is not None or self.y is not None:
            payload["uiMetadata"] = {
                "position": {
                    "x": self.x if self.x is not None else 0,
                    "y": self.y if self.y is not None else 0,
                }
            }

        return payload

    def _from_json(self, payload: Dict[str, Any]) -> None:
        self.name = payload.get("name", self.name)
        self.description = payload.get("description", self.description)
        self._from_configuration(payload.get("configuration") or {})

        # Extract position from uiMetadata if present
        ui_metadata = payload.get("uiMetadata")
        if ui_metadata and isinstance(ui_metadata, dict):
            position = ui_metadata.get("position")
            if position and isinstance(position, dict):
                self.x = position.get("x")
                self.y = position.get("y")

    # ------------------------------------------------------------------
    # Abstract methods

    @abstractmethod
    def get_task_type(self) -> str:
        assert False

    @abstractmethod
    def _to_configuration(self) -> Dict[str, Any]:
        assert False

    @abstractmethod
    def _from_configuration(self, configuration: Dict[str, Any]) -> None:
        assert False

    @abstractmethod
    def _get_sub_type(self) -> Optional[str]:
        assert False
