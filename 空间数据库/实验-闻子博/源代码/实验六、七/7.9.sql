SELECT c1.cntry_name, COUNT(c2.cntry_name) AS neighbor_count
FROM sde.country AS c1
JOIN sde.country AS c2 ON ST_Touches(c1.shape, c2.shape)
GROUP BY c1.cntry_name
ORDER BY neighbor_count DESC
LIMIT 1;
