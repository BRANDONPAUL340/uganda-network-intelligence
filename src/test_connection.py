from sqlalchemy import text

from src.database import engine


def test_connection():

    with engine.connect() as connection:

        result = connection.execute(
            text("SELECT version();")
        )

        version = result.scalar()

        print("Database connection successful.")
        print(version)


if __name__ == "__main__":
    test_connection()
