from sqlalchemy import create_engine

from app.core.config.settings import settings
from app.infrastructure.db.base import Base
from app.modules.tasks.infrastructure.task_model import TaskModel  # noqa: F401


def bootstrap_database() -> None:
    """Create missing database tables using the migration database user."""
    engine = create_engine(
        settings.database_migration_url,
        echo=False,
        future=True,
        pool_pre_ping=True,
    )
    Base.metadata.create_all(bind=engine)