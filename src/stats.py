from pathlib import Path
import duckdb

ROOT = Path(__file__).resolve().parent.parent
con = duckdb.connect((ROOT / "data" / "mandi.duckdb").as_posix(), read_only=True)

print(con.execute("""
    SELECT COUNT(*) AS rows,
           COUNT(DISTINCT market) AS markets,
           COUNT(DISTINCT commodity) AS commodities,
           MAX(arrival_date) AS data_date
    FROM clean_prices
""").df().to_string(index=False))

print(con.execute("""
    SELECT commodity,
           ROUND(MIN(modal_kg), 1) AS cheapest,
           ROUND(MAX(modal_kg), 1) AS dearest,
           ROUND((MAX(modal_kg) - MIN(modal_kg)) / MAX(modal_kg) * 100) AS gap_pct
    FROM clean_prices
    WHERE commodity IN ('Tomato', 'Onion', 'Brinjal')
    GROUP BY commodity
""").df().to_string(index=False))