from sqlmodel import SQLModel, create_engine

import src.models.models as models_module  # import models via src package layout


def test_create_schema_sqlite():
    """Quick smoke test: create all tables in an in-memory SQLite DB."""
    # ensure models_module is referenced so static analysis knows it's used
    assert hasattr(models_module, "Person")
    engine = create_engine("sqlite:///:memory:")
    SQLModel.metadata.create_all(engine)
    # If no exception is raised the models are constructible
    assert True
