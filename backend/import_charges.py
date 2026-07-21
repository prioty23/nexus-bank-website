"""Import structured Schedule of Charges CSV files into SQLite."""

from charge_database import DATABASE_PATH, import_charge_csvs


def main():
    inserted = import_charge_csvs(clear_existing=True)
    print(f"Imported {inserted} charge rows into {DATABASE_PATH}")


if __name__ == "__main__":
    main()
