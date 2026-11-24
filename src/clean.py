from pathlib import Path
import duckdb

ROOT = Path(__file__).resolve().parent.parent
con = duckdb.connect((ROOT / "data" / "mandi.duckdb").as_posix())

# 1. Column names fix: Modal_x0020_Price -> modal_price
cols = [c[0] for c in con.execute("DESCRIBE raw_prices").fetchall()]
select = ", ".join(f'"{c}" AS {c.replace("_x0020_", "_").lower()}' for c in cols)
con.execute(f"CREATE OR REPLACE TABLE stg AS SELECT {select} FROM raw_prices")
print("Columns now:", [c[0] for c in con.execute("DESCRIBE stg").fetchall()])

# 2. Clean table: Tamil Nadu only, valid prices, no duplicates, Rs per kg
con.execute("""
    CREATE OR REPLACE TABLE clean_prices AS
    SELECT DISTINCT
        state, district, market, commodity,
        COALESCE(
            TRY_STRPTIME(CAST(arrival_date AS VARCHAR), '%d/%m/%Y'),
            TRY_CAST(arrival_date AS TIMESTAMP)
        )::DATE AS arrival_date,
        min_price / 100.0   AS min_kg,
        max_price / 100.0   AS max_kg,
        modal_price / 100.0 AS modal_kg
    FROM stg
    WHERE state = 'Tamil Nadu'
      AND modal_price IS NOT NULL
      AND modal_price > 0
""")

print("\nClean rows:", con.execute("SELECT COUNT(*) FROM clean_prices").fetchone()[0])
print(con.execute("""
    SELECT MIN(arrival_date) AS first_day, MAX(arrival_date) AS last_day,
           COUNT(DISTINCT arrival_date) AS days,
           COUNT(DISTINCT market) AS markets,
           COUNT(DISTINCT commodity) AS commodities
    FROM clean_prices
""").df().to_string(index=False))
print(con.execute("""
    SELECT commodity, COUNT(*) AS rows FROM clean_prices
    GROUP BY commodity ORDER BY rows DESC LIMIT 15
""").df().to_string(index=False))