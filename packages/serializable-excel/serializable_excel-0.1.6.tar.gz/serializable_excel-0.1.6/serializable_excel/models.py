"""
ExcelModel - Base class for Excel-serializable Pydantic models.
"""

from io import BytesIO
from typing import Callable, Dict, List, Optional, Type, TypeVar, Union

from pydantic import BaseModel

from serializable_excel.color_extractor import ColorExtractor
from serializable_excel.excel_reader import ExcelReader
from serializable_excel.excel_writer import ExcelWriter
from serializable_excel.field_extractor import FieldExtractor
from serializable_excel.field_metadata import FieldMetadataExtractor
from serializable_excel.validators import FieldValidator

T = TypeVar('T', bound='ExcelModel')

# Module-level storage for singletons to avoid Pydantic conflicts
_singletons: Dict[type, Dict[str, any]] = {}


class ExcelModel(BaseModel):
    """
    Base class for Excel-serializable Pydantic models.

    Inherit from this class and define fields using Column() or DynamicColumn() descriptors.
    """

    model_config = {'arbitrary_types_allowed': True}

    @classmethod
    def _get_singletons(cls) -> Dict[str, any]:
        """Get or create singletons dictionary for this class."""
        if cls not in _singletons:
            _singletons[cls] = {}
        return _singletons[cls]

    @classmethod
    def _get_reader(cls) -> ExcelReader:
        """Get or create ExcelReader instance (lazy initialization)."""
        singletons = cls._get_singletons()
        if 'reader' not in singletons:
            metadata_extractor = FieldMetadataExtractor()
            validator = FieldValidator()
            singletons['reader'] = ExcelReader(metadata_extractor, validator)
        return singletons['reader']

    @classmethod
    def _get_writer(cls) -> ExcelWriter:
        """Get or create ExcelWriter instance (lazy initialization)."""
        singletons = cls._get_singletons()
        if 'writer' not in singletons:
            metadata_extractor = FieldMetadataExtractor()
            field_extractor = FieldExtractor()
            color_extractor = ColorExtractor()
            singletons['writer'] = ExcelWriter(
                metadata_extractor,
                field_extractor,
                color_extractor,
            )
        return singletons['writer']

    @classmethod
    def from_excel(
        cls: Type[T],
        source: Union[str, bytes, BytesIO],
        dynamic_columns: bool = False,
    ) -> List[T]:
        """
        Read models from an Excel file, bytes, or BytesIO.

        Args:
            source: Path to the Excel file (.xlsx), bytes, or BytesIO object
            dynamic_columns: Enable detection of additional columns not defined in model

        Returns:
            List of model instances

        Raises:
            FileNotFoundError: If the Excel file doesn't exist (only for file paths)
            ValidationError: If validation fails
            ColumnNotFoundError: If a required column is not found

        Example:
            # From file
            users = UserModel.from_excel("users.xlsx")

            # From bytes (e.g., from API request)
            users = UserModel.from_excel(request.files['file'].read())

            # From BytesIO
            users = UserModel.from_excel(BytesIO(file_bytes))
        """
        reader = cls._get_reader()
        return reader.read(cls, source, dynamic_columns)

    @classmethod
    def to_excel(
        cls,
        instances: List[T],
        file_path: Optional[str] = None,
        return_bytes: bool = False,
        column_order: Optional[
            Union[Callable[[str], Optional[int]], Dict[str, int]]
        ] = None,
    ) -> Optional[bytes]:
        """
        Export model instances to an Excel file or return as bytes.

        Args:
            instances: List of model instances to export
            file_path: Path where to save the Excel file (.xlsx).
                       Required if return_bytes=False.
            return_bytes: If True, return Excel content as bytes instead of saving to file.
            column_order: Optional function to specify order for static columns.
                         Takes header name (str) and returns order number (int) or None.
                         Can also be a dict mapping header names to order numbers.

        Returns:
            bytes if return_bytes=True, None otherwise

        Raises:
            ValueError: If instances list is empty or invalid
            ValueError: If file_path is not provided when return_bytes=False

        Example:
            # Save to file
            UserModel.to_excel(users, "users.xlsx")

            # Return bytes for API response
            excel_bytes = UserModel.to_excel(users, return_bytes=True)
            return StreamingResponse(
                BytesIO(excel_bytes),
                media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                headers={"Content-Disposition": "attachment; filename=users.xlsx"}
            )

            # With column ordering
            def static_order(header: str) -> Optional[int]:
                order_map = {"Email": 1, "Name": 2, "Age": 3}
                return order_map.get(header)

            UserModel.to_excel(
                users,
                "output.xlsx",
                column_order=static_order,
            )
        """
        writer = cls._get_writer()
        return writer.write(
            cls,
            instances,
            file_path,
            return_bytes,
            column_order,
        )
