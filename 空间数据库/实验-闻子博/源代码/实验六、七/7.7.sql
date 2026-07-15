SELECT co.cntry_name, c.city_name, ST_Distance(ST_SetSRID(ST_MakePoint(0, ST_Y(c.shape)), 4326), c.shape) AS distance
FROM sde.country AS co
JOIN sde.city AS c ON co.cntry_name = c.cntry_name
WHERE c.status = 'Y';
