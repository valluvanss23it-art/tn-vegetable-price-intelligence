from pathlib import Path
import duckdb

ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = ROOT / "data" / "raw"
DB_PATH = (ROOT / "data" / "mandi.duckdb").as_posix()

files = list(RAW_DIR.glob("*.csv"))
print("CSV files found:", files)

if not files:
    raise SystemExit(f"No CSV found in {RAW_DIR}. Put your file there and run again.")

file_list = ", ".join(f"'{f.as_posix()}'" for f in files)

con = duckdb.connect(DB_PATH)
con.execute(f"""
    CREATE OR REPLACE TABLE raw_prices AS
    SELECT * FROM read_csv_auto([{file_list}], union_by_name=true)
""")

print("Rows:", con.execute("SELECT COUNT(*) FROM raw_prices").fetchone()[0])

print("\nColumns:")
for col in con.execute("DESCRIBE raw_prices").fetchall():
    print(" ", col[0], "-", col[1])

print("\nFirst 5 rows:")
print(con.execute("SELECT * FROM raw_prices LIMIT 5").df())