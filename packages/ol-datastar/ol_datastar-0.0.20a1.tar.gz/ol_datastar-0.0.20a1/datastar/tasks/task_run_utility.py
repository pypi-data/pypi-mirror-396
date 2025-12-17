"""Task type for run utility task."""

from __future__ import annotations

import json
from typing import Any, Dict, Optional, TYPE_CHECKING

from ..task import Task

if TYPE_CHECKING:
    from ..macro import Macro


class RunUtilityTask(Task):
    """Runs a Datastar utility job within the macro."""

    @staticmethod
    def build_command_args_from_properties(self, properties: Dict[str, Any]) -> str:
        """
        Build a commandArgs string directly from the provided properties dict.

        - Booleans become toggle flags (only included when True).
        - Numbers are passed as-is.
        - Everything else is JSON-quoted.
        """

        parts: list[str] = []

        for field, value in properties.items():
            flag = f"--{field}"

            if isinstance(value, bool):
                if value:
                    parts.append(flag)
                continue

            if isinstance(value, (int, float)):
                parts.append(f"{flag} {value}")
                continue

            parts.append(f"{flag} {json.dumps(str(value))}")

        return " ".join(parts).strip()

    def __init__(
        self,
        macro: "Macro",
        *,
        name: str = "",
        description: str = "",
        utility_name: Optional[str] = None,
        utility_configuration: Optional[Dict[str, Any]] = None,
        run_configuration: Optional[Dict[str, Any]] = None,
        auto_join: bool = True,
        previous_task: Optional[Task] = None,
        persist: bool = True,
    ) -> None:
        self.utility_name = utility_name
        # Use shallow copies so callers can reuse their input dictionaries safely
        self.utility_configuration = (
            dict(utility_configuration) if utility_configuration is not None else None
        )
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
        return "runutility"

    def _to_configuration(self) -> Dict[str, Any]:
        configuration: Dict[str, Any] = {}

        # Utility selection
        utility_section: Dict[str, Any] = {}
        if self.utility_name is not None:
            utility_section["utilityName"] = self.utility_name
        if utility_section:
            configuration["utility"] = utility_section

        # Optional sections
        if self.utility_configuration is not None:
            configuration["utilityConfiguration"] = dict(self.utility_configuration)
        if self.run_configuration is not None:
            configuration["runConfiguration"] = dict(self.run_configuration)

        return configuration

    def _from_configuration(self, configuration: Dict[str, Any]) -> None:
        utility_section = configuration.get("utility")
        if utility_section is not None:
            self.utility_name = utility_section.get("utilityName")
        else:
            self.utility_name = None

        self.utility_configuration = configuration.get("utilityConfiguration")
        self.run_configuration = configuration.get("runConfiguration")

    def _get_sub_type(self) -> Optional[str]:
        return None
