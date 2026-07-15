SELECT c.city_name, ST_Distance(c.shape, ST_SetSRID(ST_MakePoint(-77.0369, 38.9072), 4326)) AS distance
FROM sde.city AS c
WHERE ST_DWithin(c.shape, ST_SetSRID(ST_MakePoint(-77.0369, 38.9072), 4326), 80467);  -- 50英里转为米
