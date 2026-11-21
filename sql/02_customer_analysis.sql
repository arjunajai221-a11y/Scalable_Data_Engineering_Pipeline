-- 02 CUSTOMER ANALYSIS

USE retail_data_warehouse;

-- Customer purchase summary
SELECT
    customer_id,
    COUNT(DISTINCT invoice) AS total_orders,
    SUM(quantity) AS total_quantity,
    ROUND(SUM(revenue), 2) AS total_spending
FROM fact_retail_transactions
WHERE customer_id IS NOT NULL
GROUP BY customer_id
ORDER BY total_spending DESC
LIMIT 20;

-- Top 10 customers by revenue
SELECT
    customer_id,
    ROUND(SUM(revenue), 2) AS total_revenue
FROM fact_retail_transactions
WHERE customer_id IS NOT NULL
GROUP BY customer_id
ORDER BY total_revenue DESC
LIMIT 10;

-- Customer purchase frequency
SELECT
    customer_id,
    COUNT(DISTINCT invoice) AS purchase_frequency
FROM fact_retail_transactions
WHERE customer_id IS NOT NULL
GROUP BY customer_id
ORDER BY purchase_frequency DESC
LIMIT 10;

-- Customer spending segments
SELECT
    CASE
        WHEN total_spending >= 10000 THEN 'High Value'
        WHEN total_spending >= 1000 THEN 'Medium Value'
        ELSE 'Low Value'
    END AS customer_segment,
    COUNT(*) AS customer_count
FROM (
    SELECT
        customer_id,
        SUM(revenue) AS total_spending
    FROM fact_retail_transactions
    WHERE customer_id IS NOT NULL
    GROUP BY customer_id
) AS customer_summary
GROUP BY customer_segment
ORDER BY customer_count DESC;
