# Ejericio 2.1
SELECT 
	country,
	status,
	count(amount) AS num_operaciones,
	avg(amount) AS importe_promedio
FROM orders
WHERE 
	(date(created_at) > '2015-07-01') AND
	(country IN ('Francia', 'Portugal', 'EspaÃ±a')) AND
	(amount BETWEEN 100 AND 1500)
GROUP BY country, status
ORDER BY importe_promedio DESC;

# Ejercicio 2.2
SELECT
	country,
    count(*) AS num_operaciones,
    sum(amount) AS total_operaciones,
    max(amount) AS max_operación,
    min(amount) AS min_operación
FROM orders
WHERE 
	status NOT IN ('DELINQUENT', 'CANCELLED') AND
    amount > 100
GROUP BY country
ORDER BY num_operaciones DESC
LIMIT 3;

# Ejercicio 3.1
SELECT
	m.ï»¿merchant_id AS merchant_id,
    m.name AS nombre_comercio,
    o.country,
    count(*) AS num_operaciones,
    avg(o.amount) AS promedio_operaciones,
	count(r.refunded_at) AS num_devoluciones,
	CASE WHEN count(r.refunded_at) > 0 THEN 'Sí' ELSE 'No' END AS acepta_devoluciones
FROM orders AS o 
INNER JOIN merchants AS m ON o.merchant_id = m.ï»¿merchant_id
LEFT JOIN refunds AS r ON o.ï»¿order_id = r.ï»¿order_id
GROUP BY nombre_comercio, o.country, merchant_id
HAVING 
	(num_operaciones > 10) AND
    (country IN ('Marruecos', 'Italia', 'EspaÃ±a', 'Portugal'))
ORDER BY num_operaciones ASC;

# Ejercicio 3.2
CREATE VIEW orders_view AS
SELECT
	o.ï»¿order_id AS order_id,
	date(o.created_at),
	o.status,
	o.amount,
	o.merchant_id,
	o.country,
   	m.name AS nombre_comercio,
	sum(r.amount) AS monto_devoluciones,
	count(r.refunded_at) AS num_devoluciones
FROM orders AS o
INNER JOIN merchants AS m ON o.merchant_id = m.ï»¿merchant_id
LEFT JOIN refunds AS r ON o.ï»¿order_id = r.ï»¿order_id
GROUP BY 1, 2, 3, 4, 5, 6, 7
;
SELECT * FROM orders_view;

# Ejercicio 4
-- Operaciones por países
SELECT 
	country,
    count(amount) AS num_operación,
    round(sum(amount), 2) AS total_operación
FROM orders
GROUP BY country
ORDER BY 3 DESC
;

-- Crear view con las columnas necesarias (España)
CREATE VIEW españa_funcionalidad AS
SELECT 
	o.country,
    m.name as nombre_comercio,
	o.created_at,
    o.amount as monto_operación,
    CASE 
		WHEN r.amount IS NOT NULL THEN r.amount ELSE 0
    END AS monto_devolución
FROM orders AS o
INNER JOIN merchants AS m ON o.merchant_id = m.ï»¿merchant_id
LEFT JOIN refunds AS r ON o.ï»¿order_id = r.ï»¿order_id
WHERE country = 'EspaÃ±a'
;
SELECT * FROM españa_funcionalidad;

-- Conocer el sumatorio del total_operación_neto en España
SELECT ROUND(SUM(total_operación_neto),2) AS sumatorio_total_operación_neto
FROM (SELECT (SUM(monto_operación) - SUM(monto_devolución)) AS total_operación_neto FROM devolucion_mes) AS subconsulta;

-- Operaciones por mes en España
SELECT 
	country,
    month(created_at) AS mes,
	count(monto_operación) AS num_operación,
    round(sum(monto_operación),2) AS total_operación,
	sum(monto_devolución) AS total_devolución,
    round(sum(monto_operación) - sum(monto_devolución),2) AS total_operación_neto,
    round((sum(monto_operación) - sum(monto_devolución)) /
    		(SELECT ROUND(SUM(total_operación_neto),2) 
			FROM (SELECT (SUM(monto_operación) - SUM(monto_devolución)) AS total_operación_neto FROM devolucion_mes) AS subconsulta) 
			* 100,2)  AS contribución_total_operación_neto
FROM españa_funcionalidad
GROUP BY mes
;

-- Operaciones por comercio en España
SELECT
	country,
    nombre_comercio,
	count(monto_operación) AS num_operación,
    round(sum(monto_operación),2) AS total_operación,
	sum(monto_devolución) AS total_devolución,
    round(sum(monto_operación) - sum(monto_devolución),2) AS total_operación_neto,
    round((sum(monto_operación) - sum(monto_devolución)) /
    		(SELECT ROUND(SUM(total_operación_neto),2) 
			FROM (SELECT (SUM(monto_operación) - SUM(monto_devolución)) AS total_operación_neto FROM devolucion_mes) AS subconsulta) 
			* 100,2)  AS contribución_total_operación_neto
FROM españa_funcionalidad
GROUP BY nombre_comercio
ORDER BY contribución_total_operación_neto DESC
;

-- Recuento de los distintos comercios en España
Select count(distinct nombre_comercio) FROM españa_funcionalidad;