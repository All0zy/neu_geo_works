SELECT c.city_name
FROM sde.city c, sde.river r
WHERE ST_Intersects(c.shape, ST_Buffer(r.shape, 300)) = true
AND r.name = 'Saint Louis';
