"""Connection subclass for Excel files."""

from __future__ import annotations

from typing import Any, Dict, Optional

from ..connection import Connection


class ExcelConnection(Connection):
    """Represents an Excel connection."""

    def __init__(
        self,
        *,
        path: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        sheet_name: Optional[str] = None,
        workbook_password: Optional[str] = None,
    ):
        # Excel connectors are currently not supported in the backend API
        assert False, "this connection type is currently not supported"
        if not path:
            raise ValueError("path is required for ExcelConnection.")

        self.path = str(path)
        self.sheet_name = None if sheet_name is None else str(sheet_name)
        self.workbook_password = (
            None if workbook_password is None else str(workbook_password)
        )

        # Note: base will persist, which calls back into subclass, so call init here at end
        super().__init__(name=name, description=description)

    # ------------------------------------------------------------------
    # Abstract method implementation

    def _to_configuration(self) -> Dict[str, Any]:

        config: Dict[str, Any] = {
            "type": "excel",
            "path": self.path,
            "sheetName": self.sheet_name,
            "password": self.workbook_password,
        }

        return config

    def _from_configuration(self, payload: Dict[str, Any]) -> None:

        self.path = payload.get("path")

        self.sheet_name = payload.get("sheetName")

        self.workbook_password = payload.get("password")
