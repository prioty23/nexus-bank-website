"""Import loan type CSV files into SQLite."""

from loan_database import DATABASE_PATH, import_loan_types


def main():
    inserted = import_loan_types(clear_existing=True)
    print(f"Imported {inserted} loan type rows into {DATABASE_PATH}")


if __name__ == "__main__":
    main()
