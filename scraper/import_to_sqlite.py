import sqlite3
import csv
import os
import pandas as pd

def create_connection(db_file):
    try:
        conn = sqlite3.connect(db_file)
        print(f"✅ Connected to {db_file}")
        return conn
    except sqlite3.Error as e:
        print(f"❌ Error connecting to database: {e}")
        return None

def import_csv_to_table(conn, csv_path, table_name, columns_types, clean_data=True):
    if not os.path.exists(csv_path):
        print(f"⚠️ File not found: {csv_path}")
        return

    try:
        print(f"\n📂 Loading raw data from: {csv_path}")
        df = pd.read_csv(csv_path)

        print("🔹 BEFORE CLEANING:")
        print(df.head())

        if clean_data:
            # Count how many duplicates were found (compare with length)
            num_duplicates_removed = df.shape[0] - df.drop_duplicates().shape[0]
            df.drop_duplicates(inplace=True)

            # Count rows with missing values in key columns before removal
            num_na_removed = df[["Player", "Event", "Value"]].isna().any(axis=1).sum()
            df.dropna(subset=["Player", "Event", "Value"], inplace=True)

            if "Value" in df.columns:
                df["Value"] = pd.to_numeric(df["Value"], errors="coerce")

                na_after_value_conversion = df["Value"].isna().sum()
                num_na_removed += na_after_value_conversion
                df.dropna(subset=["Value"], inplace=True)

            print(f"Duplicates removed: {num_duplicates_removed}")
            print(f"Removed rows with missing values: {num_na_removed}")

            print("🔹 AFTER CLEANING:")
            print(df.head())

        # Overwriting CSV after cleaning
        temp_cleaned_csv = csv_path.replace(".csv", "_cleaned.csv")
        df.to_csv(temp_cleaned_csv, index=False)

        cur = conn.cursor()
        cur.execute(f"DROP TABLE IF EXISTS {table_name}")
        cur.execute(f"CREATE TABLE {table_name} ({', '.join(columns_types)})")

        with open(temp_cleaned_csv, newline='', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            headers = next(reader)
            placeholders = ", ".join(["?" for _ in headers])
            insert_sql = f"INSERT INTO {table_name} VALUES ({placeholders})"

            row_count = 0
            for row in reader:
                if len(row) != len(headers):
                    print(f"⏩ Skipping malformed row: {row}")
                    continue

                cur.execute(insert_sql, row)
                row_count += 1

        conn.commit()
        print(f"✅ Imported {row_count} rows into table: {table_name}")

        os.remove(temp_cleaned_csv)

    except Exception as e:
        print(f"❌ Error processing {csv_path}: {e}")

def main():
    db_path = "../data/mlb_stats.db"
    conn = create_connection(db_path)

    if conn:
        import_csv_to_table(
            conn,
            "../data/american_league_stats_1901_2024.csv",
            "hitting_stats",
            [
                "Year INTEGER",
                "Event TEXT",
                "Player TEXT",
                "Team TEXT",
                "Value REAL"
            ],
            clean_data=True
        )

        import_csv_to_table(
            conn,
            "../data/american_league_pitcher_stats_1901_2024.csv",
            "pitching_stats",
            [
                "Year INTEGER",
                "Event TEXT",
                "Player TEXT",
                "Team TEXT",
                "Value REAL"
            ],
            clean_data=True
        )

        import_csv_to_table(
            conn,
            "../data/mlb_events.csv",
            "events",
            [
                "Event TEXT PRIMARY KEY",
                "Description TEXT"
            ],
            clean_data=False  # No cleaning needed for mlb_events
        )

        conn.close()
        print("\n✅ Import completed and connection closed.")

if __name__ == "__main__":
    main()


