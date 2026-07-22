"""Import structured deposit interest rate CSV files into SQLite."""

from deposit_rate_database import DATABASE_PATH, import_deposit_rate_csvs


def main():
    inserted = import_deposit_rate_csvs(clear_existing=True)
    print(f"Imported {inserted} deposit rate rows into {DATABASE_PATH}")


if __name__ == "__main__":
    main()
