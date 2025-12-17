"""
Custom exceptions for SerializableExcel.
"""


class ExcelModelError(Exception):
    """Base exception for all SerializableExcel errors."""

    pass


class ValidationError(ValueError):
    """Raised when data validation fails during from_excel()."""

    pass


class ColumnNotFoundError(ExcelModelError):
    """Raised when a required column is not found in the Excel file."""

    pass
