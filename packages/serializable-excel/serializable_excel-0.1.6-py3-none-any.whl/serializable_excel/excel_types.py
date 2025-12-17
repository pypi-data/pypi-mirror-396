"""
Excel cell type definitions for column formatting.

Provides type classes that map Python types to Excel cell formats.
"""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Optional

from openpyxl.cell import Cell


class ExcelType(ABC):
    """
    Base abstract class for Excel cell types.

    Subclasses define how values are formatted and displayed in Excel cells.
    """

    @abstractmethod
    def apply_format(self, cell: Cell, value: Any) -> None:
        """
        Apply formatting to an Excel cell.

        Args:
            cell: openpyxl Cell object
            value: Value to format
        """
        pass


class ExcelText(ExcelType):
    """
    Text type for Excel cells.

    Forces cell to be formatted as text.
    """

    def apply_format(self, cell: Cell, value: Any) -> None:
        """Apply text formatting to cell."""
        cell.number_format = "@"  # Text format
        if value is not None:
            cell.value = str(value)
        else:
            cell.value = value


class ExcelNumber(ExcelType):
    """
    Number type for Excel cells.

    Args:
        decimal_places: Number of decimal places to display (default: None = auto)
        thousands_separator: Whether to use thousands separator (default: False)
    """

    def __init__(
        self,
        decimal_places: Optional[int] = None,
        thousands_separator: bool = False,
    ):
        self.decimal_places = decimal_places
        self.thousands_separator = thousands_separator

    def apply_format(self, cell: Cell, value: Any) -> None:
        """Apply number formatting to cell."""
        if value is None:
            cell.value = value
            return

        # Build format string
        if self.decimal_places is not None:
            decimal_part = "." + "0" * self.decimal_places
        else:
            decimal_part = ""

        if self.thousands_separator:
            format_str = f"#,##0{decimal_part}"
        else:
            format_str = f"0{decimal_part}" if decimal_part else "0"

        cell.number_format = format_str

        # Convert to number if string
        if isinstance(value, str):
            try:
                value = float(value) if "." in value else int(value)
            except ValueError:
                pass
        cell.value = value


class ExcelDate(ExcelType):
    """
    Date type for Excel cells.

    Args:
        format: Excel date format string (e.g., "DD.MM.YYYY", "YYYY-MM-DD")
                Default is "YYYY-MM-DD" which is standard ISO format.
        python_format: Python datetime format for parsing strings (e.g., "%d.%m.%Y")
                      If not provided, will try to infer from format parameter.
    """

    # Mapping from Python datetime format to Excel format
    _PY_TO_EXCEL = {
        "%d": "DD",
        "%m": "MM",
        "%Y": "YYYY",
        "%y": "YY",
        "%H": "HH",
        "%M": "MM",
        "%S": "SS",
    }

    # Mapping from Excel format to Python format
    _EXCEL_TO_PY = {
        "DD": "%d",
        "MM": "%m",
        "YYYY": "%Y",
        "YY": "%y",
        "HH": "%H",
        "SS": "%S",
    }

    def __init__(
        self,
        format: str = "YYYY-MM-DD",
        python_format: Optional[str] = None,
    ):
        self.format = format
        # Infer python format if not provided
        if python_format:
            self.python_format = python_format
        else:
            self.python_format = self._infer_python_format(format)

    def _infer_python_format(self, excel_format: str) -> str:
        """Infer Python datetime format from Excel format."""
        py_format = excel_format
        for excel_code, py_code in self._EXCEL_TO_PY.items():
            py_format = py_format.replace(excel_code, py_code)
        return py_format

    def apply_format(self, cell: Cell, value: Any) -> None:
        """Apply date formatting to cell."""
        if value is None:
            cell.value = value
            return

        cell.number_format = self.format

        # Convert string to datetime if needed
        if isinstance(value, str):
            try:
                value = datetime.strptime(value, self.python_format)
            except ValueError:
                # If parsing fails, keep as string
                pass

        cell.value = value
