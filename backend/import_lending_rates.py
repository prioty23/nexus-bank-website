"""Import structured lending interest rate CSV files into SQLite."""

from lending_rate_database import DATABASE_PATH, import_lending_rate_csvs


def main():
    inserted = import_lending_rate_csvs(clear_existing=True)
    print(f"Imported {inserted} lending rate rows into {DATABASE_PATH}")


if __name__ == "__main__":
    main()
