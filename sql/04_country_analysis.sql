-- 04 COUNTRY ANALYSIS

USE retail_data_warehouse;

-- Country-wise revenue
SELECT
    country,
    COUNT(DISTINCT invoice) AS total_orders,
    COUNT(DISTINCT customer_id) AS total_customers,
    SUM(quantity) AS total_quantity,
    ROUND(SUM(revenue), 2) AS total_revenue
FROM fact_retail_transactions
GROUP BY country
ORDER BY total_revenue DESC;

-- Top 10 countries by revenue
SELECT
    country,
    ROUND(SUM(revenue), 2) AS total_revenue
FROM fact_retail_transactions
GROUP BY country
ORDER BY total_revenue DESC
LIMIT 10;

-- Country-wise average order value
SELECT
    country,
    ROUND(SUM(revenue) / NULLIF(COUNT(DISTINCT invoice), 0), 2)
        AS average_order_value
FROM fact_retail_transactions
GROUP BY country
ORDER BY average_order_value DESC;
