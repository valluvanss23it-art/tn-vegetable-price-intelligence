-- 1. Average price per commodity
SELECT commodity, ROUND(AVG(modal_kg), 2) AS avg_rs_kg, COUNT(*) AS rows
FROM clean_prices
GROUP BY commodity
ORDER BY rows DESC;

-- 2. Cheapest market per commodity on the latest date
WITH ranked AS (
  SELECT commodity, market, district, modal_kg,
         ROW_NUMBER() OVER (PARTITION BY commodity ORDER BY modal_kg) AS rn
  FROM clean_prices
  WHERE arrival_date = (SELECT MAX(arrival_date) FROM clean_prices)
)
SELECT commodity, market, district, modal_kg
FROM ranked WHERE rn = 1
ORDER BY commodity;

-- 3. Price gap between cheapest and dearest market
SELECT commodity,
       ROUND(MIN(modal_kg), 1) AS cheapest,
       ROUND(MAX(modal_kg), 1) AS dearest,
       ROUND((MAX(modal_kg) - MIN(modal_kg)) / MAX(modal_kg) * 100) AS gap_pct
FROM clean_prices
GROUP BY commodity
HAVING COUNT(*) >= 5
ORDER BY gap_pct DESC;

-- 4. Markets priced above their commodity average (window function)
SELECT commodity, market, modal_kg,
       ROUND(AVG(modal_kg) OVER (PARTITION BY commodity), 2) AS commodity_avg,
       ROUND(modal_kg / AVG(modal_kg) OVER (PARTITION BY commodity) - 1, 3) AS pct_vs_avg
FROM clean_prices
ORDER BY pct_vs_avg DESC
LIMIT 20;

-- 5. Markets reporting per district
SELECT district, COUNT(DISTINCT market) AS markets
FROM clean_prices
GROUP BY district
ORDER BY markets DESC;
