"""Import account type CSV files into SQLite."""

from account_database import DATABASE_PATH, import_account_types


def main():
    inserted = import_account_types(clear_existing=True)
    print(f"Imported {inserted} account type rows into {DATABASE_PATH}")


if __name__ == "__main__":
    main()
