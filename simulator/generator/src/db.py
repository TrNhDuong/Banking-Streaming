import os


def dsn() -> str:
    """Build psycopg connection string from environment variables."""
    return (
        f"host={os.getenv('POSTGRES_HOST', 'postgres')} "
        f"port=5432 "
        f"dbname={os.getenv('POSTGRES_DB', 'banking')} "
        f"user={os.getenv('POSTGRES_USER', 'bank_admin')} "
        f"password={os.getenv('POSTGRES_PASSWORD', 'bank_admin_password')}"
    )
