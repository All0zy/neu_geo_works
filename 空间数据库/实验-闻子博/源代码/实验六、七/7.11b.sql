SELECT r.name AS river_name, SUM(ST_Length(ST_Intersection(r.shape, c.shape))) AS length
FROM sde.river AS r
JOIN sde.country AS c ON ST_Intersects(r.shape, c.shape)
WHERE r.name = 'Rio Paranas' AND (c.cntry_name = 'Argentina' OR c.cntry_name = 'Brazil')
GROUP BY r.name;
