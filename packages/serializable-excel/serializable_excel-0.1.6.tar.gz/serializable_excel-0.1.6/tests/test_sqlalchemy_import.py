"""
Tests for importing Excel data into SQLAlchemy models.
"""

import pytest
from faker import Faker
from sqlalchemy.orm import Session

from serializable_excel import Column, ExcelModel
from tests.models import User

fake = Faker()


class UserImportModel(ExcelModel):
    """Excel import model for User SQLAlchemy model."""

    name: str = Column(header="Name", required=True)
    email: str = Column(header="Email", required=True)
    age: int = Column(header="Age", default=0)


def test_import_users_from_excel(db_session: Session, temp_excel_file: str):
    """Test importing users from Excel and creating SQLAlchemy models."""
    # Create Excel file with test data
    import_data = [
        UserImportModel(
            name=fake.name(),
            email=fake.unique.email(),
            age=fake.random_int(min=18, max=80),
        )
        for _ in range(10)
    ]

    # Export to Excel first
    UserImportModel.to_excel(import_data, temp_excel_file)

    # Now import from Excel
    loaded_data = UserImportModel.from_excel(temp_excel_file)

    # Create SQLAlchemy models from imported data
    users = []
    for data in loaded_data:
        user = User(
            name=data.name,
            email=data.email,
            age=data.age,
        )
        db_session.add(user)
        users.append(user)
    db_session.commit()

    # Verify
    assert len(users) == len(import_data), "Should create same number of users"
    assert users[0].name == import_data[0].name
    assert users[0].email == import_data[0].email

    # Verify in database
    db_users = db_session.query(User).all()
    assert len(db_users) == len(users), "Users should be in database"


def test_import_from_bytes(db_session: Session):
    """Test importing users from bytes."""
    # Create Excel data as bytes
    import_data = [
        UserImportModel(
            name=fake.name(),
            email=fake.unique.email(),
            age=fake.random_int(min=18, max=80),
        )
        for _ in range(5)
    ]

    # Export to bytes
    excel_bytes = UserImportModel.to_excel(import_data, return_bytes=True)

    # Import from bytes
    loaded_data = UserImportModel.from_excel(excel_bytes)

    # Create SQLAlchemy models
    users = []
    for data in loaded_data:
        user = User(
            name=data.name,
            email=data.email,
            age=data.age,
        )
        db_session.add(user)
        users.append(user)
    db_session.commit()

    assert len(users) == len(import_data), "Should import from bytes correctly"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
