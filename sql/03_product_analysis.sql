-- 03 PRODUCT ANALYSIS

USE retail_data_warehouse;

-- Top 20 products by revenue
SELECT
    stock_code,
    MAX(description) AS product_name,
    SUM(quantity) AS units_sold,
    ROUND(SUM(revenue), 2) AS total_revenue
FROM fact_retail_transactions
GROUP BY stock_code
ORDER BY total_revenue DESC
LIMIT 20;

-- Top 20 products by quantity sold
SELECT
    stock_code,
    MAX(description) AS product_name,
    SUM(quantity) AS total_quantity
FROM fact_retail_transactions
GROUP BY stock_code
ORDER BY total_quantity DESC
LIMIT 20;

-- Product performance summary
SELECT
    COUNT(DISTINCT stock_code) AS unique_products,
    SUM(quantity) AS total_units_sold,
    ROUND(SUM(revenue), 2) AS total_product_revenue
FROM fact_retail_transactions;
