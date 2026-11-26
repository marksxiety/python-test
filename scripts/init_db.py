"""Create the configured SQLAlchemy tables explicitly."""

from app.core.logging import print_logging
from app.database.connection import create_tables


def main() -> None:
    """Create the tables registered with the shared declarative base."""
    create_tables()
    print_logging("info", "Database schema initialized")


if __name__ == "__main__":
    main()
