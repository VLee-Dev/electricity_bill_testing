from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url

from app.config import settings


def main() -> None:
    admin_url = make_url(settings.database_url).set(database="postgres")
    engine = create_engine(admin_url, isolation_level="AUTOCOMMIT")
    with engine.connect() as connection:
        exists = connection.execute(
            text("SELECT 1 FROM pg_database WHERE datname = :name"),
            {"name": make_url(settings.database_url).database},
        ).scalar()
        if not exists:
            connection.exec_driver_sql(f'CREATE DATABASE "{make_url(settings.database_url).database}"')
            print("Database đã được tạo.")
        else:
            print("Database đã tồn tại.")
    engine.dispose()


if __name__ == "__main__":
    main()
