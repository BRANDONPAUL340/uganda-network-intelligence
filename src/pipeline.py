from src.transformation.silver import run_silver
from src.transformation.gold import run_gold


def main():

    print("=" * 60)
    print("UGANDA NETWORK & SERVICE INTELLIGENCE PIPELINE")
    print("=" * 60)

    print("\n[1/2] Running SILVER transformations...")
    run_silver()

    print("\n[2/2] Running GOLD transformations...")
    run_gold()

    print("\n" + "=" * 60)
    print("PIPELINE COMPLETED SUCCESSFULLY")
    print("=" * 60)


if __name__ == "__main__":
    main()
