SELECT r.name AS river, c.cntry_name AS country, ST_Length(ST_Intersection(r.shape, c.shape)) AS length
FROM sde.river AS r
JOIN sde.country AS c ON ST_Intersects(r.shape, c.shape);
