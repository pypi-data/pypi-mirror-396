import os
from pathlib import Path

import alembic.command
import alembic.config
import pytest
from sqlalchemy import create_engine, inspect


def _get_test_url() -> str:
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


def _run_alembic_upgrade(db_url: str, project_root: str):
    ini_path = Path(project_root) / "alembic.ini"
    assert ini_path.exists(), f"alembic.ini not found at {ini_path}"

    cfg = alembic.config.Config(str(ini_path))
    prev_db = os.environ.get("DATABASE_URL")
    prev_main = os.environ.get("MAIN_DB_URL")
    os.environ["DATABASE_URL"] = db_url
    try:
        cfg.set_main_option("sqlalchemy.url", db_url)
        cfg.set_main_option("script_location", "migrations")
        alembic.command.upgrade(cfg, "head")
    finally:
        if prev_db is None:
            os.environ.pop("DATABASE_URL", None)
        else:
            os.environ["DATABASE_URL"] = prev_db
        if prev_main is None:
            os.environ.pop("MAIN_DB_URL", None)
        else:
            os.environ["MAIN_DB_URL"] = prev_main


@pytest.mark.postgres
@pytest.mark.skipif(not _get_test_url(), reason="Requires TEST_DATABASE_URL to run")
def test_alembic_upgrade_postgres():
    url = _get_test_url()
    _run_alembic_upgrade(url, project_root=Path(__file__).resolve().parents[2])

    engine = create_engine(url)
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    assert "person" in tables
    assert "alembic_version" in tables
