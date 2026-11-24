from pathlib import Path
import duckdb

ROOT = Path(__file__).resolve().parent.parent
con = duckdb.connect((ROOT / "data" / "mandi.duckdb").as_posix(), read_only=True)

def show(title, sql):
    print(f"\n=== {title} ===")
    print(con.execute(sql).df().to_string(index=False))

show("1. All column names", "DESCRIBE raw_prices")

show("2. Total rows", "SELECT COUNT(*) AS total_rows FROM raw_prices")

show("3. Which states?", """
    SELECT State, COUNT(*) AS rows
    FROM raw_prices GROUP BY State ORDER BY rows DESC
""")

show("4. Which commodities? (top 20)", """
    SELECT Commodity, COUNT(*) AS rows
    FROM raw_prices GROUP BY Commodity ORDER BY rows DESC LIMIT 20
""")

show("5. Tamil Nadu + 3 vegetables", """
    SELECT State, Commodity, COUNT(*) AS rows
    FROM raw_prices
    WHERE State = 'Tamil Nadu'
      AND Commodity IN ('Tomato', 'Onion', 'Brinjal')
    GROUP BY State, Commodity
""")