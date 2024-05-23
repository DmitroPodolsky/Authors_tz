from pathlib import Path

from alembic import command
from alembic.config import Config
from loguru import logger

from app.config import project_dir
from app.config import settings


def migrate() -> None:
    """
    Function to generate and apply a new migration.
    """

    alembic_cfg = Config(settings.DB_PATH / "alembic.ini")

    # Generate a new migration script
    command.revision(alembic_cfg, autogenerate=True, message="Auto-generated migration")

    # Locate the newest migration file by finding the file with the latest creation time
    migrations_directory = project_dir / "db" / "migrations" / "versions"
    migration_files = [
        p for p in migrations_directory.iterdir() if p.is_file() and p.suffix == ".py"
    ]

    newest_migration_path = max(migration_files, key=lambda p: p.stat().st_mtime)

    # Check if the newly generated migration script is empty
    if is_migration_empty(newest_migration_path):
        logger.info(
            "Generated migration is empty. No changes to apply. Deleting migration file and cache."
        )
        newest_migration_path.unlink()
        newest_cache_path = max(
            (migrations_directory / "__pycache__").iterdir(),
            key=lambda p: p.stat().st_mtime,
        )
        newest_cache_path.unlink()
        logger.info("Deleted migration file and cache.")
    else:
        logger.info("Applying migration.")
        command.upgrade(alembic_cfg, "head")
        logger.success("Migration applied.")


def is_migration_empty(migration_file_path: Path) -> bool:
    """
    Function to check if the migration script is empty.

    Args:
        migration_file_path (Path): Path to the migration script.

    Returns:
        bool: True if the migration script is empty, False otherwise.
    """
    with migration_file_path.open("r", encoding="utf-8") as file:
        migration_text = file.read()

    upgrade_start = migration_text.find("def upgrade()")
    upgrade_end = migration_text.find("# ### end Alembic commands ###", upgrade_start)
    upgrade_content = migration_text[upgrade_start:upgrade_end]

    downgrade_start = migration_text.find("def downgrade()")
    downgrade_end = migration_text.find(
        "# ### end Alembic commands ###", downgrade_start
    )
    downgrade_content = migration_text[downgrade_start:downgrade_end]

    def check_block_content(block):
        lines = [line.strip() for line in block.splitlines()]
        return any(line == "pass" for line in lines)

    return check_block_content(upgrade_content) and check_block_content(
        downgrade_content
    )
