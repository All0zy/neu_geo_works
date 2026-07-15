SELECT R.name AS river_name, C.city_name, MIN(ST_Distance(R.shape, C.shape)) AS distance
FROM sde.river R
JOIN sde.city C ON ST_DWithin(R.shape, C.shape, (SELECT MAX(ST_Distance(R1.shape, C1.shape)) FROM sde.river R1, sde.city C1))
GROUP BY R.name, C.city_name;
