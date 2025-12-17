"""
SerializableExcel - A library for bidirectional conversion between Excel and Pydantic models.
"""

__version__ = "0.1.4"

from serializable_excel.colors import CellStyle, Colors
from serializable_excel.descriptors import Column, DynamicColumn
from serializable_excel.excel_types import (
    ExcelDate,
    ExcelNumber,
    ExcelText,
    ExcelType,
)
from serializable_excel.exceptions import (
    ColumnNotFoundError,
    ExcelModelError,
    ValidationError,
)
from serializable_excel.models import ExcelModel

__all__ = [
    # Model
    "ExcelModel",
    # Descriptors
    "Column",
    "DynamicColumn",
    # Exceptions
    "ExcelModelError",
    "ValidationError",
    "ColumnNotFoundError",
    # Styling
    "CellStyle",
    "Colors",
    # Excel Types
    "ExcelType",
    "ExcelText",
    "ExcelNumber",
    "ExcelDate",
]
