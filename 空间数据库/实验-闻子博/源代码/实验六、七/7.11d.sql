SELECT cntry_name
FROM sde.country
WHERE ST_YMax(shape) < 0;
