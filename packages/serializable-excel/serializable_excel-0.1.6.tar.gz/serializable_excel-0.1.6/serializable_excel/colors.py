"""
Color constants and utilities for Excel cell styling.
"""

from dataclasses import dataclass
from typing import Optional

from openpyxl.cell import Cell
from openpyxl.styles import Font, PatternFill


@dataclass
class CellStyle:
    """
    Represents cell styling options.

    Args:
        fill_color: Background color in HEX format (e.g., "FF0000" for red)
        font_color: Font color in HEX format
        font_bold: Whether the font should be bold
        font_italic: Whether the font should be italic
    """

    fill_color: Optional[str] = None
    font_color: Optional[str] = None
    font_bold: bool = False
    font_italic: bool = False


# Predefined color constants for common use cases
class Colors:
    """Predefined color constants."""

    # Background colors
    CHANGED = "FFFF00"  # Yellow - for changed values
    UNCHANGED = "90EE90"  # Light green - for unchanged values
    ERROR = "FF6B6B"  # Light red - for errors
    WARNING = "FFA500"  # Orange - for warnings
    INFO = "87CEEB"  # Light blue - for information
    NEW = "98FB98"  # Pale green - for new entries

    # Font colors
    FONT_RED = "FF0000"
    FONT_GREEN = "008000"
    FONT_BLUE = "0000FF"
    FONT_BLACK = "000000"
    FONT_GRAY = "808080"


class CellStyleApplier:
    """Applies CellStyle to openpyxl cells."""

    @staticmethod
    def apply(cell: Cell, style: CellStyle) -> None:
        """
        Apply a CellStyle to an openpyxl cell.

        Args:
            cell: openpyxl Cell object
            style: CellStyle to apply
        """
        if style is None:
            return

        # Apply fill color
        if style.fill_color is not None:
            cell.fill = PatternFill(
                start_color=style.fill_color,
                end_color=style.fill_color,
                fill_type="solid",
            )

        # Apply font styling
        if style.font_color is not None or style.font_bold or style.font_italic:
            cell.font = Font(
                color=style.font_color,
                bold=style.font_bold,
                italic=style.font_italic,
            )
