from pathlib import Path
import duckdb

ROOT = Path(__file__).resolve().parent.parent
con = duckdb.connect((ROOT / "data" / "mandi.duckdb").as_posix(), read_only=True)

cols = [c[0] for c in con.execute("DESCRIBE raw_prices").fetchall()]
print("Columns:", cols)

date_col = next((c for c in cols if "date" in c.lower()), None)
print("Date column:", date_col)

if date_col:
    print(con.execute(f"""
        SELECT MIN({date_col}) AS first_day,
               MAX({date_col}) AS last_day,
               COUNT(DISTINCT {date_col}) AS distinct_days
        FROM raw_prices
    """).df().to_string(index=False))

print(con.execute("""
    SELECT Commodity, COUNT(*) AS rows
    FROM raw_prices
    WHERE State = 'Tamil Nadu'
    GROUP BY Commodity
    ORDER BY rows DESC
    LIMIT 25
""").df().to_string(index=False))