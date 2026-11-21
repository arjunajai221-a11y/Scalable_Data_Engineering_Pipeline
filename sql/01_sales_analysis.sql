-- 01 SALES ANALYSIS

USE retail_data_warehouse;

-- Overall business KPIs
SELECT
    COUNT(DISTINCT invoice) AS total_orders,
    COUNT(DISTINCT customer_id) AS total_customers,
    SUM(quantity) AS total_units_sold,
    ROUND(SUM(revenue), 2) AS total_revenue,
    ROUND(AVG(revenue), 2) AS average_line_revenue
FROM fact_retail_transactions;

-- Monthly revenue trend
SELECT
    invoice_year,
    invoice_month,
    ROUND(SUM(revenue), 2) AS monthly_revenue
FROM fact_retail_transactions
GROUP BY invoice_year, invoice_month
ORDER BY invoice_year, invoice_month;

-- Yearly revenue
SELECT
    invoice_year,
    ROUND(SUM(revenue), 2) AS yearly_revenue
FROM fact_retail_transactions
GROUP BY invoice_year
ORDER BY invoice_year;

-- Top 10 revenue-generating months
SELECT
    invoice_year,
    invoice_month,
    ROUND(SUM(revenue), 2) AS revenue
FROM fact_retail_transactions
GROUP BY invoice_year, invoice_month
ORDER BY revenue DESC
LIMIT 10;
