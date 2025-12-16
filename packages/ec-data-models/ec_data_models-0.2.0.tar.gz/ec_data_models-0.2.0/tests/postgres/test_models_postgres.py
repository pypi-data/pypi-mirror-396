import os
import time

import pytest
from sqlmodel import Session, SQLModel, create_engine, select

import src.models.models as models


def _get_test_url() -> str:
    # Prefer TEST_DATABASE_URL env var, fall back to MAIN_DB_URL/DATABASE_URL
    url = (
        os.getenv("TEST_DATABASE_URL")
        or os.getenv("MAIN_DB_URL")
        or os.getenv("DATABASE_URL")
    )
    if not url:
        from dotenv import load_dotenv

        load_dotenv()
        url = (
            os.getenv("TEST_DATABASE_URL")
            or os.getenv("MAIN_DB_URL")
            or os.getenv("DATABASE_URL")
        )
    return url  # type: ignore


@pytest.mark.postgres
@pytest.mark.skipif(not _get_test_url(), reason="Requires TEST_DATABASE_URL to run")
def test_models_postgres_insert():
    """Postgres-only test: create schema and perform simple insert/query."""
    url = _get_test_url()
    engine = create_engine(url)

    # create tables (uses Postgres-specific enum types etc.)
    SQLModel.metadata.create_all(engine)

    # Use a unique email to avoid conflicts on repeated test runs
    test_email = f"pg_pgtest_{int(time.time() * 1000000)}@example.org"

    with Session(engine) as session:
        person = models.Person(email=test_email)
        session.add(person)
        session.commit()
        session.refresh(person)
        person_id = person.id

        # Verify the person was inserted
        res = session.exec(
            select(models.Person).where(models.Person.email == test_email)
        ).one()
        assert res.email == test_email
        assert res.id == person_id

        # Clean up: delete the test person to keep database clean
        session.delete(person)
        session.commit()

        # Verify deletion
        deleted = session.exec(
            select(models.Person).where(models.Person.email == test_email)
        ).first()
        assert deleted is None
