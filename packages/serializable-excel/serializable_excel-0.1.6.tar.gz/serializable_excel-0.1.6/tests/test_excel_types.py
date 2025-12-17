"""
Tests for Excel type formatting.
"""

from datetime import datetime
from typing import Any

import pytest

from serializable_excel import (
    Column,
    DynamicColumn,
    ExcelDate,
    ExcelModel,
    ExcelNumber,
    ExcelText,
)


def datetime_to_str(value: Any) -> str:
    """Convert datetime to string for reading back from Excel."""
    if isinstance(value, datetime):
        return value.strftime('%d.%m.%Y')
    return str(value) if value else ''


class TypedUserModel(ExcelModel):
    """Model with explicit Excel types."""

    name: str = Column(header='Name', excel_type=ExcelText())
    age: int = Column(header='Age', excel_type=ExcelNumber())
    salary: float = Column(
        header='Salary',
        excel_type=ExcelNumber(decimal_places=2, thousands_separator=True),
    )
    birth_date: str = Column(
        header='Birth Date',
        excel_type=ExcelDate('DD.MM.YYYY', python_format='%d.%m.%Y'),
        validator=datetime_to_str,
    )


def test_export_with_excel_types(temp_excel_file: str):
    """Test exporting with explicit Excel types."""
    users = [
        TypedUserModel(
            name='Alice Johnson',
            age=30,
            salary=75000.50,
            birth_date='15.03.1994',
        ),
        TypedUserModel(
            name='Bob Smith',
            age=25,
            salary=55000.00,
            birth_date='22.07.1999',
        ),
    ]

    # Export to Excel
    TypedUserModel.to_excel(users, temp_excel_file)

    # Read back and verify
    loaded = TypedUserModel.from_excel(temp_excel_file)
    assert len(loaded) == 2
    assert loaded[0].name == 'Alice Johnson'
    # Dates are converted back via validator
    assert loaded[0].birth_date == '15.03.1994'


def test_export_with_excel_types_to_bytes():
    """Test exporting with Excel types to bytes."""
    users = [
        TypedUserModel(
            name='Charlie',
            age=35,
            salary=90000.00,
            birth_date='01.01.1989',
        ),
    ]

    # Export to bytes
    excel_bytes = TypedUserModel.to_excel(users, return_bytes=True)
    assert excel_bytes is not None
    assert len(excel_bytes) > 0


def get_dynamic_type(column_name: str):
    """Determine Excel type for dynamic columns."""
    col_lower = column_name.lower()
    if 'date' in col_lower:
        return ExcelDate('DD.MM.YYYY', python_format='%d.%m.%Y')
    elif 'count' in col_lower or 'quantity' in col_lower:
        return ExcelNumber()
    elif 'price' in col_lower or 'amount' in col_lower:
        return ExcelNumber(decimal_places=2)
    return ExcelText()


class DynamicTypedModel(ExcelModel):
    """Model with dynamic column type getter."""

    name: str = Column(header='Name')
    characteristics: dict = DynamicColumn(type_getter=get_dynamic_type)


def test_dynamic_columns_with_type_getter(temp_excel_file: str):
    """Test dynamic columns with type_getter."""
    items = [
        DynamicTypedModel(
            name='Product A',
            characteristics={
                'Price': 99.99,
                'Quantity': 100,
                'Release Date': '01.06.2024',
            },
        ),
        DynamicTypedModel(
            name='Product B',
            characteristics={
                'Price': 149.99,
                'Quantity': 50,
                'Release Date': '15.08.2024',
            },
        ),
    ]

    # Export to Excel
    DynamicTypedModel.to_excel(items, temp_excel_file)

    # Read back and verify
    loaded = DynamicTypedModel.from_excel(
        temp_excel_file, dynamic_columns=True
    )
    assert len(loaded) == 2
    assert loaded[0].name == 'Product A'
    assert 'Price' in loaded[0].characteristics


class GetterDynamicModel(ExcelModel):
    """Model using getter to provide dynamic values."""

    name: str = Column(header='Name')
    extras: dict = DynamicColumn(
        getter=lambda inst: {'Computed': inst.name.upper()}
    )


def test_dynamic_columns_with_getter(temp_excel_file: str):
    """DynamicColumn should use getter to fetch values when exporting."""
    items = [
        GetterDynamicModel(name='alpha'),
        GetterDynamicModel(name='beta'),
    ]

    GetterDynamicModel.to_excel(items, temp_excel_file)
    loaded = GetterDynamicModel.from_excel(
        temp_excel_file, dynamic_columns=True
    )

    assert len(loaded) == 2
    assert loaded[0].extras['Computed'] == 'ALPHA'
    assert loaded[1].extras['Computed'] == 'BETA'


def test_excel_date_format():
    """Test ExcelDate with different formats."""
    # European format
    date_type = ExcelDate('DD.MM.YYYY', python_format='%d.%m.%Y')
    assert date_type.format == 'DD.MM.YYYY'
    assert date_type.python_format == '%d.%m.%Y'

    # ISO format (inferred python format)
    date_type2 = ExcelDate('YYYY-MM-DD')
    assert date_type2.format == 'YYYY-MM-DD'
    assert date_type2.python_format == '%Y-%m-%d'


def test_excel_number_formats():
    """Test ExcelNumber with different formats."""
    # Default
    num = ExcelNumber()
    assert num.decimal_places is None
    assert num.thousands_separator is False

    # With decimal places
    num2 = ExcelNumber(decimal_places=2)
    assert num2.decimal_places == 2

    # With thousands separator
    num3 = ExcelNumber(decimal_places=2, thousands_separator=True)
    assert num3.thousands_separator is True


def test_mixed_types_model(temp_excel_file: str):
    """Test model with mix of typed and untyped columns."""

    def date_validator(value: Any) -> str:
        if isinstance(value, datetime):
            return value.strftime('%Y-%m-%d')
        return str(value) if value else ''

    class MixedModel(ExcelModel):
        """Mix of typed and auto-detected columns."""

        # Explicit types
        price: float = Column(
            header='Price', excel_type=ExcelNumber(decimal_places=2)
        )
        date: str = Column(
            header='Date',
            excel_type=ExcelDate('YYYY-MM-DD'),
            validator=date_validator,
        )
        # No explicit type - auto-detect
        name: str = Column(header='Name')
        quantity: int = Column(header='Quantity')

    items = [
        MixedModel(price=99.99, date='2024-01-15', name='Widget', quantity=10),
        MixedModel(price=149.99, date='2024-02-20', name='Gadget', quantity=5),
    ]

    MixedModel.to_excel(items, temp_excel_file)
    loaded = MixedModel.from_excel(temp_excel_file)

    assert len(loaded) == 2
    assert loaded[0].name == 'Widget'
    assert loaded[0].date == '2024-01-15'


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
