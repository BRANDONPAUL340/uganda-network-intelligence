from src.database import engine

def run_test():
    print("Attempting to connect to PostgreSQL...")
    with engine.connect() as connection:
        print("Successfully connected to PostgreSQL!")

if __name__ == "__main__":
    run_test()
