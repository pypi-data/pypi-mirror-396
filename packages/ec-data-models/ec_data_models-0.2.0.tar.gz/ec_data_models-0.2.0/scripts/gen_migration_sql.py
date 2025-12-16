"""Generate SQL for Alembic migrations programmatically.

This script loads alembic config, sets the DB URL,
and writes the SQL for 'upgrade head' to stdout.
"""

import sys
from typing import TYPE_CHECKING, Any

from alembic import command  # type: ignore[attr-defined]
from alembic.config import Config

if TYPE_CHECKING:
    # mypy can't see alembic's dynamic runtime attributes; keep block present
    # but avoid importing problematic submodules here.
    pass

# At runtime alembic exposes some dynamic modules/attributes; help mypy by
# annotating expected symbols as Any.
script: Any  # type: ignore

if len(sys.argv) < 2:
    print("Usage: gen_migration_sql.py <sqlalchemy_url>")
    sys.exit(2)

url = sys.argv[1]
cfg = Config("alembic.ini")
cfg.set_main_option("sqlalchemy.url", url)
# Ensure script_location picks up our alembic package
cfg.set_main_option("script_location", "alembic")

# Generate SQL and print to stdout
command.upgrade(cfg, "head", sql=True)
command.upgrade(cfg, "head", sql=True)
