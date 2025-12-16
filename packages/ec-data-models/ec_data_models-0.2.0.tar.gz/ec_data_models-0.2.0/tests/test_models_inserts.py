from pathlib import Path

from sqlmodel import Session, SQLModel, create_engine, select

import src.models.models as models
from src.models.enums import Tags


def test_create_and_insert_models_sqlite(tmp_path: Path):
    """Create schema on a temporary SQLite file and perform basic inserts/queries."""
    db_file = tmp_path / "test_models.db"
    url = f"sqlite:///{db_file.as_posix()}"
    engine = create_engine(url)

    # create tables
    SQLModel.metadata.create_all(engine)

    # basic insert and read back
    with Session(engine) as session:
        person = models.Person(email="alice@example.org", first_name="Alice")
        session.add(person)
        session.commit()
        session.refresh(person)

        # create Member with same PK as Person (one-to-one)
        member = models.Member(id=person.id, ec_email="alice@ec.org")
        session.add(member)
        session.commit()

        # create an event with tags (stored as JSON)
        ev = models.Event(type=models.EventType.internal, tags=[Tags.Investors.value])
        session.add(ev)
        session.commit()
        session.refresh(ev)

        # verify queries
        p = session.exec(
            select(models.Person).where(models.Person.email == "alice@example.org")
        ).one()
        assert p.first_name == "Alice"

        m = session.exec(
            select(models.Member).where(models.Member.id == person.id)
        ).one()
        assert m.ec_email == "alice@ec.org"

        e = session.exec(select(models.Event).where(models.Event.id == ev.id)).one()
        # tags persisted as list of strings
        assert e.tags and isinstance(e.tags, list)
