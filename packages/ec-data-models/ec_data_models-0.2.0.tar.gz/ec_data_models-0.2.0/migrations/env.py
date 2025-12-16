# migrations/env.py
from __future__ import annotations

import os
import sys
from logging.config import fileConfig

import alembic_postgresql_enum  # noqa: F401
from alembic import context
from sqlalchemy import create_engine, pool

# Prefer putting src at front so local package wins
sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src"))
)

# IMPORTANT: import models so tables are registered with metadata
from src.models import models  # noqa: F401

config = context.config

# Interpret the config file for Python logging.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Use models' SQLModel metadata for autogenerate
target_metadata = models.SQLModel.metadata


def get_url() -> str:
    # Prefer explicit ALEMBIC_DATABASE_URL, fall back to MAIN_DB_URL or DATABASE_URL
    url = os.getenv("MAIN_DB_URL") or os.getenv("DATABASE_URL")
    if not url:
        from dotenv import load_dotenv

        load_dotenv()
        url = os.getenv("MAIN_DB_URL") or os.getenv("DATABASE_URL")

    if not url:
        raise RuntimeError(
            "Set ALEMBIC_DATABASE_URL, MAIN_DB_URL or DATABASE_URL before "
            "running Alembic"
        )
    return url


def run_migrations_offline() -> None:
    url = get_url()

    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        compare_server_default=True,
        include_schemas=False,  # set True if you use multiple schemas
        render_as_batch=False,  # PostgreSQL doesn't need batch
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    url = get_url()

    connectable = create_engine(url, poolclass=pool.NullPool, pool_pre_ping=True)

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            compare_server_default=True,
            include_schemas=False,
            render_as_batch=False,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
