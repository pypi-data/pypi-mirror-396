"""Task type for executing Python code."""

from __future__ import annotations

from typing import Any, Dict, Optional, TYPE_CHECKING

from ..task import Task

if TYPE_CHECKING:
    from ..macro import Macro


class RunPythonTask(Task):
    """Runs Python scripts within the macro."""

    def __init__(
        self,
        macro: "Macro",
        *,
        name: str = "",
        description: str = "",
        filename: str = "",
        directory_path: str = "",
        run_configuration: Optional[Dict[str, Any]] = None,
        auto_join: bool = True,
        previous_task: Optional[Task] = None,
        persist: bool = True,
    ):
        self.filename = filename
        self.directory_path = directory_path
        self.run_configuration = (
            dict(run_configuration) if run_configuration is not None else None
        )

        # Note: base will persist, which calls back into subclass, so call init here at end
        super().__init__(
            macro=macro,
            name=name,
            description=description,
            auto_join=auto_join,
            previous_task=previous_task,
            persist=persist,
        )

    # ------------------------------------------------------------------
    # Abstract method implementation

    def get_task_type(self) -> str:
        return "runpython"

    def _to_configuration(self) -> Dict[str, Any]:
        configuration: Dict[str, Any] = {}

        # Only emit file section if any values are provided
        file_section: Dict[str, Any] = {}
        if self.filename is not None:
            file_section["filename"] = self.filename
        if self.directory_path is not None:
            file_section["directoryPath"] = self.directory_path
        if file_section:
            configuration["file"] = file_section
        if self.run_configuration is not None:
            configuration["runConfiguration"] = dict(self.run_configuration)

        return configuration

    def _from_configuration(self, configuration: Dict[str, Any]) -> None:
        file_section = configuration.get("file")
        if file_section is not None:
            self.filename = file_section.get("filename")
            self.directory_path = file_section.get("directoryPath")
        else:
            # Clear when section is absent to avoid stale values
            self.filename = None
            self.directory_path = None
        self.run_configuration = configuration.get("runConfiguration")

    def _get_sub_type(self) -> Optional[str]:
        return None
